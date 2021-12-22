from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import Mitarbeiter, Wagen


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
    passwort = PasswordField('Passwort', validators=[DataRequired(), Length(min=4)])
    passwort2 = PasswordField(
        'Passwort wiederholen', validators=[DataRequired(), Length(min=4), EqualTo('passwort')])
    submit = SubmitField('Registrieren')

    def validate_mitarbeiterNr(self, mitarbeiterNr):
        for character in mitarbeiterNr.data: # Hier wird kontrolliert, ob die übergebene Mitarbeiternummer auch wirklich nur aus Zahlen besteht und keine Zeichen drinnen sind, da dies der Fall sein kann, weil es sich bei mitarbeiterNr um ein StringField handelt und in diesem StringField im Formular auch Buchstaben eingegeben werden können
            if not character.isdigit():
                raise ValidationError('Die Mitarbeiternummer muss eine achtstellige Zahl sein und darf keine Buchstaben enthalten!')
        user = Mitarbeiter.query.filter_by(mitarbeiterNr=mitarbeiterNr.data).first()
        if user is not None:
            raise ValidationError('Diese Mitarbeiternummer ist bereits vergeben! Bitte geben sie eine andere Mitarbeiternummer ein.')
    
    def validate_svnr(self, svnr):
        for character in svnr.data:
            if not character.isdigit():
                raise ValidationError('Die Sozialversicherungsnummer muss eine zehnstellige Zahl sein und darf keine Buchstaben enthalten!')
        user = Mitarbeiter.query.filter_by(svnr=svnr.data).first()
        if user is not None:
            raise ValidationError('Diese Sozialversicherungsnummer ist bereits vergeben! Bitte geben sie eine andere Sozialversicherungsnummer ein.')

    def validate_email(self, email):
        user = Mitarbeiter.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Diese Email ist bereits vergeben! Bitte geben sie eine andere Email Adresse ein.')
            
