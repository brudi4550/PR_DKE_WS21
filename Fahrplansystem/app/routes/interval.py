from flask import render_template, redirect, request, flash
from flask_login import login_required

from app import app, db, admin_required
from app.forms import SingleTripForm, IntervalTripForm
from app.models import Tour, Trip, Interval
from datetime import datetime, timedelta, time, date


@app.route('/edit_interval/<interval_id>')
@login_required
@admin_required
def interval(interval_id):
    iv = Interval.query.filter_by(id=interval_id).first()
    return render_template('interval/edit_interval.html', iv=iv)
