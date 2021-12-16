from flask import render_template, flash, redirect, url_for, jsonify, make_response, request
from app import app, db
from app.forms import LoginForm, RegisterNewUserForm, AddTourForm, EditEmployeeForm, EditTourForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Activity, Employee, Tour, Trip, Interval, Crew
from sqlalchemy import desc, asc
import requests
import json


def append_activity(message):
    new_activity = Activity()
    new_activity.msg = message
    if Activity.query.count() > 9:
        oldest_activity = Activity.query.order_by(asc(Activity.time)).first()
        db.session.delete(oldest_activity)
    db.session.add(new_activity)
    db.session.commit()


@app.route('/home', methods=['GET'])
@login_required
def home():
    return render_template('home.html', recent_activity=Activity.query.order_by(desc(Activity.time)).all())


@app.route('/', methods=['GET'])
def default():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        employee = Employee.query.filter_by(id=form.employee_id.data).first()
        successful_login = True
        if employee is None:
            append_activity(f'Jemand hat versuchte sich mit der Mitarbeiter ID {form.employee_id.data} einzuloggen.')
            successful_login = False
        elif not employee.check_password(form.password.data):
            append_activity(f'Login für Mitarbeiter ID {form.employee_id.data} wegen falschem Passwort fehlgeschlagen.')
            successful_login = False
        if not successful_login:
            flash('Ungültige Mitarbeiter ID oder Passwort')
            return redirect(url_for('login'))
        append_activity(f'Mitarbeiter {employee.first_name} {employee.last_name} hat sich eingeloggt.')
        login_user(employee, remember=form.remember_me.data)
        return redirect(url_for('home'))
    return render_template('login.html', title='Einloggen', form=form)


@app.route('/logout')
def logout():
    append_activity(f'Mitarbeiter {current_user.first_name} {current_user.last_name} hat sich ausgeloggt.')
    logout_user()
    return redirect(url_for('login'))


@app.route('/register_new_user', methods=['GET', 'POST'])
@login_required
def register_new_user():
    if current_user.employee_type != 'admin':
        redirect(url_for('home'))
    form = RegisterNewUserForm()
    if form.validate_on_submit():
        e = Employee(id=form.id.data,
                     ssn=form.ssn.data,
                     first_name=form.first_name.data,
                     last_name=form.last_name.data,
                     employee_type=form.employee_type.data,
                     crew_id=form.crew_id.data
                     )
        e.set_password(form.password.data)
        enteredCrew = Crew.query.filter_by(id=form.crew_id.data).first()
        if enteredCrew is None and form.crew_id.data != "":
            crew = Crew(id=form.crew_id.data)
            db.session.add(crew)
        db.session.add(e)
        db.session.commit()
        append_activity(f'Mitarbeiter {e.first_name} {e.last_name} hinzugefügt.')
        flash('Benutzer erfolgreich hinzugefügt.')
        return redirect(url_for('home'))
    return render_template('register_new_user.html', form=form)


@app.route('/manage_users', methods=['GET'])
@login_required
def manage_users():
    if current_user.employee_type != 'admin':
        redirect(url_for('home'))
    employees = Employee.query.order_by(Employee.id.asc())
    return render_template('manage_users.html', employees=employees)


@app.route('/manage_users/<id>', methods=['DELETE'])
@login_required
def delete_user(id):
    if current_user.employee_type != 'admin':
        redirect(url_for('home'))
    to_be_deleted = Employee.query.filter_by(id=id).first()
    if to_be_deleted is not None and to_be_deleted != current_user:
        append_activity(f'Mitarbeiter {to_be_deleted.first_name} {to_be_deleted.last_name} wurde gelöscht.')
        db.session.delete(to_be_deleted)
        db.session.commit()
        return render_template('manage_users.html'), 200
    else:
        return render_template('manage_users.html'), 500


