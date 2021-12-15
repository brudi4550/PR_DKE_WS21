from flask_wtf import Form, FlaskForm
from wtforms import StringField, SubmitField, IntegerField, PasswordField, BooleanField, \
    SelectField, DecimalField, DateField, TimeField, RadioField
from wtforms.validators import DataRequired, Length
from wtforms.validators import ValidationError, Email, EqualTo
from app.models import Employee


class LoginForm(FlaskForm):
    employee_id = StringField('Mitarbeiter ID', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    remember_me = BooleanField('Login merken')
    submit = SubmitField('Einloggen')


class RegisterNewUserForm(FlaskForm):
    id = IntegerField('Mitarbeiter ID', validators=[DataRequired()])
    ssn = IntegerField('Sozialversicherungsnummer', validators=[DataRequired()])
    first_name = StringField('Vorname', validators=[DataRequired()])
    last_name = StringField('Nachname', validators=[DataRequired()])
    employee_type_choices = [
        ('admin', 'Administrator'),
        ('employee', 'Mitarbeiter'),
        ('ticket_inspector', 'Kontrolleur'),
        ('train_driver', 'Lokführer')
    ]
    employee_type = SelectField('Mitarbeiter-Funktion', choices=employee_type_choices, validators=[DataRequired()])
    crew_id = IntegerField('Bordpersonalteam', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    password2 = PasswordField('Passwort wiederholen', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Benutzer hinzufügen')

    def validate_id(self, id):
        employee = Employee.query.filter_by(id=id.data).first()
        if employee is not None:
            raise ValidationError('Mitarbeiter ID existiert bereits.')

    def validate_ssn(self, ssn):
        employee = Employee.query.filter_by(ssn=ssn.data).first()
        if employee is not None:
            raise ValidationError('Sozialversicherungsnummer muss eindeutig sein.')


class AddTourForm(FlaskForm):
    route_choice = SelectField('Strecke auswählen', validators=[DataRequired()])
    train_choice = SelectField('Zug auswählen', validators=[DataRequired()])
    date = DateField('Datum der ersten Durchführung', validators=[DataRequired()])
    time = TimeField('Zeitpunkt der ersten Durchführung', validators=[DataRequired()])
    rush_hour_multiplicator = DecimalField('Stoßzeit-Multiplikator', validators=[DataRequired()])
    assigned_crew = IntegerField('Bordpersonalteam zuteilen', validators=[DataRequired()])
    interval = IntegerField('Im Intervall von (Minuten):')
    intervalFrom = IntegerField('Von Uhrzeit:')
    intervalTo = IntegerField('Bis Uhrzeit:')
    submit = SubmitField('Fahrt zum System hinzufügen')
