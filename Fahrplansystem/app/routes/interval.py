from flask import render_template, redirect, session
from flask_login import login_required

from app import app, db, admin_required
from app.models.models import Interval
from app.functions import append_activity


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
    tour_id = iv.tour_id
    trip_count = len(iv.trips.all())
    if iv is not None:
        db.session.delete(iv)
        db.session.commit()
        append_activity(f'Intervall der Fahrt {tour_id} gelöscht ({trip_count} Durchführungen)')
        return redirect(session['prev_url']), 200
    else:
        return redirect(session['prev_url']), 500
