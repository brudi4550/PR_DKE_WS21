from datetime import timedelta, datetime

import dateutil.parser
import json

import requests
from flask import url_for, jsonify, make_response, request, Response

from app import app, db
from app.models import Employee, RouteWarning, TrainWarning, update_timetable, Trip, Tour
from app.routes.general import append_activity


def get_route_choices(form):
    routes_json = json.loads(requests.get(url_for('get_routes', _external=True), verify=False).text)
    routes_choices = []
    for route in routes_json['routes']:
        value_and_label = route.get('start') + '-' + route.get('end')
        routes_choices.append((value_and_label, value_and_label))
    form.route_choice.choices = routes_choices


def get_train_choices(form):
    trains_json = json.loads(requests.get(url_for('get_trains', _external=True), verify=False).text)
    train_choices = []
    for train in trains_json['trains']:
        value_and_label = train.get('model') + ' ' + train.get('modelNr')
        train_choices.append((value_and_label, value_and_label))
    form.train_choice.choices = train_choices


@app.route('/update_route_warnings', methods=['PATCH'])
def update_route_warnings():
    request_id = request.authorization.username
    password = request.authorization.password
    employee = Employee.query.filter_by(id=request_id).first()
    if employee is not None:
        if employee.check_password(password):
            added_count = 0
            deleted_count = 0
            routes_json = json.loads(requests.get(url_for('get_routes', _external=True), verify=False).text)
            current_api_warning_ids = []
            for route in routes_json['routes']:
                current_route_start = route['start']
                current_route_end = route['end']
                for section in route['sections']:
                    for warning in section['warnings']:
                        w = RouteWarning()
                        w.route_start = current_route_start
                        w.route_end = current_route_end
                        w.msg = warning['warningMsg']
                        w.start = dateutil.parser.parse(warning['from'])
                        w.end = dateutil.parser.parse(warning['to'])
                        w.system_id = 1
                        alreadyExistingWarning = RouteWarning.query.filter(
                            RouteWarning.route_start == w.route_start,
                            RouteWarning.route_end == w.route_end,
                            RouteWarning.start == w.start,
                            RouteWarning.end == w.end
                        ).first()
                        if alreadyExistingWarning is None:
                            db.session.add(w)
                            db.session.commit()
                            current_api_warning_ids.append(w.id)
                            added_count += 1
                        else:
                            current_api_warning_ids.append(alreadyExistingWarning.id)
            to_be_deleted = RouteWarning.query.filter(RouteWarning.id.not_in(current_api_warning_ids))
            for warning in to_be_deleted:
                deleted_count += 1
                db.session.delete(warning)
                db.session.commit()
            if added_count > 0 or deleted_count > 0:
                update_timetable_added, update_timetable_deleted = update_timetable()
                append_activity(f'Fahrplanüberprüfung aufgrund von Änderungen in den Strecken-API. (Hinzugefügte'
                                f' Durchführungen {update_timetable_added}, Entfernte Durchführungen '
                                f'{update_timetable_deleted})')
            return Response(status=200)
    return Response(status=500)


@app.route('/search_trips')
def search_trips():
    params = request.args.to_dict()
    start_section = params['start']
    end_section = params['end']
    year = int(params['year'])
    month = int(params['month'])
    day = int(params['day'])
    hour = int(params['hour'])
    minute = int(params['minute'])
    departure = datetime(year=year, month=month, day=day, hour=hour, minute=minute)
    routes_json = json.loads(requests.get(url_for('get_routes', _external=True), verify=False).text)
    correct_route_start, correct_route_end = get_correct_route(routes_json['routes'], start_section, end_section)
    distance_to_start, distance_between_start_and_end = get_distances(routes_json['routes'],
                                                                      correct_route_start,
                                                                      correct_route_end,
                                                                      start_section,
                                                                      end_section)
    time_to_train_station = distance_to_start / app.config['AVG_TRAIN_SPEED_KMH']
    latest_departure_time = departure - timedelta(hours=time_to_train_station)
    # TODO fix, only checks non interval trips, check for rushhour and increase price
    tour = Tour.query.filter(Tour.start == correct_route_start,
                             Tour.end == correct_route_end).first()
    trips = Trip.query.filter(Trip.tour_id == tour.id,
                              Trip.start_datetime < latest_departure_time).all()
    price = distance_between_start_and_end * app.config['PRICE_PER_KM_EURO']
    trips_with_price = {'price': price, 'matching_trips': []}
    for trip in trips:
        trips_with_price['matching_trips'].append({
            'from': start_section,
            'to': end_section,
            'start_train_station': tour.start,
            'end_train_station': tour.end,
            'departure_from_start_train_station_at': trip.start_datetime
        })
    return jsonify(trips_with_price)


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


def get_distances(routes, correct_route_start, correct_route_end, start, destination):
    distance_to_start = 0
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
                distance_between_start_and_destination += section['distance']
            else:
                distance_to_start += section['distance']
            if section['to'] == destination:
                break
    return distance_to_start, distance_between_start_and_destination


@app.route('/get_routes')
def get_routes():
    routes = {
        "routes": [{
            "start": "Linz",
            "end": "Wien",
            "sections": [{
                "from": "Linz",
                "to": "StPoelten",
                "distance": 120,
                "warnings": []
            }, {
                "from": "StPoelten",
                "to": "Wien",
                "distance": 100,
                "warnings": []
            }]
        }, {
            "start": "Wien",
            "end": "Linz",
            "sections": [{
                "from": "Wien",
                "to": "StPoelten",
                "distance": 100,
                "warnings": [{
                    "warningMsg": "Wartungsarbeiten",
                    "from": "2022-01-17T10:13:51.674Z",
                    "to": "2022-01-17T16:13:51.674Z"
                }]
            }, {
                "from": "StPoelten",
                "to": "Linz",
                "distance": 120,
                "warnings": []
            }]
        }]
    }
    return make_response(jsonify(routes))


@app.route('/get_trains')
def get_trains():
    trains = {
        "trains": [{
            "model": "Railjet",
            "modelNr": "391"
        },
            {
                "model": "REX",
                "modelNr": "981"
            },
            {
                "model": "Eurocity",
                "modelNr": "114"
            },
            {
                "model": "Intercity",
                "modelNr": "289"
            },
            {
                "model": "Nightjet",
                "modelNr": "545"
            },
            {
                "model": "Cityjet",
                "modelNr": "831"
            },
            {
                "model": "Eurocity",
                "modelNr": "103"
            },
        ]
    }
    return make_response(jsonify(trains))
