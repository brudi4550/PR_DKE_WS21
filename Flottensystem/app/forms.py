from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import Mitarbeiter


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    passwort = PasswordField('Passwort', validators=[DataRequired()])
    angemeldet_bleiben = BooleanField('Angemeldet bleiben')
    submit = SubmitField('Anmelden')
    
    
class RegistrationForm(FlaskForm):
    mitarbeiterNr = StringField('Mitarbeiternummer', validators=[DataRequired(), Length(min=8, max=8)]) 
    svnr = StringField('Sozialversicherungsnummer', validators=[DataRequired(), Length(min=10, max=10)])
    vorname = StringField('Vorname', validators=[DataRequired()])
    nachname = StringField('Nachname', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    passwort = PasswordField('Passwort', validators=[DataRequired()])
    passwort2 = PasswordField(
        'Passwort wiederholen', validators=[DataRequired(), EqualTo('passwort')])
    submit = SubmitField('Registrieren')

    def validate_mitarbeiterNr(self, mitarbeiterNr):
        for character in mitarbeiterNr.data: # Hier wird kontrolliert, ob die übergebene Mitarbeiternummer auch wirklich nur aus Zahlen besteht und keine Zeichen drinnen sind, da dies der Fall sein kann, weil es sich bei mitarbeiterNr um ein StringField handelt und in diesem StringField im Formular auch Buchstaben eingegeben werden können
            if not character.isdigit():
                raise ValidationError('Die Mitarbeiternummer muss eine achtstellige Zahl sein und darf keine Buchstaben enthalten!')
        user = Mitarbeiter.query.filter_by(mitarbeiterNr=mitarbeiterNr.data).first()
        if user is not None:
            raise ValidationError('Diese Mitarbeiternummer ist bereits vergeben. Bitte geben sie eine andere Mitarbeiternummer ein.')
    
    def validate_svnr(self, svnr):
        for character in svnr.data:
            if not character.isdigit():
                raise ValidationError('Die Sozialversicherungsnummer muss eine zehnstellige Zahl sein und darf keine Buchstaben enthalten!')
        user = Mitarbeiter.query.filter_by(svnr=svnr.data).first()
        if user is not None:
            raise ValidationError('Bitte geben sie eine andere Sozialversicherungsnummer ein.')

    def validate_email(self, email):
        user = Mitarbeiter.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Bitte geben sie eine andere Email Adresse ein.')
            
class RegistrationFormZugpersonal(FlaskForm):
    mitarbeiterNr = StringField('Mitarbeiternummer', validators=[DataRequired(), Length(min=8, max=8)]) 
    svnr = StringField('Sozialversicherungsnummer', validators=[DataRequired(), Length(min=10, max=10)])
    vorname = StringField('Vorname', validators=[DataRequired()])
    nachname = StringField('Nachname', validators=[DataRequired()])
    berufsbezeichnung = StringField('Berufsbezeichnung', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    passwort = PasswordField('Passwort', validators=[DataRequired()])
    passwort2 = PasswordField(
        'Passwort wiederholen', validators=[DataRequired(), EqualTo('passwort')])
    submit = SubmitField('Registrieren')
    
    def validate_mitarbeiterNr(self, mitarbeiterNr):
        for character in mitarbeiterNr.data:
            if not character.isdigit():
                raise ValidationError('Die Mitarbeiternummer muss eine achtstellige Zahl sein und darf keine Buchstaben enthalten!')
        user = Mitarbeiter.query.filter_by(mitarbeiterNr=mitarbeiterNr.data).first()
        if user is not None:
            raise ValidationError('Diese Mitarbeiternummer ist bereits vergeben. Bitte geben sie eine andere Mitarbeiternummer ein.')
    
    def validate_svnr(self, svnr):
        for character in svnr.data:
            if not character.isdigit():
                raise ValidationError('Die Sozialversicherungsnummer muss eine zehnstellige Zahl sein und darf keine Buchstaben enthalten!')
        user = Mitarbeiter.query.filter_by(svnr=svnr.data).first()
        if user is not None:
            raise ValidationError('Bitte geben sie eine andere Sozialversicherungsnummer ein.')

    def validate_email(self, email):
        user = Mitarbeiter.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Bitte geben sie eine andere Email Adresse ein.')
            
            
class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')
    
    
class EditProfileForm(FlaskForm):
    mitarbeiterNr = StringField('Mitarbeiternummer', validators=[DataRequired(), Length(min=8, max=8)]) 
    svnr = StringField('Sozialversicherungsnummer', validators=[DataRequired(), Length(min=10, max=10)])
    vorname = StringField('Vorname', validators=[DataRequired()])
    nachname = StringField('Nachname', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Bestätigen')

    def __init__(self, original_mitarbeiterNr, original_svnr, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_mitarbeiterNr = original_mitarbeiterNr
        self.original_svnr = original_svnr
        self.original_email = original_email

    def validate_mitarbeiterNr(self, mitarbeiterNr):
        for character in mitarbeiterNr.data:
            if not character.isdigit():
                raise ValidationError('Die Mitarbeiternummer muss eine achtstellige Zahl sein und darf keine Buchstaben enthalten!')
        if int(mitarbeiterNr.data) != self.original_mitarbeiterNr: # Da es sich beim übergebenen Parameter mitarbeiterNr um einen StringField handelt, muss dieser in ein int geparst werden, sonst wäre diese if-Bedingung immer false
            user = Mitarbeiter.query.filter_by(mitarbeiterNr=self.mitarbeiterNr.data).first()
            if user is not None:
                raise ValidationError('Diese Mitarbeiternummer ist bereits vergeben. Bitte geben sie eine andere Mitarbeiternummer ein.')
                
    def validate_svnr(self, svnr):
        for character in svnr.data:
            if not character.isdigit():
                raise ValidationError('Die Sozialversicherungsnummer muss eine zehnstellige Zahl sein und darf keine Buchstaben enthalten!')
        if int(svnr.data) != self.original_svnr:
            user = Mitarbeiter.query.filter_by(svnr=self.svnr.data).first()
            if user is not None:
                raise ValidationError('Diese Sozialversicherungsnummer ist bereits vergeben. Bitte geben sie eine andere Mitarbeiternummer ein.')
                
    def validate_email(self, email):
        if email.data != self.original_email:
            user = Mitarbeiter.query.filter_by(email=self.email.data).first()
            if user is not None:
                raise ValidationError('Diese Email ist bereits vergeben. Bitte geben sie eine andere Mitarbeiternummer ein.')
                
class EditProfileFormZugpersonal(FlaskForm):
    mitarbeiterNr = StringField('Mitarbeiternummer', validators=[DataRequired(), Length(min=8, max=8)]) 
    svnr = StringField('Sozialversicherungsnummer', validators=[DataRequired(), Length(min=10, max=10)])
    vorname = StringField('Vorname', validators=[DataRequired()])
    nachname = StringField('Nachname', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    berufsbezeichnung = StringField('Berufsbezeichnung', validators=[DataRequired()])
    submit = SubmitField('Bestätigen')

    def __init__(self, original_mitarbeiterNr, original_svnr, original_email, *args, **kwargs):
        super(EditProfileFormZugpersonal, self).__init__(*args, **kwargs)
        self.original_mitarbeiterNr = original_mitarbeiterNr
        self.original_svnr = original_svnr
        self.original_email = original_email

    def validate_mitarbeiterNr(self, mitarbeiterNr):
        for character in mitarbeiterNr.data:
            if not character.isdigit():
                raise ValidationError('Die Mitarbeiternummer muss eine achtstellige Zahl sein und darf keine Buchstaben enthalten!')
        if int(mitarbeiterNr.data) != self.original_mitarbeiterNr:
            user = Mitarbeiter.query.filter_by(mitarbeiterNr=self.mitarbeiterNr.data).first()
            if user is not None:
                raise ValidationError('Diese Mitarbeiternummer ist bereits vergeben. Bitte geben sie eine andere Mitarbeiternummer ein.')
                
    def validate_svnr(self, svnr):
        for character in svnr.data:
            if not character.isdigit():
                raise ValidationError('Die Sozialversicherungsnummer muss eine zehnstellige Zahl sein und darf keine Buchstaben enthalten!')
        if int(svnr.data) != self.original_svnr:
            user = Mitarbeiter.query.filter_by(svnr=self.svnr.data).first()
            if user is not None:
                raise ValidationError('Diese Sozialversicherungsnummer ist bereits vergeben. Bitte geben sie eine andere Mitarbeiternummer ein.')
                
    def validate_email(self, email):
        if email.data != self.original_email:
            user = Mitarbeiter.query.filter_by(email=self.email.data).first()
            if user is not None:
                raise ValidationError('Diese Email ist bereits vergeben. Bitte geben sie eine andere Mitarbeiternummer ein.')
