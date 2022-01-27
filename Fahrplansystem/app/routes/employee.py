from flask import flash, url_for, render_template, request
from flask_login import login_required, current_user
from werkzeug.utils import redirect

from app import app, db, admin_required
from app.forms import EmployeeForm
from app.models.models import Employee, Crew
from app.functions import append_activity


@app.route('/add_employee', methods=['GET', 'POST'])
@login_required
@admin_required
def add_employee():
    form = EmployeeForm()
    if form.validate_on_submit():
        e = Employee()
        e.ssn = form.ssn.data
        e.first_name = form.first_name.data
        e.last_name = form.last_name.data
        e.employee_type = form.employee_type.data
        e.crew_id = form.crew_id.data
        e.set_password(form.password.data)
        enteredCrew = Crew.query.filter_by(id=form.crew_id.data).first()
        if enteredCrew is None and form.crew_id.data != "":
            crew = Crew(id=form.crew_id.data)
            db.session.add(crew)
        db.session.add(e)
        db.session.commit()
        append_activity(f'Mitarbeiter {e.first_name} {e.last_name} hinzugefügt.')
        flash('Benutzer erfolgreich hinzugefügt.')
        return redirect(url_for('home'))
    return render_template('employee/add_employee.html', form=form)


@app.route('/manage_employees', methods=['GET'])
@login_required
@admin_required
def manage_employees():
    employees = Employee.query.order_by(Employee.id.asc())
    return render_template('employee/manage_employees.html', employees=employees)


@app.route('/manage_employees/<id>', methods=['DELETE'])
@login_required
@admin_required
def delete_employee(id):
    to_be_deleted = Employee.query.filter_by(id=id).first()
    if to_be_deleted is not None and to_be_deleted != current_user:
        db.session.delete(to_be_deleted)
        db.session.commit()
        append_activity(f'Mitarbeiter {to_be_deleted.first_name} {to_be_deleted.last_name} wurde gelöscht.')
        return render_template('employee/manage_employees.html'), 200
    else:
        return render_template('employee/manage_employees.html'), 500


@app.route('/edit_employee/<id>', methods=['GET', 'POST'])
@login_required
@admin_required
def employee(id):
    emp = Employee.query.filter_by(id=id).first_or_404()
    form = EmployeeForm()
    form.submit.label.text = 'Benutzer speichern'
    if request.method == 'GET':
        form.ssn.data = emp.ssn
        form.first_name.data = emp.first_name
        form.last_name.data = emp.last_name
        form.employee_type.data = emp.employee_type
        form.crew_id.data = emp.crew_id
    if form.validate_on_submit():
        emp.ssn = form.ssn.data
        emp.first_name = form.first_name.data
        emp.last_name = form.last_name.data
        emp.employee_type = form.employee_type.data
        emp.crew_id = form.crew_id.data
        if form.password.data != '' and form.password2.data != '':
            emp.set_password(form.password.data)
        db.session.commit()
        flash('Mitarbeiter aktualisiert.')
        return redirect(url_for('manage_employees'))
    return render_template('employee/edit_employee.html', form=form)
