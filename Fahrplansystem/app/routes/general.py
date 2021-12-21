from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import desc, asc

from app import app, db
from app.forms import LoginForm
from app.models import Activity, Employee


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
    return render_template('general/home.html', recent_activity=Activity.query.order_by(desc(Activity.time)).all())


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
    return render_template('general/login.html', title='Einloggen', form=form)


@app.route('/logout')
def logout():
    append_activity(f'Mitarbeiter {current_user.first_name} {current_user.last_name} hat sich ausgeloggt.')
    logout_user()
    return redirect(url_for('login'))
