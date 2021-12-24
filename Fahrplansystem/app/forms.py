from flask_wtf import Form, FlaskForm
from wtforms import StringField, SubmitField, IntegerField, PasswordField, BooleanField, \
    SelectField, DecimalField, DateField, TimeField, RadioField
from wtforms.validators import DataRequired, Optional
from wtforms.validators import ValidationError, Email, EqualTo
from app.models import Employee


class LoginForm(FlaskForm):
    employee_id = StringField('Mitarbeiter ID', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    remember_me = BooleanField('Login merken')
    submit = SubmitField('Einloggen')


# TODO refactor registeruserform and edituserform
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
    crew_id = IntegerField('Bordpersonalteam', validators=[Optional()])
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


class EditEmployeeForm(FlaskForm):
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
    crew_id = IntegerField('Bordpersonalteam', validators=[Optional()])
    password = PasswordField('Passwort')
    password2 = PasswordField('Passwort wiederholen', validators=[EqualTo('password')])
    submit = SubmitField('Benutzer speichern')


class TourForm(FlaskForm):
    route_choice = SelectField('Strecke auswählen', validators=[DataRequired()])
    train_choice = SelectField('Zug auswählen', validators=[DataRequired()])
    rush_hour_multiplicator = DecimalField('Stoßzeit-Multiplikator', validators=[DataRequired()])
    # interval = IntegerField('Im Intervall von (Minuten):', default=0)
    # intervalFrom = IntegerField('Von Uhrzeit:', default=0)
    # intervalTo = IntegerField('Bis Uhrzeit:', default=0)
    submit = SubmitField()


class EditTourForm(FlaskForm):
    route_choice = SelectField('Strecke auswählen', validators=[DataRequired()])
    train_choice = SelectField('Zug auswählen', validators=[DataRequired()])
    date = DateField('Datum der ersten Durchführung', validators=[DataRequired()])
    time = TimeField('Zeitpunkt der ersten Durchführung', validators=[DataRequired()])
    rush_hour_multiplicator = DecimalField('Stoßzeit-Multiplikator', validators=[DataRequired()])
    assigned_crew = IntegerField('Bordpersonalteam zuteilen', validators=[DataRequired()])
    interval = IntegerField('Im Intervall von (Minuten):', default=0)
    intervalFrom = IntegerField('Von Uhrzeit:', default=0)
    intervalTo = IntegerField('Bis Uhrzeit:', default=0)
    submit = SubmitField('Fahrt zum System hinzufügen')


class SingleTripForm(FlaskForm):
    date = DateField('Datum der Durchführung', validators=[DataRequired()])
    time = TimeField('Zeitpunkt der Durchführung', validators=[DataRequired()])
    assigned_crew = IntegerField('Bordpersonalteam zuteilen', validators=[DataRequired()])
    submit = SubmitField('Einzelne Durchführung hinzufügen')


class IntervalTripForm(FlaskForm):
    start_date = DateField('Start des Intervalls', validators=[DataRequired()])
    start_time = TimeField('Zwischen', validators=[DataRequired()])
    end_time = TimeField('Und', validators=[DataRequired()])
    interval = IntegerField('Im Intervall von: (in Minuten)', validators=[DataRequired()])
    submit = SubmitField('Intervall Durchführung hinzufügen')
