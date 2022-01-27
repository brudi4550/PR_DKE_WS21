from datetime import timedelta, datetime

import dateutil.parser
import json

import requests
from flask import url_for, jsonify, make_response, request, Response, render_template

from app import app, db
from app.functions import update_timetable, is_in_rushhour, get_rushhour_multiplicator, get_correct_route, \
    get_info
from app.models.models import Employee, RouteWarning, TrainWarning, Trip, Tour
from app.functions import append_activity


# display route information for a given tour
@app.route('/route/<tour_id>')
def route(tour_id):
    tour = Tour.query.filter_by(id=tour_id).first()
    routes_json = json.loads(requests.get(url_for('get_routes', _external=True), verify=False).text)
    sections = []
    for curr_route in routes_json['routes']:
        if curr_route['start'] == tour.start and curr_route['end'] == tour.end:
            for section in curr_route['sections']:
                sections.append(section)
    return render_template('api/route.html', tour=tour, sections=sections)


# display train information for a given tour
@app.route('/train/<train_nr>')
def train(train_nr):
    trains_json = requests.get('http://127.0.0.1:5001/api/Züge').json()
    curr_train = None
    for curr_train in trains_json['items']:
        if curr_train['nr'] == train_nr:
            break
    warnings = []
    warnings_json = requests.get('http://127.0.0.1:5001/api/Wartungen').json()
    for warning in warnings_json['items']:
        if warning.get('zugNr') == curr_train['nr']:
            warnings.append(warning)
    return render_template('api/train.html', train=curr_train, warnings=warnings)


# remotely update route warnings with Basic HTTP Auth
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
            for curr_route in routes_json['routes']:
                current_route_start = curr_route['start']
                current_route_end = curr_route['end']
                for section in curr_route['sections']:
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
                            RouteWarning.msg == w.msg
                        ).first()
                        if alreadyExistingWarning is None:
                            db.session.add(w)
                            db.session.commit()
                            current_api_warning_ids.append(w.id)
                            added_count += 1
                        else:
                            current_api_warning_ids.append(alreadyExistingWarning.id)
            to_be_deleted = RouteWarning.query.filter(RouteWarning.id.not_in(current_api_warning_ids)).all()
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


