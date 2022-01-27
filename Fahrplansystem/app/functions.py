import json

import requests
from datetime import datetime, date, timedelta, time

from flask import url_for
from sqlalchemy import asc

from app import System, db
from app.models.models import Tour, RouteWarning, TrainWarning, Activity, Trip


# returns true if there is a warning for a given tour at a certain datetime
def warnings_found(tour, dt):
    warnings_count = RouteWarning.query.filter(RouteWarning.route_start == tour.start,
                                               RouteWarning.route_end == tour.end,
                                               RouteWarning.start < dt,
                                               RouteWarning.end > dt).count()
    warnings_count += TrainWarning.query.filter(TrainWarning.train_nr == tour.train,
                                                TrainWarning.start < dt,
                                                TrainWarning.end > dt).count()
    return warnings_count > 0


# goes through all trips, tours and intervals and checks if new trips need to be added
# old ones deleted or deleted because of a new warning in either the routes API or trains API
def update_timetable():
    days_to_keep_old_trips = System.query.get(1).days_to_keep_old_trips
    delete_if_before = date.today() - timedelta(days=days_to_keep_old_trips)
    tours = Tour.query.all()
    deleted_count = 0
    added_count = 0
    for tour in tours:
        for interval in tour.intervals:
            for trip in interval.trips:
                if trip.start_datetime.date() < delete_if_before \
                        or warnings_found(interval.tour, trip.start_datetime):
                    db.session.delete(trip)
                    deleted_count += 1
            start_date = interval.start_date
            # interval.start_date is irrelevant if the interval is already
            # in action. date.today() makes sure intervals are always up to date for
            # the next 4 weeks
            if start_date < date.today():
                start_date = date.today()
            end_date = timedelta(weeks=4) + start_date
            # reduce the 4 weeks update-timespan if the interval does have an end_date
            if interval.end_date is not None and interval.end_date < end_date:
                end_date = interval.end_date
            start_time = interval.start_time
            end_time = interval.end_time
            weekdays = get_weekdays(interval)
            iv_minutes_delta = timedelta(minutes=interval.interval_minutes)
            while start_date < end_date:
                while start_time < end_time:
                    dt = datetime.combine(start_date, start_time)
                    # if no trip can be found on the datetime where one should be
                    # a new trip gets added. The weekday of the datetime needs to be
                    # in this intervals weekdays and there can be no warnings for this
                    # route and datetime.
                    trip = Trip.query.filter(Trip.start_datetime == dt,
                                             Trip.interval_id == interval.id).first()
                    if trip is None and start_date.weekday() in weekdays \
                            and not warnings_found(interval.tour, dt):
                        trip = Trip()
                        trip.start_datetime = dt
                        trip.interval_id = interval.id
                        db.session.add(trip)
                        added_count += 1
                    # Converting datetime.time to datetime.datetime and back
                    # because time doesn't support addition, datetime does
                    dummy_time = datetime(2021, 1, 1, hour=start_time.hour, minute=start_time.minute)
                    dummy_time = iv_minutes_delta + dummy_time
                    start_time = time(hour=dummy_time.hour, minute=dummy_time.minute)
                start_date = start_date + timedelta(days=1)
                start_time = interval.start_time
        # go through all single-trips of a tour and check if some need
        # to be deleted
        for trip in tour.trips:
            if trip.start_datetime.date() < delete_if_before \
                    or warnings_found(trip.tour, trip.start_datetime):
                db.session.delete(trip)
                deleted_count += 1
    sys = System.query.get(1)
    sys.last_system_check = datetime.today()
    db.session.commit()
    return added_count, deleted_count


# Activities appear on the admin homepage
def append_activity(message):
    new_activity = Activity()
    new_activity.msg = message
    if Activity.query.count() > 9:
        oldest_activity = Activity.query.order_by(asc(Activity.time)).first()
        db.session.delete(oldest_activity)
    db.session.add(new_activity)
    db.session.commit()


# see stored weekdays format below
def get_weekdays(interval):
    wd = interval.weekdays.split(':')
    wd.pop()
    wd = [int(x) for x in wd]
    return wd


