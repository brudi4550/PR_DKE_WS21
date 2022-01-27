from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required

from app import app, db, admin_required
from app.forms import TourForm
from app.models.models import Tour
from app.functions import append_activity, get_route_choices, get_train_choices, train_width_matches_track_width


@app.route('/add_tour', methods=['GET', 'POST'])
@login_required
@admin_required
def add_tour():
    form = TourForm()
    form.submit.label.text = 'Fahrt hinzufügen'
    get_route_choices(form)
    get_train_choices(form)
    if form.validate_on_submit():
        tour = Tour()
        route = form.route_choice.data.split("-")
        tour.start = route[0]
        tour.end = route[1]
        tour.train = form.train_choice.data
        tour.rushHourMultiplicator = form.rush_hour_multiplicator.data
        if train_width_matches_track_width(tour):
            db.session.add(tour)
            db.session.commit()
            append_activity(f'Fahrt {tour.start} - {tour.end} hinzugefügt.')
            flash('Fahrt erfolgreich hinzugefügt')
        else:
            flash('Spurweiten der Fahrtstrecke und des ausgewählten Zuges stimmen nicht überein.')
    return render_template('tour/add_tour.html', form=form)


@app.route('/manage_tours', methods=['GET'])
@login_required
@admin_required
def manage_tours():
    tours = Tour.query.order_by(Tour.id.asc())
    return render_template('tour/manage_tours.html', tours=tours)


@app.route('/manage_tours/<id>', methods=['DELETE'])
@login_required
@admin_required
def delete_tour(id):
    to_be_deleted = Tour.query.filter_by(id=id).first()
    if to_be_deleted is not None:
        db.session.delete(to_be_deleted)
        db.session.commit()
        append_activity(f'Fahrt {to_be_deleted.start}-{to_be_deleted.end} wurde gelöscht.')
        return render_template('tour/manage_tours.html'), 200
    else:
        return render_template('tour/manage_tours.html'), 500


@app.route('/edit_tour/<id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_tour(id):
    tour = Tour.query.filter_by(id=id).first()
    form = TourForm()
    form.submit.label.text = 'Fahrt speichern'
    get_route_choices(form)
    get_train_choices(form)
    if request.method == 'GET':
        form.route_choice.data = tour.start + "-" + tour.end
        form.train_choice.data = tour.train
        form.rush_hour_multiplicator.data = tour.rushHourMultiplicator
    if form.validate_on_submit():
        route = form.route_choice.data.split("-")
        tour.start = route[0]
        tour.end = route[1]
        tour.train = form.train_choice.data
        tour.rushHourMultiplicator = form.rush_hour_multiplicator.data
        db.session.commit()
        flash('Fahrt aktualisiert.')
        return redirect(url_for('manage_tours'))
    return render_template('tour/edit_tour.html', form=form, tour=tour)
