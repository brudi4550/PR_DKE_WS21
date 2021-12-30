import json

import requests
from flask import url_for, jsonify, make_response

from app import app


def get_route_choices(form):
    routes_json = json.loads(requests.get(url_for('get_routes', _external=True)).text)
    routes_choices = []
    for route in routes_json['routes']:
        value_and_label = route.get('start') + '-' + route.get('ende')
        routes_choices.append((value_and_label, value_and_label))
    form.route_choice.choices = routes_choices


def get_train_choices(form):
    trains_json = json.loads(requests.get(url_for('get_trains', _external=True)).text)
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
                "start": "Salzburg",
                "ende": "Innsbruck"
            }
        ]
    }
    return make_response(jsonify(routes))


@app.route('/get_trains')
def get_trains():
    trains = {
        "trains": [{
            "model": "ICE",
            "modelNr": "391"
        },
            {
                "model": "REX",
                "modelNr": "981"
            }
        ]
    }
    return make_response(jsonify(trains))