# Specified weekdays of an interval get saved in a string formatted like:
# '4:5:6:', which would indicate that this interval is only active on friday, saturday and sunday.
def add_weekdays(iv, iv_form):
    weekdays = ''
    if iv_form.monday.data:
        weekdays += '0:'
    if iv_form.tuesday.data:
        weekdays += '1:'
    if iv_form.wednesday.data:
        weekdays += '2:'
    if iv_form.thursday.data:
        weekdays += '3:'
    if iv_form.friday.data:
        weekdays += '4:'
    if iv_form.saturday.data:
        weekdays += '5:'
    if iv_form.sunday.data:
        weekdays += '6:'
    iv.weekdays = weekdays


# displays the current route choices in the given form
def get_route_choices(form):
    routes_json = json.loads(requests.get(url_for('get_routes', _external=True), verify=False).text)
    routes_choices = []
    for route in routes_json['routes']:
        value = route.get('start') + '-' + route.get('end')
        label = route.get('start') + '-' + route.get('end') + ', Spurweite: ' + str(route.get('track_width')) + 'mm'
        routes_choices.append((value, label))
    form.route_choice.choices = routes_choices


# displays the current train choices in the given form
def get_train_choices(form):
    trains_json = requests.get('http://127.0.0.1:5001/api/Züge').json()
    train_choices = []
    for train in trains_json['items']:
        train_width = get_train_width(train.get('triebwagen_nr'))
        label = train.get('name') + ' ' + train.get('nr') + ', Spurweite: ' + str(train_width) + 'mm'
        if Tour.query.filter(Tour.train == train.get('nr')).first() is None:
            train_choices.append((train.get('nr'), label))
    form.train_choice.choices = train_choices


# checks if a given trip lies in the timeframe of a rushhour
def is_in_rushhour(trip):
    tour = trip.tour if trip.tour is not None else trip.interval.tour
    for rushhour in tour.rushhours:
        if rushhour.start_time.time() < trip.start_datetime.time() < rushhour.end_time.time():
            return True
    return False


def get_rushhour_multiplicator(trip):
    tour = trip.tour if trip.tour is not None else trip.interval.tour
    return tour.rushHourMultiplicator


# given a start and end section within a route return the start and end points
# of the whole route (needed because only start and endpoint of the whole route get
# saved in the system, not the sections)
def get_correct_route(routes, start, destination):
    correct_route_start = ''
    correct_route_end = ''
    for route in routes:
        start_point_found = False
        end_point_found = False
        current_route_start = route['start']
        current_route_end = route['end']
        for section in route['sections']:
            if section['from'] == start:
                start_point_found = True
            if section['to'] == destination:
                end_point_found = True
        if start_point_found and end_point_found:
            correct_route_start = current_route_start
            correct_route_end = current_route_end
            break
    return correct_route_start, correct_route_end


# calculate how long it takes for a train to reach the given section, how long
# the travel time between the start section and destination section is and the distance
# between those two
def get_info(routes, correct_route_start, correct_route_end, start, destination):
    minutes_to_start = 0
    travel_time = 0
    distance_between_start_and_destination = 0
    between_start_and_destination = False
    # go through the dict again and calculate the needed values for the found route/sections
    for route in routes:
        if route['start'] != correct_route_start and route['end'] != correct_route_end:
            continue
        for section in route['sections']:
            if section['from'] == start:
                between_start_and_destination = True
            if between_start_and_destination:
                travel_time += section['travel_time']
                distance_between_start_and_destination += section['distance']
            else:
                minutes_to_start += section['travel_time']
            if section['to'] == destination:
                break
    return minutes_to_start, travel_time, distance_between_start_and_destination


# used when adding a new tour, mismatch between track width and train width can't be allowed
def train_width_matches_track_width(tour):
    # get route track width
    routes_json = json.loads(requests.get(url_for('get_routes', _external=True), verify=False).text)
    route_track_width = 0
    for route in routes_json['routes']:
        if tour.start == route['start'] and tour.end == route['end']:
            route_track_width = route['track_width']
            break

    # get train width
    trains_json = requests.get('http://127.0.0.1:5001/api/Züge').json()
    railcar_nr = ''
    for train in trains_json['items']:
        if tour.train == train['nr']:
            railcar_nr = train['triebwagen_nr']
            break
    return get_train_width(railcar_nr) == route_track_width


# get a train width from train API given a railcar number
def get_train_width(railcar_nr):
    train_width = 0
    railcar_json = requests.get('http://127.0.0.1:5001/api/Triebwaggons').json()
    for railcar in railcar_json['items']:
        if railcar_nr == railcar['nr']:
            train_width = railcar['spurweite']
            break
    return train_width
