from flask import render_template, redirect, request, flash, session
from flask_login import login_required

from app import app, db, admin_required
from app.forms import SingleTripForm, IntervalTripForm
from app.models import Tour, Trip, Interval
from datetime import datetime, timedelta, time, date


@app.route('/edit_interval/<interval_id>')
@login_required
@admin_required
def edit_interval(interval_id):
    iv = Interval.query.filter_by(id=interval_id).first()
    trips = iv.trips.all()
    sorted_trips = sorted(trips, key=lambda trip: trip.start_datetime)
    return render_template('interval/edit_interval.html', trips=sorted_trips)


@app.route('/manage_interval/<interval_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_interval(interval_id):
    iv = Interval.query.filter_by(id=interval_id).first()
    if iv is not None:
        db.session.delete(iv)
        db.session.commit()
        return redirect(session['prev_url']), 200
    else:
        return redirect(session['prev_url']), 500
