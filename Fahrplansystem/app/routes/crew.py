from flask import render_template, redirect, url_for
from flask_login import current_user, login_required

from app import app, admin_required, db, append_activity
from app.models import Crew


@app.route('/manage_crews', methods=['GET'])
@login_required
@admin_required
def manage_crews():
    crews = Crew.query.order_by(Crew.id.asc())
    return render_template('crew/manage_crews.html', crews=crews)


@app.route('/add_empty_crew', methods=['POST'])
@login_required
@admin_required
def add_empty_crew():
    c = Crew()
    db.session.add(c)
    db.session.commit()
    append_activity(f'Bordpersonalteam {c.id} wurde hinzugefügt.')
    return redirect(url_for('manage_crews'))


@app.route('/manage_crews/<id>', methods=['DELETE'])
@login_required
@admin_required
def delete_crew(id):
    to_be_deleted = Crew.query.filter_by(id=id).first()
    if to_be_deleted is not None:
        db.session.delete(to_be_deleted)
        db.session.commit()
        append_activity(f'Bordpersonalteam {to_be_deleted.id} wurde gelöscht.')
        return render_template('tour/manage_tours.html'), 200
    else:
        return render_template('tour/manage_tours.html'), 500
