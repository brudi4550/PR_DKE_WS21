from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, PasswordField, BooleanField, SelectField
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

# class RegistrationForm(FlaskForm):
#     employee_id = StringField('Employee ID', validators=[DataRequired()])
#     password = PasswordField('Password', validators=[DataRequired()])
#     password2 = PasswordField(
#         'Repeat Password', validators=[DataRequired(), EqualTo('password')])
#     submit = SubmitField('Register')
#
#     def validate_username(self, username):
#         user = User.query.filter_by(username=username.data).first()
#         if user is not None:
#             raise ValidationError('Please use a different username.')
#
#     def validate_email(self, email):
#         user = User.query.filter_by(email=email.data).first()
#         if user is not None:
#             raise ValidationError('Please use a different email address.')


# class EditProfileForm(FlaskForm):
#     username = StringField('Username', validators=[DataRequired()])
#     about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
#     submit = SubmitField('Submit')
#
#     def __init__(self, original_username, *args, **kwargs):
#         super(EditProfileForm, self).__init__(*args, **kwargs)
#         self.original_username = original_username
#
#     def validate_username(self, username):
#         if username.data != self.original_username:
#             user = User.query.filter_by(username=self.username.data).first()
#             if user is not None:
#                 raise ValidationError('Please use a different username.')
