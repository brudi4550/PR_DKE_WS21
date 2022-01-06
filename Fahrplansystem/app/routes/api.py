import json

import requests
from flask import url_for, jsonify, make_response

from app import app


def get_route_choices(form):
    routes_json = json.loads(requests.get(url_for('get_routes', _external=True), verify=False).text)
    routes_choices = []
    for route in routes_json['routes']:
        value_and_label = route.get('start') + '-' + route.get('ende')
        routes_choices.append((value_and_label, value_and_label))
    form.route_choice.choices = routes_choices


def get_train_choices(form):
    trains_json = json.loads(requests.get(url_for('get_trains', _external=True), verify=False).text)
    train_choices = []
    for train in trains_json['trains']:
        value_and_label = train.get('model') + ' ' + train.get('modelNr')
        train_choices.append((value_and_label, value_and_label))
    form.train_choice.choices = train_choices


# TODO make api only accessible with API key?
@app.route('/get_routes')
def get_routes():
    routes = {
        "routes": [{
                "start": "Linz",
                "ende": "Wien"
            },
            {
                "start": "Wien",
                "ende": "Linz"
            },
            {
                "start": "Salzburg",
                "ende": "Innsbruck"
            },
            {
                "start": "Innsbruck",
                "ende": "Salzburg"
            },
            {
                "start": "Graz",
                "ende": "Wien"
            },
            {
                "start": "Wien",
                "ende": "Graz"
            },
            {
                "start": "Rom",
                "ende": "Wien"
            },
        ]
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
