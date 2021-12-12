from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegisterNewUserForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Employee, Activity
from sqlalchemy import desc, asc
from werkzeug.urls import url_parse
from datetime import datetime


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
    return render_template('home.html', recent_activity=Activity.query.order_by(desc(Activity.time)).all())


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
    return render_template('login.html', title='Einloggen', form=form)


@app.route('/logout')
def logout():
    append_activity(f'Mitarbeiter {current_user.first_name} {current_user.last_name} hat sich ausgeloggt.')
    logout_user()
    return redirect(url_for('login'))


@app.route('/register_new_user', methods=['GET', 'POST'])
def register_new_user():
    if current_user.employee_type != 'admin':
        redirect(url_for('home'))
    form = RegisterNewUserForm()
    if form.validate_on_submit():
        e = Employee(id=form.id.data,
                     ssn=form.ssn.data,
                     first_name=form.first_name.data,
                     last_name=form.last_name.data,
                     employee_type=form.employee_type.data,
                     crew_id=form.crew_id.data
                     )
        e.set_password(form.password.data)
        db.session.add(e)
        db.session.commit()
        append_activity(f'Mitarbeiter {e.first_name} {e.last_name} hinzugefügt.')
        flash('Benutzer erfolgreich hinzugefügt.')
        return redirect(url_for('home'))
    return render_template('register_new_user.html', form=form)


@app.route('/manage_users', methods=['GET'])
def manage_users():
    if current_user.employee_type != 'admin':
        redirect(url_for('home'))
    employees = Employee.query.order_by(Employee.id.asc())
    return render_template('manage_users.html', employees=employees)


@app.route('/manage_users/<id>', methods=['DELETE'])
def delete_user(id):
    if current_user.employee_type != 'admin':
        redirect(url_for('home'))
    to_be_deleted = Employee.query.filter_by(id=id).first()
    if to_be_deleted is not None and to_be_deleted != current_user:
        append_activity(f'Mitarbeiter {to_be_deleted.first_name} {to_be_deleted.last_name} wurde gelöscht.')
        db.session.delete(to_be_deleted)
        db.session.commit()
        return render_template('manage_users.html'), 200
    else:
        return render_template('manage_users.html'), 500


# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         user = User(username=form.username.data, email=form.email.data)
#         user.set_password(form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         flash('Congratulations, you are now a registered user!')
#         return redirect(url_for('login'))
#     return render_template('register.html', title='Register', form=form)


@app.route('/employee/<id>')
@login_required
def user(id):
    employee = Employee.query.filter_by(id=id).first_or_404()
    return render_template('employee.html', employee=employee)

# @app.route('/edit_profile', methods=['GET', 'POST'])
# @login_required
# def edit_profile():
#     form = EditProfileForm(current_user.username)
#     if form.validate_on_submit():
#         current_user.username = form.username.data
#         current_user.about_me = form.about_me.data
#         db.session.commit()
#         flash('Your changes have been saved.')
#         return redirect(url_for('edit_profile'))
#     elif request.method == 'GET':
#         form.username.data = current_user.username
#         form.about_me.data = current_user.about_me
#     return render_template('edit_profile.html', title='Edit Profile',
#                            form=form)
