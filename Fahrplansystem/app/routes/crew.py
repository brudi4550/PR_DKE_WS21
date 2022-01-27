from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user

from app import app, admin_required, db
from app.models.models import Crew, Employee
from app.functions import append_activity


@app.route('/manage_crews', methods=['GET'])
@login_required
@admin_required
def manage_crews():
    crews = Crew.query.order_by(Crew.id.asc())
    employees_in_no_crew = Employee.query \
        .filter(Employee.employee_type != 'admin') \
        .filter(Employee.crew_id == None) \
        .all()
    return render_template('crew/manage_crews.html', crews=crews, employees_in_no_crew=employees_in_no_crew)


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


@app.route('/move_employee_to_crew', methods=['POST'])
@login_required
@admin_required
def move_employee_to_crew():
    content = request.json
    employee = Employee.query.filter_by(id=content['employee_id']).first()
    employee.crew_id = content['crew_id']
    db.session.commit()
    return redirect(url_for('manage_crews'))


@app.route('/my_crew', methods=['GET'])
@login_required
def my_crew():
    users_crew = Crew.query.filter_by(id=current_user.crew_id).first_or_404()
    return render_template('crew/my_crew.html', crew=users_crew)
