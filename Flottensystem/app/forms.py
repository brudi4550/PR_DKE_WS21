from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    SelectField, DateTimeField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import Mitarbeiter, Wagen, Triebwagen, Zug, Wartung

''' Folgende Vorgehensweise wurde bei der Codebeschreibung vorgenommen: Es wurde darauf geachtet, dass der Code nur einmal beschrieben wurde.
    In den darauf folgenden Codebeschreibungen befinden sich wenige bis teilweise keine Beschreibungen. Hier wird meistens darauf verwiesen, 
    in den vorherigen Implementierungen nachzuschauen. '''

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
            ein StringField handelt und in diesem StringField im Formular auch Buchstaben eingegeben werden können. '''
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

    ''' Nachfolgend wird überprüft, ob der Vorname nur aus Buchstaben besteht. Ist dies nicht der Fall, so wird ein Error geworfen. '''
    def validate_vorname(self, vorname):
        for character in vorname.data:
            if character.isdigit():
                raise ValidationError('Der Vorname darf keine Zahl enthalten! Überprüfen Sie bitte Ihre Angaben.')

    ''' Analog zu "validate_vorname" wird dieselbe Überprüfung beim Nachnamen durchgeführt. '''
    def validate_nachname(self, nachname):
        for character in nachname.data:
            if character.isdigit():
                raise ValidationError('Der Nachname darf keine Zahl enthalten! Überprüfen Sie bitte Ihre Angaben.')

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
    ''' Im nachfolgenden SelectField werden die Auswahlmöglichkeiten bei der Wahl der Berufsbezeichnung festgelegt. Dieses statische
        setzen der Werte ist empfohlen, wenn es nicht sehr viele Auswahlmöglichkeiten gibt. Die Variable "choices" ist eine Liste, in der 
        die verschiedenen Auswahlmöglichkeiten eingetragen werden. Die Liste besteht aus (value, label) Paaren, also ist links der Wert 
        eingetragen, welches dann die Variable "berufsbezeichnng" bekommt und rechts steht die Beschriftung für diesen Wert, also das ist 
        jener Teil, den der User dann im Formular sieht und auswählen kann. Bei diesem SelectField ist es eigentlich nicht notwendig, ein 
        "DataRequired" validator einzusetzen, da ohnehin immer ein Wert gesetzt wird (wenn man im SelectField nichts auswählt, so wird
        automatisch das erste Feld ausgewählt). Hier wurde trotzdem ein "DataRequired" validator eingesetzt. '''
    berufsbezeichnung = SelectField('Berufsbezeichnung', choices=[('Triebfahrzeugführer', 'Triebfahrzeugführer'),
                                                                  ('Triebfahrzeugbeleiter', 'Triebfahrzeugbegleiter'),
                                                                  ('Zugführer', 'Zugführer'), ('Zugschaffner', 'Zugschaffner'),
                                                                  ('Zugbegleiter', 'Zugbegleiter')], validators=[DataRequired()])
    zugNr = SelectField('Zugewiesener Zug', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    passwort = PasswordField('Passwort', validators=[DataRequired(), Length(min=4)])
    passwort2 = PasswordField('Passwort wiederholen', validators=[DataRequired(), Length(min=4), EqualTo('passwort')])
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

    def validate_vorname(self, vorname):
        for character in vorname.data:
            if character.isdigit():
                raise ValidationError('Der Vorname darf keine Zahl enthalten! Überprüfen Sie bitte Ihre Angaben.')

    def validate_nachname(self, nachname):
        for character in nachname.data:
            if character.isdigit():
                raise ValidationError('Der Nachname darf keine Zahl enthalten! Überprüfen Sie bitte Ihre Angaben.')

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
        sich ein jeweiliger Wert verändert hat. '''
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

    def validate_vorname(self, vorname):
        for character in vorname.data:
            if character.isdigit():
                raise ValidationError('Der Vorname darf keine Zahl enthalten! Überprüfen Sie bitte Ihre Angaben.')

    def validate_nachname(self, nachname):
        for character in nachname.data:
            if character.isdigit():
                raise ValidationError('Der Nachname darf keine Zahl enthalten! Überprüfen Sie bitte Ihre Angaben.')
                
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

    def validate_vorname(self, vorname):
        for character in vorname.data:
            if character.isdigit():
                raise ValidationError('Der Vorname darf keine Zahl enthalten! Überprüfen Sie bitte Ihre Angaben.')

    def validate_nachname(self, nachname):
        for character in nachname.data:
            if character.isdigit():
                raise ValidationError('Der Nachname darf keine Zahl enthalten! Überprüfen Sie bitte Ihre Angaben.')
                
    def validate_email(self, email):
        if email.data != self.original_email:
            user = Mitarbeiter.query.filter_by(email=self.email.data).first()
            if user is not None:
                raise ValidationError('Diese Email ist bereits vergeben! Bitte geben sie eine andere Email ein.')



