from datetime import datetime, timedelta, time, date

from flask import render_template, redirect, request, flash, session
from flask_login import login_required, current_user

from app import app, db, admin_required
from app.forms import SingleTripForm, IntervalTripForm
from app.models import Tour, Trip, Interval, Crew


@app.route('/manage_trips/<tour_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_trips(tour_id):
    session['prev_url'] = request.referrer
    tour = Tour.query.filter_by(id=tour_id).first_or_404()
    intervals = tour.intervals.all()
    single_trips = tour.trips.all()
    add_single_trip_form = SingleTripForm()
    add_single_trip_form.submit.label.text = "+"
    add_interval_trip_form = IntervalTripForm()
    add_interval_trip_form.submit.label.text = "+"
    if add_interval_trip_form.validate_on_submit():
        start_date = add_interval_trip_form.start_date.data
        if start_date <= date.today():
            flash('Startzeitpunkt eines Intervalls darf nicht in der Vergangenheit liegen.')
            return redirect('/manage_trips/' + tour_id)
        end_date = start_date + timedelta(weeks=4)
        start_time = add_interval_trip_form.start_time.data
        end_time = add_interval_trip_form.end_time.data
        time_delta = timedelta(minutes=add_interval_trip_form.interval.data)
        iv = Interval()
        iv.start_date = start_date
        iv.tour_id = tour_id
        iv.start_time = start_time
        iv.end_time = end_time
        iv.interval_minutes = add_interval_trip_form.interval.data
        # iv only gets assigned an id after commit
        db.session.add(iv)
        db.session.commit()
        while start_date < end_date:
            while start_time < end_time:
                t = Trip()
                t.date = start_date
                t.time = start_time
                t.interval_id = iv.id
                db.session.add(t)
                # Converting datetime.time to datetime.datetime and back
                # because time doesn't support addition, datetime does
                dummy_time = datetime(2021, 1, 1, hour=start_time.hour, minute=start_time.minute)
                dummy_time = time_delta + dummy_time
                start_time = time(hour=dummy_time.hour, minute=dummy_time.minute)
            start_date = start_date + timedelta(days=1)
            start_time = add_interval_trip_form.start_time.data
        db.session.commit()
        return redirect('/manage_trips/' + tour_id)
    if add_single_trip_form.validate_on_submit():
        trip = Trip(date=add_single_trip_form.date.data,
                    time=add_single_trip_form.time.data,
                    crew_id=add_single_trip_form.assigned_crew.data,
                    tour_id=tour_id)
        db.session.add(trip)
        db.session.commit()
        return redirect('/manage_trips/'+tour_id)
    return render_template('trip/manage_trips.html',
                           tour=tour,
                           intervals=intervals,
                           single_trips=single_trips,
                           add_single_trip_form=add_single_trip_form,
                           add_interval_trip_form=add_interval_trip_form)


@app.route('/edit_trip/<trip_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_trip(trip_id):
    trip = Trip.query.filter_by(id=trip_id).first_or_404()
    form = SingleTripForm()
    form.submit.label.text = 'Durchführung speichern'
    if request.method == 'GET':
        session['prev_url'] = request.referrer
        form.date.data = trip.date
        form.time.data = trip.time
        form.assigned_crew.data = trip.crew_id
    if form.validate_on_submit():
        trip.date = form.date.data
        trip.time = form.time.data
        trip.crew_id = form.assigned_crew.data
        db.session.commit()
        return redirect(session['prev_url'])
    return render_template('trip/edit_trip.html', form=form, trip=trip)


@app.route('/manage_trips/<trip_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_trip(trip_id):
    trip = Trip.query.filter_by(id=trip_id).first()
    if trip is not None:
        db.session.delete(trip)
        db.session.commit()
        return redirect('/manage_trips/' + str(trip.tour_id)), 200
    return redirect('/manage_tours'), 500


@app.route('/my_trips')
@login_required
def my_trips():
    users_crew = Crew.query.filter_by(id=current_user.crew_id).first_or_404()
    return render_template('trip/my_trips.html', crew=users_crew)
