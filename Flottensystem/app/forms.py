import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    SelectField, DateTimeField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import Mitarbeiter, Wagen, Triebwagen, Personenwagen, Zug, Wartung

''' Folgende Vorgehensweise wurde bei der Codebeschreibung vorgenommen: Es wurde darauf geachtet, dass der Code nur einmal beschrieben wurde.
    In den darauf folgenden Codebeschreibungen befinden sich wenige bis teilweise keine Beschreibungen. Hier wird darauf verwiesen, in den 
    vorherigen Implementierungen nachzuschauen. '''

class LoginForm(FlaskForm):
    ''' Mit dem Validator "DataRequired()" wird festgelegt, dass dieses Feld ausgefüllt werden muss. Anschließend wird mit dem Validator "Email()"
        die Schreibweise bzw. Syntax einer Email-Adresse sichergestellt, also dass in diesem Feld ein @ existieren muss, welches danach anschließend
        mit einem String, einem Punkt und einem weiteren String beendet wird (z.B.: "...@live.at") '''
    email = StringField('Email', validators=[DataRequired(), Email()])
    passwort = PasswordField('Passwort', validators=[DataRequired()])
    angemeldet_bleiben = BooleanField('Angemeldet bleiben')
    submit = SubmitField('Anmelden')
    


class RegistrationForm(FlaskForm):
    ''' In der nachfolgenden Zeile wird die Länge der Mitarbeiternummer bestimmt. Diese muss 8 Zeichen lang sein, was durch
        min und max im Validator "Length()" sichergestellt wird '''
    mitarbeiterNr = StringField('Mitarbeiternummer', validators=[DataRequired(), Length(min=8, max=8)]) 
    svnr = StringField('Sozialversicherungsnummer', validators=[DataRequired(), Length(min=10, max=10)])
    vorname = StringField('Vorname', validators=[DataRequired()])
    nachname = StringField('Nachname', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    # Als nächstes wird mit dem Validator "Length" festgelegt, dass ein Passwort eine Länge von mindestens 4 Zeichen haben muss
    passwort = PasswordField('Passwort', validators=[DataRequired(), Length(min=4)])
    # Mit EqualTo wird kontrolliert, ob das eingegebene Passwort in "passwort2" mit dem in "passwort" übereinstimmt
    passwort2 = PasswordField('Passwort wiederholen', validators=[DataRequired(), Length(min=4), EqualTo('passwort')])
    submit = SubmitField('Registrieren')

    def validate_mitarbeiterNr(self, mitarbeiterNr):
        ''' In der nachfolgenden for-Schleife wird kontrolliert, ob die übergebene Mitarbeiternummer auch wirklich nur aus
            Zahlen besteht und keine Zeichen drinnen sind, da dies der Fall sein kann, weil es sich bei mitarbeiterNr um
            ein StringField handelt und in diesem StringField im Formular auch Buchstaben eingegeben werden können '''
        for character in mitarbeiterNr.data:
            if not character.isdigit():
                raise ValidationError('Die Mitarbeiternummer muss eine achtstellige Zahl sein und darf keine Buchstaben enthalten!')

        ''' Es wird überprüft, ob der Mitarbeiter unter der eingegebenen Mitarbeiternummer schon existiert. Ist dies der Fall,
            wird ein Fehler ausgegeben. '''
        user = Mitarbeiter.query.filter_by(mitarbeiterNr=mitarbeiterNr.data).first()
        if user is not None:
            raise ValidationError('Diese Mitarbeiternummer ist bereits vergeben! Bitte geben sie eine andere Mitarbeiternummer ein.')
    
    def validate_svnr(self, svnr):
        # Analog zu "validate_mitarbeiterNr" wird das gleiche auch hier überprüft
        for character in svnr.data:
            if not character.isdigit():
                raise ValidationError('Die Sozialversicherungsnummer muss eine zehnstellige Zahl sein und darf keine Buchstaben enthalten!')
        user = Mitarbeiter.query.filter_by(svnr=svnr.data).first()
        if user is not None:
            raise ValidationError('Diese Sozialversicherungsnummer ist bereits vergeben! Bitte geben sie eine andere Sozialversicherungsnummer ein.')

    def validate_email(self, email):
        ''' Hier wird überprüft, ob die eingegebene Email-Adresse in der Datenbank schon existiert und somit vergeben ist '''
        user = Mitarbeiter.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Diese Email ist bereits vergeben! Bitte geben sie eine andere Email Adresse ein.')
            
class RegistrationFormZugpersonal(FlaskForm):
    mitarbeiterNr = StringField('Mitarbeiternummer', validators=[DataRequired(), Length(min=8, max=8)]) 
    svnr = StringField('Sozialversicherungsnummer', validators=[DataRequired(), Length(min=10, max=10)])
    vorname = StringField('Vorname', validators=[DataRequired()])
    nachname = StringField('Nachname', validators=[DataRequired()])
    ''' Im nachfolgenden SelectField werden die Auswahlmöglichkeiten bei der Wahl der Berufsbezeichnung festgelegt. Dies ist empfohlen,
        wenn es nicht sehr viele Auswahlmöglichkeiten gibt. Die Variable "choices" ist eine Liste, in der die verschiedenen
        Auswahlmöglichkeiten eingetragen werden. Die Liste besteht aus (value, label) Paaren, also ist links der Wert eingetragen, welches 
        dann die Variable berufsbezeichnng bekommt und rechts steht die Beschriftung für diesen Wert, also das ist jener Teil, den der User
        dann im Formular sieht und auswählen kann. '''
    berufsbezeichnung = SelectField('Berufsbezeichnung', choices=[('Triebfahrzeugführer', 'Triebfahrzeugführer'),
                                                                  ('Triebfahrzeugbeleiter', 'Triebfahrzeugbegleiter'),
                                                                  ('Zugführer', 'Zugführer'), ('Zugschaffner', 'Zugschaffner'),
                                                                  ('Zugbegleiter', 'Zugbegleiter')], validators=[DataRequired()])
    zugNr = SelectField('Zugewiesener Zug', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    passwort = PasswordField('Passwort', validators=[DataRequired(), Length(min=4)])
    passwort2 = PasswordField(
        'Passwort wiederholen', validators=[DataRequired(), Length(min=4), EqualTo('passwort')])
    submit = SubmitField('Registrieren')

    # Für die Erklärung der folgenden Methoden wird auf die vorherige RegistrationForm verwiesen
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
            
# Diese EmptyForm wird bspw. für das Profilformular gebraucht, bei der ein Administrator sich selbst löschen kann
class EmptyForm(FlaskForm):
    submit = SubmitField('Entfernen')
    
    
class EditProfileForm(FlaskForm):
    mitarbeiterNr = StringField('Mitarbeiternummer', validators=[DataRequired(), Length(min=8, max=8)])
    svnr = StringField('Sozialversicherungsnummer', validators=[DataRequired(), Length(min=10, max=10)])
    vorname = StringField('Vorname', validators=[DataRequired()])
    nachname = StringField('Nachname', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Bestätigen')

    ''' Nachfolgend wird ein überladener Konstruktor definiert, welches die Unique Eigenschaften der Mitarbeitertabelle
        speichert. In den nachfolgenden Methoden wird dann der Wert von diesen Feldern abgefragt, um zu überprüfen, ob
        sich ein jeweiliger Wert verändert hat'''
    def __init__(self, original_mitarbeiterNr, original_svnr, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_mitarbeiterNr = original_mitarbeiterNr
        self.original_svnr = original_svnr
        self.original_email = original_email

    def validate_mitarbeiterNr(self, mitarbeiterNr):
        for character in mitarbeiterNr.data:
            if not character.isdigit():
                raise ValidationError('Die Mitarbeiternummer muss eine achtstellige Zahl sein und darf keine Buchstaben enthalten!')
        ''' Da es sich beim übergebenen Parameter mitarbeiterNr um einen StringField handelt, muss dieser in ein int geparst werden,
            sonst wäre diese if-Bedingung immer false, weil man einen String mit einem int-Wert vergleichen würde. Es wird in dieser
            if-Abfrage überprüft, ob das Feld "original_mitarbeiterNr" (welches mit dem überladenen Konstruktor erstellt wurde) von 
            dem im Formular eingetragenen Wert unterscheidet. Ist dies der Fall, dann heißt es, dass in diesem Feld eine neue
            Mitarbeiternummer eingegeben wurde. Anschließend wird dann überprüft, ob die neu eingegebene Mitarbeiternummer schon existiert.
            Wenn dies der Fall ist, dann wird ein Fehler ausgegeben. Dieser Vorgang wird auch ín den folgenden Methoden durchgeführt. '''
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
                
class EditProfileFormZugpersonal(FlaskForm):
    mitarbeiterNr = StringField('Mitarbeiternummer', validators=[DataRequired(), Length(min=8, max=8)]) 
    svnr = StringField('Sozialversicherungsnummer', validators=[DataRequired(), Length(min=10, max=10)])
    vorname = StringField('Vorname', validators=[DataRequired()])
    nachname = StringField('Nachname', validators=[DataRequired()])
    berufsbezeichnung = SelectField('Berufsbezeichnung', choices=[('Triebfahrzeugführer', 'Triebfahrzeugführer'),
                                                                  ('Triebfahrzeugbeleiter', 'Triebfahrzeugbegleiter'),
                                                                  ('Zugführer', 'Zugführer'), ('Zugschaffner', 'Zugschaffner'),
                                                                  ('Zugbegleiter', 'Zugbegleiter')], validators=[DataRequired()])
    zugNr = SelectField('Zugewiesener Zug', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Bestätigen')

    # Für die Erklärung dieses Formulars wird auf das vorherige Formular EditProfileForm verwiesen
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
    ''' Es wird angenommen, dass ein Waggon maximal zweistellig wiegt und maximal eine zweistellige sitzanzahl hat, also weniger als 100 Tonnen
        und weniger als 100 Sitzplätze '''
    sitzanzahl = StringField('Sitzanzahl', validators=[DataRequired(), Length(max=2)])
    maximalgewicht = StringField('Maximalgewicht [Tonnen]', validators=[DataRequired(), Length(max=2)])
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
    submit = SubmitField('Bestätigen')

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
    sitzanzahl = StringField('Sitzanzahl', validators=[DataRequired(), Length(max=2)])
    maximalgewicht = StringField('Maximalgewicht [Tonnen]', validators=[DataRequired(), Length(max=2)])
    submit = SubmitField('Bestätigen')

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



class ZugForm(FlaskForm):
    nr = StringField('Zugnummer', validators=[DataRequired()])
    name = StringField('Zugname', validators=[DataRequired()])
    triebwagen_nr = SelectField('Triebwagen', validators=[DataRequired()])
    submit = SubmitField('Erstellen')

    def validate_nr(self, nr):
        zug = Zug.query.filter_by(nr=nr.data).first()
        if zug is not None:
            raise ValidationError('Diese Zugnummer ist bereits vergeben! Bitte geben sie eine andere Zugnummer ein.')

    def validate_triebwagen_nr(self, triebwagen_nr):
        triebwagen = Triebwagen.query.filter_by(nr=triebwagen_nr.data).first()
        ''' Es muss nachfolgend nicht abgefragt werden, ob es den Triebwagen überhaupt gibt, da die Triebwaggons dynamisch 
            im SelectField gebunden werden und es somit auch nur die Triebwaggons im SelectField erscheinen, die in der 
            Datenbank existieren. Deswegen wird nachfolgend auch nur abgefragt, ob der ausgewählte Triebwagen schon einem 
            Zug zugeteilt wurde. Ist dieser der Fall, so wird ein Fehler ausgegeben.'''
        if triebwagen.zug is not None:
            raise ValidationError('Dieser Triebwagen wurde bereits einem Zug zugeordnet, bitte wählen Sie einen anderen Triebwagen aus')

class EditZugForm(FlaskForm):
    nr = StringField('Zugnummer', validators=[DataRequired()])
    name = StringField('Zugname', validators=[DataRequired()])
    triebwagen_nr = SelectField('Triebwagen', validators=[DataRequired()])
    submit = SubmitField('Erstellen')

    def __init__(self, original_nr, original_triebwagen_nr, *args, **kwargs):
        super(EditZugForm, self).__init__(*args, **kwargs)
        self.original_nr = original_nr
        self.original_triebwagen_nr = original_triebwagen_nr

    def validate_nr(self, nr):
        if nr.data != self.original_nr:
            zug = Zug.query.filter_by(nr=nr.data).first()
            if zug is not None:
                raise ValidationError('Diese Zugnummer ist bereits vergeben! Bitte geben sie eine andere Zugnummer ein.')

    def validate_triebwagen_nr(self, triebwagen_nr):
        if triebwagen_nr.data != self.original_triebwagen_nr:
            triebwagen = Triebwagen.query.filter_by(nr=triebwagen_nr.data).first()
            if triebwagen.zug is not None and triebwagen.zug.nr != self.original_nr:
                raise ValidationError('Dieser Triebwagen  wurde bereits einem Zug zugeteilt, bitte wählen Sie einen anderen Triebwagen aus')



class WartungForm(FlaskForm):
    wartungsNr = StringField('Wartungsnummer', validators=[DataRequired()])
    ''' In der nachfolgenden Zeile wird durch "format" angegeben, in welchem Format das Datum und die Uhrzeit 
        eingegeben werden müssen '''
    von = DateTimeField('Von (Format: "dd.mm.YYYY HH:MM")', format='%d.%m.%Y %H:%M', validators=[DataRequired()])
    bis = DateTimeField('Bis (Format: "dd.mm.YYYY HH:MM")', format='%d.%m.%Y %H:%M', validators=[DataRequired()])
    #mitarbeiterNr = SelectMultipleField('Wartungspersonal', validators=[DataRequired()])
    zugNr = SelectField('Zugnummer', validators=[DataRequired()])
    submit = SubmitField('Erstellen')

    def validate_wartungsNr(self, wartungsNr):
        for character in wartungsNr.data:
            if not character.isdigit():
                raise ValidationError('Die Wartungsnummer darf nur aus Ziffern bestehen!')
        wartung = Wartung.query.filter_by(wartungsNr=wartungsNr.data).first()
        if wartung is not None:
            raise ValidationError('Diese Wartungsnummer ist bereits vergeben! Bitte geben sie eine andere Wartungsnummer ein.')

    def validate_von(self, von):
        ''' Hier wird überprüft, ob der Beginnzeitpunkt der Wartung nach dem Endzeitpunkt der Wartung erfolgt. Ist diese
        Abfrage True, so wird ein Fehler ausgegeben '''
        if von.data > self.bis.data:
            raise ValidationError('Der Beginn einer Wartung kann nicht nach dem Ende dieser erfolgen!')
        ''' Als nächstes wird überprüft ob die Start- und Endzeit der Wartung gleich ist. '''
        if von.data == self.bis.data:
            raise ValidationError('Beginn und Ende einer Wartung darf nicht gleich sein!')
        ''' Es wird angenommen, dass eine Wartung mindestens 30 Minuten (also 1800 Sekunden) dauert. Dies wird
            in der nachfolgenden Abfrage überprüft, dabei wird das Timedelta berechnet, also der zeitliche
            Unterschied zwischen Wartungsbeginn und Wartungsende. Dieser zeitliche Unterschied wird durch
            "total_seconds" in Sekunden umgewandelt. Nun wird überprüft ob der zeitliche Unterschied, welches
            in Sekunden umgewandelt wurde, kürzer als 1800 Sekunden (also eine halbe Stunde) ist '''
        if (self.bis.data - von.data).total_seconds() < 1800:
            raise ValidationError('Eine Wartung dauert mindestens 30 Minuten!')


    def validate_bis(self, bis):
        ''' Hierbei handelt es sich um eine ähnliche Abfrage wie in "validate_von", nur dass hier überprüft wird,
        ob der Endzeitpunkt der Wartung vor dem Beginnzeitpunkt der Wartung erfolgt. Auch hier wird ein Fehler
        ausgegeben, falls die Abfrage True ist '''
        if bis.data < self.von.data:
            raise ValidationError('Das Ende der Wartung muss nach dem Beginn dieser erfolgen!')
        ''' Die folgenden zwei Abfragen sind auch fast identisch wie in "validate_von" '''
        if bis.data == self.von.data:
            raise ValidationError('Beginn und Ende einer Wartung darf nicht gleich sein!')
        if (bis.data - self.von.data).total_seconds() < 1800:
            raise ValidationError('Eine Wartung dauert mindestens 30 Minuten!')

class EditWartungForm(FlaskForm):
    wartungsNr = StringField('Wartungsnummer', validators=[DataRequired()])
    von = DateTimeField('Von', format='%d.%m.%Y %H:%M', validators=[DataRequired()])
    bis = DateTimeField('Bis', format='%d.%m.%Y %H:%M', validators=[DataRequired()])
    zugNr = SelectField('Zugnummer', validators=[DataRequired()])
    submit = SubmitField('Erstellen')

    def __init__(self, original_nr, *args, **kwargs):
        super(EditWartungForm, self).__init__(*args, **kwargs)
        self.original_nr = original_nr

    def validate_wartungsNr(self, wartungsNr):
        for character in wartungsNr.data:
            if not character.isdigit():
                raise ValidationError('Die Wartungsnummer darf nur aus Ziffern bestehen!')
        if int(wartungsNr.data) != self.original_nr:
            wartung = Wartung.query.filter_by(wartungsNr=wartungsNr.data).first()
            if wartung is not None:
                raise ValidationError('Diese Wartungsnummer ist bereits vergeben! Bitte geben sie eine andere Wartungsnummer ein.')

    def validate_von(self, von):
        if von.data > self.bis.data:
            raise ValidationError('Der Beginn einer Wartung kann nicht nach dem Ende dieser erfolgen!')

    def validate_bis(self, bis):
        if bis.data < self.von.data:
            raise ValidationError('Das Ende der Wartung muss nach dem Beginn dieser erfolgen!')