class TriebwagenForm(FlaskForm):
    ''' Laut Internetrecherchen ist eine Wagennummer eine 12-stellige Zahl. Deswegen wird hier die
        Länge der Wagennummer auf genau 12 begrenzt. '''
    nr = StringField('Wagennummer', validators=[DataRequired(), Length(min=12, max=12)])
    spurweite = SelectField('Spurweite', choices=[('1435', 'Normalspur (1435 mm)'), ('1000', 'Schmalspur (1000 mm)')], validators=[DataRequired()])
    maxZugkraft = StringField('Maximale Zugkraft [Tonnen]', validators=[DataRequired(), Length(max=2)])
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
    maxZugkraft = StringField('Maximale Zugkraft', validators=[DataRequired(), Length(max=2)])
    submit = SubmitField('Bestätigen')

    ''' Für die Erklärung der Notwendigkeit des überladenen Konstruktors, siehe "EditProfileForm". '''
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

    ''' Als nächstes werden die Spurweiten behandelt. Hier wird überprüft ob ein Waggon bereits einem Zug zugeteilt worden ist.
        Ist dies der Fall, so kann bei diesem Waggon keine Änderung in der Spurweite durchgeführt werden. '''
    def validate_spurweite(self, spurweite):
        wagen = Wagen.query.filter_by(nr=self.original_nr).first()
        if wagen.zug is not None and wagen.spurweite != int(spurweite.data):
            raise ValidationError('Die Spurweite eines Triebwagens, welches bereits einem Zug zugeordnet ist, kann nicht geändert werden! ')

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

    def validate_spurweite(self, spurweite):
        wagen = Wagen.query.filter_by(nr=self.original_nr).first()
        if wagen.zug is not None and wagen.spurweite != int(spurweite.data):
            raise ValidationError('Die Spurweite eines Personenwagens, welches bereits einem Zug zugeordnet ist, kann nicht geändert werden! ')

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
    ''' Bei "triebwagen_nr" handelt es sich um ein dynamisches SelectField. Hier wird der Variable "choices"
        erst in der jeweiligen View Function Werte zugewiesen und somit wird das SelectField dynamisch in der 
        View Function mit Werten befüllt. '''
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
            Zug zugeteilt wurde. Ist dies der Fall, so wird ein Fehler ausgegeben. Diese "validate_triebwagen_nr" Methode
            ist hier nur aus Sicherheitsgründen trotzdem implementiert worden, da dies eigentlich nicht notwendig war, weil
            man bei der Erstellung eines Zuges nur Triebwaggons auswählen kann, die keinem Zug zugeordnet sind. '''
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


''' Anmerkung: Es wird angenommen, dass man auch Wartungen hinzufügen kann, welche in der Vergangenheit liegen. Bspw. hat man
    vergessen, eine Wartung, die schon vergangen ist, hinzuzufügen und macht dies im Nachhinein oder es wurde eine ungeplante
    Wartung durchgeführt, die man im Nachhinein eintragen will. Deswegen wird auch nicht überprüft, ob eine Wartung, die erstellt
    wird, in der Vergangenheit liegt. '''
class WartungForm(FlaskForm):
    wartungsNr = StringField('Wartungsnummer', validators=[DataRequired()])
    ''' In der nachfolgenden Zeile wird durch "format" angegeben, in welchem Format das Datum und die Uhrzeit 
        eingegeben werden müssen. '''
    von = DateTimeField('Von (Format: "dd.mm.YYYY HH:MM")', format='%d.%m.%Y %H:%M', validators=[DataRequired()])
    bis = DateTimeField('Bis (Format: "dd.mm.YYYY HH:MM")', format='%d.%m.%Y %H:%M', validators=[DataRequired()])
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
            in Sekunden umgewandelt wurde, kürzer als 1800 Sekunden (also eine halbe Stunde) ist. Ist dies der 
            Fall, so wird ein Fehler ausgegeben. '''
        if (self.bis.data - von.data).total_seconds() < 1800:
            raise ValidationError('Eine Wartung dauert mindestens 30 Minuten!')
        ''' Weiters wird angenommen, dass eine Wartung höchstens 8 Stunden (28.800 Sekunden) dauert, da des
            weiteren angenommen wird, dass ein Arbeitstag 8 Stunden beträgt. Wird diese 8 Stunden Grenze
            überschritten, so wird ein Fehler ausgegeben. '''
        if (self.bis.data - von.data).total_seconds() > 28800:
            raise ValidationError('Eine Wartung darf nicht länger als 8 Stunden dauern!')

        ''' Als nächstes werden die einzelnen Wartungen von dem ausgewählten Zug ermittelt. Anschließend wird dann
            abgefragt, ob es zwischen den einzelnen Wartungen und dem eingetragenem Zeitraum eine Überschneidung
            gibt. Falls dies der Fall ist, wird ein Fehler ausgegeben.  '''
        zug = Zug.query.filter_by(nr=self.zugNr.data).first()
        for w in zug.wartung.all():
            if w.von <= von.data <= w.bis or von.data <= w.von <= w.bis < self.bis.data:
                raise ValidationError('Zu diesem Zeitraum befindet sich der Zug schon in einer Wartung! Bitte wählen Sie einen anderen Zeitraum aus')

    def validate_bis(self, bis):
        ''' Hierbei handelt es sich um eine ähnliche Abfrage wie in "validate_von", nur dass hier überprüft wird,
        ob der Endzeitpunkt der Wartung vor dem Beginnzeitpunkt der Wartung erfolgt. Auch hier wird ein Fehler
        ausgegeben, falls die Abfrage True ist. '''
        if bis.data < self.von.data:
            raise ValidationError('Das Ende der Wartung muss nach dem Beginn dieser erfolgen!')
        ''' Die folgenden drei Abfragen sind auch fast identisch wie in "validate_von". '''
        if bis.data == self.von.data:
            raise ValidationError('Beginn und Ende einer Wartung darf nicht gleich sein!')
        if (bis.data - self.von.data).total_seconds() < 1800:
            raise ValidationError('Eine Wartung dauert mindestens 30 Minuten!')
        if (bis.data - self.von.data).total_seconds() > 28800:
            raise ValidationError('Eine Wartung darf nicht länger als 8 Stunden dauern!')

        ''' Genauso wie in "validate_von" wird hier auch ermittelt, ob es eine Überschneidung des Wartungszeitraums
            des ausgewählten Zuges gibt. '''
        zug = Zug.query.filter_by(nr=self.zugNr.data).first()
        for w in zug.wartung.all():
            if w.von <= bis.data <= w.bis or self.von.data < w.von <= w.bis <= bis.data:
                raise ValidationError('Zu diesem Zeitraum befindet sich der Zug schon in einer Wartung! Bitte wählen Sie einen anderen Zeitraum aus')

