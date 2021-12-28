from datetime import datetime

from flask import render_template, flash, redirect, url_for, request, session
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import desc, asc

# TODO figure out why importing admin_required wont work
from app import app, db, admin_required
from app.forms import LoginForm, RushhourForm
from app.models import *


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
    return render_template('general/home.html', recent_activity=Activity.query.order_by(desc(Activity.time)).all())


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
    return render_template('general/login.html', title='Einloggen', form=form)


@app.route('/logout')
def logout():
    append_activity(f'Mitarbeiter {current_user.first_name} {current_user.last_name} hat sich ausgeloggt.')
    logout_user()
    return redirect(url_for('login'))


@app.route('/system_settings', methods=['GET', 'POST'])
@login_required
@admin_required
def system_settings():
    sys = System.query.get(1)
    rushhours = sys.rushhours
    rushhour_form = RushhourForm()
    rushhour_form.submit.label.text = '+'
    if rushhour_form.validate_on_submit():
        r = Rushhour()
        start_time_date = datetime(year=2021,
                                   month=1,
                                   day=1,
                                   hour=rushhour_form.start_time.data.hour,
                                   minute=rushhour_form.start_time.data.minute)
        end_time_date = datetime(year=2021,
                                 month=1,
                                 day=1,
                                 hour=rushhour_form.end_time.data.hour,
                                 minute=rushhour_form.end_time.data.minute)
        r.start_time = start_time_date
        r.end_time = end_time_date
        r.system_id = 1
        db.session.add(r)
        db.session.commit()
        redirect(url_for('system_settings'))
    return render_template('general/system_settings.html', sys=sys, rushhours=rushhours, rushhour_form=rushhour_form)


@app.route('/edit_rushhour/<rushhour_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_rushhour(rushhour_id):
    form = RushhourForm()
    form.submit.label.text = 'Stoßzeit speichern'
    rushhour = Rushhour.query.filter_by(id=rushhour_id).first_or_404()
    if request.method == 'GET':
        session['prev_url'] = request.referrer
        form.start_time.data = rushhour.start_time
        form.end_time.data = rushhour.end_time
    if form.validate_on_submit():
        start_time_date = datetime(year=2021,
                                   month=1,
                                   day=1,
                                   hour=form.start_time.data.hour,
                                   minute=form.start_time.data.minute)
        end_time_date = datetime(year=2021,
                                 month=1,
                                 day=1,
                                 hour=form.end_time.data.hour,
                                 minute=form.end_time.data.minute)
        rushhour.start_time = start_time_date
        rushhour.end_time = end_time_date
        db.session.commit()
        return redirect(session['prev_url'])
    return render_template('general/edit_rushhour.html', form=form)


@app.route('/delete_rushhour/<rushhour_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_rushhour(rushhour_id):
    to_be_deleted = Rushhour.query.filter_by(id=rushhour_id).first()
    if to_be_deleted is not None:
        db.session.delete(to_be_deleted)
        db.session.commit()
        start = to_be_deleted.start_time.strftime('%H:%M')
        end = to_be_deleted.end_time.strftime('%H:%M')
        append_activity(f'Stoßzeit {to_be_deleted.id} (Beginn: {start}, Ende: {end}) wurde gelöscht.')
        return redirect(url_for('system_settings')), 200
    else:
        return redirect(url_for('system_settings')), 500


@app.route('/update_timetable')
@login_required
@admin_required
def update_timetable_route():
    update_timetable()
    return redirect(url_for('system_settings'))
