from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required

from app import app, db, admin_required
from app.forms import TourForm, EditTourForm, AddTripForm
from app.models import Tour, Trip
from app.routes.api import get_route_choices, get_train_choices
from app.routes.general import append_activity


@app.route('/trips/<tour_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_trips(tour_id):
    tour = Tour.query.filter_by(id=tour_id).first_or_404()
    intervals = tour.intervals.all()
    single_trips = tour.trips.all()
    add_trip_form = AddTripForm()
    add_trip_form.submit.label.text = "+"
    if add_trip_form.validate_on_submit():
        trip = Trip(date=add_trip_form.date.data,
                    time=add_trip_form.time.data,
                    crew_id=add_trip_form.assigned_crew.data,
                    tour_id=tour_id)
        db.session.add(trip)
        db.session.commit()
        return redirect('/trips/'+tour_id)
    return render_template('trip/manage_trips.html',
                           intervals=intervals,
                           single_trips=single_trips,
                           add_trip_form=add_trip_form)


@app.route('/edit_trip/<trip_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_trip(trip_id):
    return render_template('trip/trip.html')