# TODO refactor this
@app.route('/employee/<id>', methods=['GET', 'POST'])
@login_required
def user(id):
    if current_user.employee_type != 'admin':
        redirect(url_for('home'))
    employee = Employee.query.filter_by(id=id).first_or_404()
    form = EditEmployeeForm()
    if request.method == 'GET':
        form.id.data = employee.id
        form.ssn.data = employee.ssn
        form.first_name.data = employee.first_name
        form.last_name.data = employee.last_name
        form.employee_type.data = employee.employee_type
    if form.validate_on_submit():
        employee.id = form.id.data
        employee.ssn = form.ssn.data
        employee.first_name = form.first_name.data
        employee.last_name = form.last_name.data
        employee.employee_type = form.employee_type.data
        if form.password.data != '' and form.password2.data != '':
            employee.set_password(form.password.data)
        db.session.commit()
        flash('Mitarbeiter aktualisiert.')
        return redirect(url_for('manage_users'))
    return render_template('employee.html', form=form)


@app.route('/manage_crews', methods=['GET'])
@login_required
def manage_crews():
    if current_user.employee_type != 'admin':
        redirect(url_for('home'))
    crews = Crew.query.order_by(Crew.id.asc())
    return render_template('manage_crews.html', crews=crews)


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


@app.route('/add_tour', methods=['GET', 'POST'])
@login_required
def add_tour():
    if current_user.employee_type != 'admin':
        redirect(url_for('home'))
    form = AddTourForm()
    get_route_choices(form)
    get_train_choices(form)
    if form.validate_on_submit():
        tour = Tour()
        route = form.route_choice.data.split("-")
        tour.start = route[0]
        tour.end = route[1]
        tour.rushHourMultiplicator = form.rush_hour_multiplicator.data
        # Tour gets assigned id only after persistence
        db.session.add(tour)
        db.session.commit()
        if request.form['options'] == 'onetime':
            trip = Trip()
            trip.tour_id = tour.id
            # TODO add crew if id doesnt exist
            trip.crew_id = form.assigned_crew.data
            trip.date = form.date.data
            trip.time = form.time.data
            db.session.add(trip)
        else:
            # TODO implement add according to intervall
            for i in range(5):
                trip = Trip()
                trip.tour_id = tour.id
                # TODO add crew if id doesnt exist
                trip.crew_id = form.assigned_crew.data
                trip.date = form.date.data
                trip.time = form.time.data
                db.session.add(trip)
        db.session.commit()
        flash('Fahrt erfolgreich hinzugefügt')
    return render_template('add_tour.html', form=form)


@app.route('/manage_tours')
@login_required
def manage_tours():
    if current_user.employee_type != 'admin':
        redirect(url_for('home'))
    tours = Tour.query.order_by(Tour.id.asc())
    return render_template('manage_tours.html', tours=tours)


@app.route('/manage_tours/<id>', methods=['DELETE'])
@login_required
def delete_tour(id):
    if current_user.employee_type != 'admin':
        redirect(url_for('home'))
    to_be_deleted = Tour.query.filter_by(id=id).first()
    if to_be_deleted is not None:
        db.session.delete(to_be_deleted)
        db.session.commit()
        append_activity(f'Tour {to_be_deleted.id} {to_be_deleted.start}-{to_be_deleted.end} wurde gelöscht.')
        return render_template('manage_users.html'), 200
    else:
        return render_template('manage_tours.html'), 500


# TODO implement edit tour
@app.route('/manage_tours/<id>', methods=['GET', 'POST'])
@login_required
def edit_tour(id):
    if current_user.employee_type != 'admin':
        redirect(url_for('home'))
    tour = Tour.query.filter_by(id=id).first()
    form = EditTourForm()
    get_route_choices(form)
    get_train_choices(form)
    if request.method == 'GET':
        pass
    if form.validate_on_submit():
        flash('Fahrt aktualisiert.')
        return redirect(url_for('manage_tours'))
    return render_template('tour.html', form=form, tour=tour)


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