# remotely update train warnings with Basic HTTP Auth
@app.route('/update_train_warnings', methods=['PATCH'])
def update_train_warnings():
    request_id = request.authorization.username
    password = request.authorization.password
    employee = Employee.query.filter_by(id=request_id).first()
    if employee is not None:
        if employee.check_password(password):
            added_count = 0
            deleted_count = 0
            trains_json = requests.get('http://127.0.0.1:5001/api/Wartungen').json()
            current_api_warning_ids = []
            for warning in trains_json['items']:
                tw = TrainWarning()
                tw.start = dateutil.parser.parse(warning['von'])
                tw.end = dateutil.parser.parse(warning['bis'])
                tw.train_nr = warning['zugNr']
                tw.system_id = 1
                tw.msg = 'Wartung'
                alreadyExistingWarning = TrainWarning.query.filter(
                    TrainWarning.train_nr == tw.train_nr,
                    TrainWarning.start == tw.start,
                    TrainWarning.end == tw.end
                ).first()
                if alreadyExistingWarning is None:
                    db.session.add(tw)
                    db.session.commit()
                    current_api_warning_ids.append(tw.id)
                    added_count += 1
                else:
                    current_api_warning_ids.append(alreadyExistingWarning.id)
            to_be_deleted = TrainWarning.query.filter(TrainWarning.id.not_in(current_api_warning_ids)).all()
            for warning in to_be_deleted:
                deleted_count += 1
                db.session.delete(warning)
                db.session.commit()
            if added_count > 0 or deleted_count > 0:
                update_timetable_added, update_timetable_deleted = update_timetable()
                append_activity(f'Fahrplanüberprüfung aufgrund von Änderungen in den Flotten-API. (Hinzugefügte'
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
    minutes_to_start, travel_time, distance_between_start_and_end = get_info(routes_json['routes'],
                                                                             correct_route_start,
                                                                             correct_route_end,
                                                                             start_section,
                                                                             end_section)
    latest_departure_time = departure - timedelta(minutes=minutes_to_start)
    tour = Tour.query.filter(Tour.start == correct_route_start,
                             Tour.end == correct_route_end).first()
    trips = []
    if tour is not None:
        trips = tour.trips.filter(Trip.start_datetime < latest_departure_time,
                                  Trip.start_datetime > latest_departure_time - timedelta(days=1)).all()
        for interval in tour.intervals:
            trips += interval.trips.filter(Trip.start_datetime < latest_departure_time,
                                           Trip.start_datetime > latest_departure_time - timedelta(days=1)).all()
    price = distance_between_start_and_end * app.config['PRICE_PER_KM_EURO']
    trips_with_price = {'matching_trips': []}
    for trip in trips:
        departure_time = trip.start_datetime + timedelta(minutes=minutes_to_start)
        arrival_time = departure_time + timedelta(minutes=travel_time)
        if is_in_rushhour(trip):
            price *= get_rushhour_multiplicator(trip)
        trips_with_price['matching_trips'].append({
            'price': price,
            'from': start_section,
            'to': end_section,
            'route_start': tour.start,
            'route_end': tour.end,
            'departure_time': departure_time,
            'arrival_time': arrival_time
        })
    return jsonify(trips_with_price)


@app.route('/get_routes')
def get_routes():
    routes = {
        "routes": [{
            "start": "Linz",
            "end": "Wien",
            "track_width": 1435,
            "sections": [{
                "from": "Linz",
                "to": "StPoelten",
                "travel_time": 48,
                "distance": 120,
                "warnings": []
            }, {
                "from": "StPoelten",
                "to": "Wien",
                "travel_time": 27,
                "distance": 100,
                "warnings": []
            }]
        }, {
            "start": "Wien",
            "end": "Linz",
            "track_width": 1435,
            "sections": [{
                "from": "Wien",
                "to": "StPoelten",
                "travel_time": 27,
                "distance": 100,
                "warnings": [{
                    "warningMsg": "Wartungsarbeiten",
                    "from": "2022-01-17T10:13:51.674Z",
                    "to": "2022-01-29T20:00:00.674Z"
                }]
            }, {
                "from": "StPoelten",
                "to": "Linz",
                "travel_time": 48,
                "distance": 120,
                "warnings": []
            }]
        }, {
            "start": "Innsbruck",
            "end": "Graz",
            "track_width": 1000,
            "sections": [{
                "from": "Innsbruck",
                "to": "Saalfelden",
                "travel_time": 101,
                "distance": 130,
                "warnings": []
            }, {
                "from": "Saalfelden",
                "to": "Schladming",
                "travel_time": 68,
                "distance": 75,
                "warnings": []
            }, {
                "from": "Schladming",
                "to": "Selzthal",
                "travel_time": 55,
                "distance": 57,
                "warnings": []
            }, {
                "from": "Selzthal",
                "to": "Graz",
                "travel_time": 90,
                "distance": 113,
                "warnings": []
            }]
        }, {
            "start": "Graz",
            "end": "Innsbruck",
            "track_width": 1000,
            "sections": [{
                "from": "Graz",
                "to": "Selzthal",
                "travel_time": 90,
                "distance": 113,
                "warnings": []
            }, {
                "from": "Selzthal",
                "to": "Schladming",
                "travel_time": 55,
                "distance": 57,
                "warnings": []
            }, {
                "from": "Schladming",
                "to": "Saalfelden",
                "travel_time": 68,
                "distance": 75,
                "warnings": []
            }, {
                "from": "Saalfelden",
                "to": "Innsbruck",
                "travel_time": 101,
                "distance": 130,
                "warnings": []
            }]
        }]
    }
    return make_response(jsonify(routes))