class EditWartungForm(FlaskForm):
    wartungsNr = StringField('Wartungsnummer', validators=[DataRequired()])
    von = DateTimeField('Von', format='%d.%m.%Y %H:%M', validators=[DataRequired()])
    bis = DateTimeField('Bis', format='%d.%m.%Y %H:%M', validators=[DataRequired()])
    zugNr = SelectField('Zugnummer', validators=[DataRequired()])
    submit = SubmitField('Erstellen')

    def __init__(self, original_nr, original_zugNr, *args, **kwargs):
        super(EditWartungForm, self).__init__(*args, **kwargs)
        self.original_nr = original_nr
        self.original_zugNr = original_zugNr

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
        if von.data == self.bis.data:
            raise ValidationError('Beginn und Ende einer Wartung darf nicht gleich sein!')
        if (self.bis.data - von.data).total_seconds() < 1800:
            raise ValidationError('Eine Wartung dauert mindestens 30 Minuten!')
        if (self.bis.data - von.data).total_seconds() > 28800:
            raise ValidationError('Eine Wartung darf nicht länger als 8 Stunden dauern!')

        zug = Zug.query.filter_by(nr=self.zugNr.data).first()
        ''' Falls der Zug, bei dem die Wartung durchgeführt wird, geändert wird, dann sind die nächsten Schritte innerhalb der
            Abfrage genau dieselben wie im normalen Zugformular. '''
        if self.zugNr.data != self.original_zugNr:
            for w in zug.wartung.all():
                if w.von <= von.data <= w.bis or von.data <= w.von <= w.bis < self.bis.data:
                    raise ValidationError('Zu diesem Zeitraum befindet sich der Zug schon in einer Wartung! Bitte wählen Sie einen anderen Zeitraum aus')
        else:
            ''' Innerhalb der folgenden Schleife wird zunächst abgefragt, ob es sich bei der jeweiligen Wartungsnummer um die original 
                definierte Wartungsnummer (hier wird die original definierte Wartungsnummer "original_nr" genommen, da es sein kann, 
                dass auch "self.wartungsNr" sich geändert hat) handelt. Falls dies der Fall ist, dann wird die Wartung (mittels continue 
                statement) übersprungen und es wird folglich nichts darüber abgefragt, da es nicht notwendig ist, von der eigenen Wartung 
                den Wartungszeitraum abzufragen. '''
            for w in zug.wartung.all():
                if w.wartungsNr == self.original_nr:
                    continue
                if w.von <= von.data <= w.bis or von.data <= w.von <= w.bis < self.bis.data:
                    raise ValidationError('Zu diesem Zeitraum befindet sich der Zug schon in einer Wartung! Bitte wählen Sie einen anderen Zeitraum aus')

    def validate_bis(self, bis):
        if bis.data < self.von.data:
            raise ValidationError('Das Ende der Wartung muss nach dem Beginn dieser erfolgen!')
        if bis.data == self.von.data:
            raise ValidationError('Beginn und Ende einer Wartung darf nicht gleich sein!')
        if (bis.data - self.von.data).total_seconds() < 1800:
            raise ValidationError('Eine Wartung dauert mindestens 30 Minuten!')
        if (bis.data - self.von.data).total_seconds() > 28800:
            raise ValidationError('Eine Wartung darf nicht länger als 8 Stunden dauern!')

        ''' Für den folgenden Code wird auf die vorherige Validierungsmethode "validate_von" verwiesen, da dies hier analog abläuft nur
            mit dem Unterschied, dass diesmal "bis" überprüft wird. '''
        zug = Zug.query.filter_by(nr=self.zugNr.data).first()
        if self.zugNr.data != self.original_zugNr:
            for w in zug.wartung.all():
                if w.von <= bis.data <= w.bis or self.von.data < w.von <= w.bis <= bis.data:
                    raise ValidationError('Zu diesem Zeitraum befindet sich der Zug schon in einer Wartung! Bitte wählen Sie einen anderen Zeitraum aus')
        else:
            for w in zug.wartung.all():
                if w.wartungsNr == self.original_nr:
                    continue
                if w.von <= bis.data <= w.bis or self.von.data < w.von <= w.bis <= bis.data:
                    raise ValidationError('Zu diesem Zeitraum befindet sich der Zug schon in einer Wartung! Bitte wählen Sie einen anderen Zeitraum aus')