class RegistrationFormZugpersonal(FlaskForm):
    mitarbeiterNr = StringField('Mitarbeiternummer', validators=[DataRequired(), Length(min=8, max=8)]) 
    svnr = StringField('Sozialversicherungsnummer', validators=[DataRequired(), Length(min=10, max=10)])
    vorname = StringField('Vorname', validators=[DataRequired()])
    nachname = StringField('Nachname', validators=[DataRequired()])
    berufsbezeichnung = SelectField('Berufsbezeichnung', choices=[('Triebfahrzeugführer', 'Triebfahrzeugführer'), ('Triebfahrzeugbeleiter', 'Triebfahrzeugbegleiter'), ('Zugführer', 'Zugführer'), ('Zugschaffner', 'Zugschaffner'), ('Zugbegleiter', 'Zugbegleiter')], validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    passwort = PasswordField('Passwort', validators=[DataRequired(), Length(min=4)])
    passwort2 = PasswordField(
        'Passwort wiederholen', validators=[DataRequired(), Length(min=4), EqualTo('passwort')])
    submit = SubmitField('Registrieren')
    
    def validate_mitarbeiterNr(self, mitarbeiterNr):
        for character in mitarbeiterNr.data:
            if not character.isdigit():
                raise ValidationError('Die Mitarbeiternummer muss eine achtstellige Zahl sein und darf keine Buchstaben enthalten!')
        user = Mitarbeiter.query.filter_by(mitarbeiterNr=mitarbeiterNr.data).first()
        if user is not None:
            raise ValidationError('Diese Mitarbeiternummer ist bereits vergeben! Bitte geben sie eine andere Mitarbeiternummer ein.')
    
    def validate_svnr(self, svnr):
        for character in svnr.data:
            if not character.isdigit():
                raise ValidationError('Die Sozialversicherungsnummer muss eine zehnstellige Zahl sein und darf keine Buchstaben enthalten!')
        user = Mitarbeiter.query.filter_by(svnr=svnr.data).first()
        if user is not None:
            raise ValidationError('Diese Sozialversicherungsnummer ist bereits vergeben! Bitte geben sie eine andere Sozialversicherungsnummer ein.')

    def validate_email(self, email):
        user = Mitarbeiter.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Diese Email ist bereits vergeben! Bitte geben sie eine andere Email Adresse ein.')
            
            
class EmptyForm(FlaskForm):
    submit = SubmitField('Entfernen')
    
    
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
                raise ValidationError('Diese Mitarbeiternummer ist bereits vergeben! Bitte geben sie eine andere Mitarbeiternummer ein.')
                
    def validate_svnr(self, svnr):
        for character in svnr.data:
            if not character.isdigit():
                raise ValidationError('Die Sozialversicherungsnummer muss eine zehnstellige Zahl sein und darf keine Buchstaben enthalten!')
        if int(svnr.data) != self.original_svnr:
            user = Mitarbeiter.query.filter_by(svnr=self.svnr.data).first()
            if user is not None:
                raise ValidationError('Diese Sozialversicherungsnummer ist bereits vergeben! Bitte geben sie eine andere Sozialversicherungsnummer ein.')
                
    def validate_email(self, email):
        if email.data != self.original_email:
            user = Mitarbeiter.query.filter_by(email=self.email.data).first()
            if user is not None:
                raise ValidationError('Diese Email ist bereits vergeben! Bitte geben sie eine andere Email ein.')
                
class EditProfileFormZugpersonal(FlaskForm):
    mitarbeiterNr = StringField('Mitarbeiternummer', validators=[DataRequired(), Length(min=8, max=8)]) 
    svnr = StringField('Sozialversicherungsnummer', validators=[DataRequired(), Length(min=10, max=10)])
    vorname = StringField('Vorname', validators=[DataRequired()])
    nachname = StringField('Nachname', validators=[DataRequired()])
    berufsbezeichnung = SelectField('Berufsbezeichnung', choices=[('Triebfahrzeugführer', 'Triebfahrzeugführer'), ('Triebfahrzeugbeleiter', 'Triebfahrzeugbegleiter'), ('Zugführer', 'Zugführer'), ('Zugschaffner', 'Zugschaffner'), ('Zugbegleiter', 'Zugbegleiter')], validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
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
                raise ValidationError('Diese Mitarbeiternummer ist bereits vergeben! Bitte geben sie eine andere Mitarbeiternummer ein.')
                
    def validate_svnr(self, svnr):
        for character in svnr.data:
            if not character.isdigit():
                raise ValidationError('Die Sozialversicherungsnummer muss eine zehnstellige Zahl sein und darf keine Buchstaben enthalten!')
        if int(svnr.data) != self.original_svnr:
            user = Mitarbeiter.query.filter_by(svnr=self.svnr.data).first()
            if user is not None:
                raise ValidationError('Diese Sozialversicherungsnummer ist bereits vergeben! Bitte geben sie eine andere Sozialversicherungsnummer ein.')
                
    def validate_email(self, email):
        if email.data != self.original_email:
            user = Mitarbeiter.query.filter_by(email=self.email.data).first()
            if user is not None:
                raise ValidationError('Diese Email ist bereits vergeben! Bitte geben sie eine andere Email ein.')


class TriebwagenForm(FlaskForm):
    nr = StringField('Wagennummer', validators=[DataRequired(), Length(min=12, max=12)])
    spurweite = SelectField('Spurweite', choices=[('1435', 'Normalspur (1435 mm)'), ('1000', 'Schmalspur (1000 mm)')], validators=[DataRequired()])
    maxZugkraft = StringField('Maximale Zugkraft [Tonnen]', validators=[DataRequired()])
    submit = SubmitField('Erstellen')

    def validate_nr(self, nr):
        for character in nr.data:
            if not character.isdigit():
                raise ValidationError('Die Wagennummer darf nur aus Ziffern bestehen!')
        wagen = Wagen.query.filter_by(nr=nr.data).first()
        if wagen is not None:
            raise ValidationError('Diese Wagennummer ist bereits vergeben! Bitte geben sie eine andere Wagennummer ein.')

    def validate_maxZugkraft(self, maxZugkraft):
        for character in maxZugkraft.data:
            if not character.isdigit():
                raise ValidationError('Die maximale Zugkraft darf nur aus Ziffern bestehen!')

class PersonenwagenForm(FlaskForm):
    nr = StringField('Wagennummer', validators=[DataRequired(), Length(min=12, max=12)])
    spurweite = SelectField('Spurweite', choices=[('1435', 'Normalspur (1435 mm)'), ('1000', 'Schmalspur (1000 mm)')], validators=[DataRequired()])
    sitzanzahl = StringField('Sitzanzahl', validators=[DataRequired(), Length(max=3)])
    maximalgewicht = StringField('Maximalgewicht [Tonnen]', validators=[DataRequired()])
    submit = SubmitField('Erstellen')

    def validate_nr(self, nr):
        for character in nr.data:
            if not character.isdigit():
                raise ValidationError('Die Wagennummer darf nur aus Ziffern bestehen!')
        wagen = Wagen.query.filter_by(nr=nr.data).first()
        if wagen is not None:
            raise ValidationError('Diese Wagennummer ist bereits vergeben! Bitte geben sie eine andere Wagennummer ein.')

    def validate_sitzanzahl(self, sitzanzahl):
        for character in sitzanzahl.data:
            if not character.isdigit():
                raise ValidationError('Die Sitzanzahl darf nur aus Ziffern bestehen!')

    def validate_maximalgewicht(self, maximalgewicht):
        for character in maximalgewicht.data:
            if not character.isdigit():
                raise ValidationError('Das Maximalgewicht darf nur aus Ziffern bestehen!')

class EditTriebwagenForm(FlaskForm):
    nr = StringField('Wagennummer', validators=[DataRequired(), Length(min=12, max=12)])
    spurweite = SelectField('Spurweite', choices=[('1435', 'Normalspur (1435 mm)'), ('1000', 'Schmalspur (1000 mm)')], validators=[DataRequired()])
    maxZugkraft = StringField('Maximale Zugkraft', validators=[DataRequired()])
    submit = SubmitField('Erstellen')

    def __init__(self, original_nr, *args, **kwargs):
        super(EditTriebwagenForm, self).__init__(*args, **kwargs)
        self.original_nr = original_nr

    def validate_nr(self, nr):
        for character in nr.data:
            if not character.isdigit():
                raise ValidationError('Die Wagennummer darf nur aus Ziffern bestehen!')
        if int(nr.data) != self.original_nr:
            wagen = Wagen.query.filter_by(nr=nr.data).first()
            if wagen is not None:
                raise ValidationError('Diese Wagennummer ist bereits vergeben! Bitte geben sie eine andere Wagennummer ein.')

    def validate_maxZugkraft(self, maxZugkraft):
        for character in maxZugkraft.data:
            if not character.isdigit():
                raise ValidationError('Die maximale Zugkraft darf nur aus Ziffern bestehen!')

class EditPersonenwagenForm(FlaskForm):
    nr = StringField('Wagennummer', validators=[DataRequired(), Length(min=12, max=12)])
    spurweite = SelectField('Spurweite', choices=[('1435', 'Normalspur (1435 mm)'), ('1000', 'Schmalspur (1000 mm)')], validators=[DataRequired()])
    sitzanzahl = StringField('Sitzanzahl', validators=[DataRequired(), Length(max=3)])
    maximalgewicht = StringField('Maximalgewicht [Tonnen]', validators=[DataRequired()])
    submit = SubmitField('Erstellen')

    def __init__(self, original_nr, *args, **kwargs):
        super(EditPersonenwagenForm, self).__init__(*args, **kwargs)
        self.original_nr = original_nr

    def validate_nr(self, nr):
        for character in nr.data:
            if not character.isdigit():
                raise ValidationError('Die Wagennummer darf nur aus Ziffern bestehen!')
        if int(nr.data) != self.original_nr:
            wagen = Wagen.query.filter_by(nr=nr.data).first()
            if wagen is not None:
                raise ValidationError('Diese Wagennummer ist bereits vergeben! Bitte geben sie eine andere Wagennummer ein.')

    def validate_sitzanzahl(self, sitzanzahl):
        for character in sitzanzahl.data:
            if not character.isdigit():
                raise ValidationError('Die Sitzanzahl darf nur aus Ziffern bestehen!')

    def validate_maximalgewicht(self, maximalgewicht):
        for character in maximalgewicht.data:
            if not character.isdigit():
                raise ValidationError('Das Maximalgewicht darf nur aus Ziffern bestehen!')