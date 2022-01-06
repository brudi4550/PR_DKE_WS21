from flask import render_template, flash, redirect, url_for, request, session, Response
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import desc, asc
from app import admin_required
from app.forms import LoginForm, AddRushhourForm, EditRushhourForm, SystemForm
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
    sorted_tours = sorted(Tour.query.all(), key=lambda t: (t.next_trip() is None, t.time_until_next_trip()))
    return render_template('general/home.html',
                           recent_activity=Activity.query.order_by(desc(Activity.time)).all(),
                           tours=sorted_tours)


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
    sys_form = SystemForm()
    if request.method == 'GET':
        sys_form.days_to_keep_old_trips.data = sys.days_to_keep_old_trips
    all_tours = Tour.query.all()
    rushhour_form = AddRushhourForm()
    rushhour_form.submit.label.text = '+'
    if sys_form.validate_on_submit():
        sys.days_to_keep_old_trips = sys_form.days_to_keep_old_trips.data
        db.session.commit()
        redirect(url_for('system_settings'))
    if rushhour_form.validate_on_submit():
        tour_ids = rushhour_form.tour_ids.data.split(",")
        tour_ids = [int(x) for x in tour_ids]
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
        for tour_id in tour_ids:
            tour = Tour.query.filter_by(id=tour_id).first()
            if tour is None:
                continue
            r = Rushhour()
            r.start_time = start_time_date
            r.end_time = end_time_date
            r.tour_id = tour.id
            db.session.add(r)
            db.session.commit()
        if len(tour_ids) > 1:
            append_activity(f'Stoßzeit zu den Fahrten {rushhour_form.tour_ids.data}'
                            f' (Beginn: {start_time_date.time()}, Ende: {end_time_date.time()}) hinzugefügt')
        else:
            append_activity(f'Stoßzeit zur Fahrt {tour_ids[0]} '
                            f'(Beginn: {start_time_date.time()}, Ende: {end_time_date.time()}) hinzugefügt')
        redirect(url_for('system_settings'))
    return render_template('general/system_settings.html', sys=sys, sys_form=sys_form,
                           all_tours=all_tours, rushhour_form=rushhour_form)


@app.route('/edit_rushhour/<rushhour_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_rushhour(rushhour_id):
    form = EditRushhourForm()
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


@app.route('/local_update_timetable', methods=['PATCH'])
@login_required
@admin_required
def update_timetable_route():
    added_count, deleted_count = update_timetable()
    added_count_d = 'Durchführung' if added_count == 0 else 'Durchführungen'
    deleted_count_d = 'Durchführung' if deleted_count == 0 else 'Durchführungen'
    append_activity(f'Manuelle Fahrplanüberprüfung: {added_count} {added_count_d} hinzugefügt')
    append_activity(f'Manuelle Fahrplanüberprüfung: {deleted_count} {deleted_count_d} entfernt')
    return Response(status=200)


@app.route('/remote_update_timetable', methods=['PATCH'])
def update_timetable_remotely():
    request_id = request.authorization.username
    password = request.authorization.password
    employee = Employee.query.filter_by(id=request_id).first()
    if employee is not None:
        if employee.check_password(password):
            # make update_timetable return a boolean indicating if successful or not
            added_count, deleted_count = update_timetable()
            added_count_d = 'Durchführung' if added_count == 0 else 'Durchführungen'
            deleted_count_d = 'Durchführung' if deleted_count == 0 else 'Durchführungen'
            append_activity(f'Automatische Fahrplanüberprüfung: {added_count} {added_count_d} hinzugefügt')
            append_activity(f'Automatische Fahrplanüberprüfung: {deleted_count} {deleted_count_d} entfernt')
            return render_template('general/update_timetable.html', successful=True, added_count=added_count,
                                   deleted_count=deleted_count), 200
    return render_template('general/update_timetable.html', successful=False), 500
