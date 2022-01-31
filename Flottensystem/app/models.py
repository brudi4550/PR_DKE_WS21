from datetime import datetime, timedelta
from hashlib import md5
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.declarative import AbstractConcreteBase
from sqlalchemy.orm import configure_mappers
from flask import url_for
import base64
import os


''' Anmerkung: Bei der Beschreibung des Codes wurde darauf beachtet, den Code möglichst wenig doppelt zu beschreiben. '''

''' In der folgenden Klasse wird eine Methode definiert, die eine Repräsentation einer Kollektion von einem Objekt
    zurückgibt, welche die API benötigt. Die Daten, die zurückgegeben werden, werden in einem Dictionary eingespeichert.
    Klassen, die diese APIMixin Klasse benötigen, müssen schließlich von dieser erben. '''
class APIMixin(object):
    @staticmethod
    def to_collection_dict(query, endpoint, **kwargs):
        data = {
            'items': [item.to_dict() for item in query],
            '_links': {
                'self': url_for(endpoint, **kwargs)
            }
        }
        return data

''' Da zwischen Wartungspersonal und Wartung eine "* zu *" Assoziation besteht, wird nachfolgend eine Hilfstabelle
    definiert, welches die Primärschlüssel der Klassen enthält, die durch die Assoziation verknüpft sind. '''
ist_zugeteilt = db.Table('ist_zugeteilt',
                         db.Column('wartungspersonal_id', db.Integer, db.ForeignKey('wartungspersonal.mitarbeiterNr', onupdate='CASCADE', ondelete='CASCADE')),
                         db.Column('wartung_id', db.Integer, db.ForeignKey('wartung.wartungsNr', onupdate='CASCADE', ondelete='CASCADE'))
)


class Zug(APIMixin, db.Model):
    nr = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    ''' Nachfolgend wird ein Feld für die Assoziation zwischen Zug und Zugpersonal definiert. Da es sich hier um eine 
        "1 zu *" Assoziation handelt, wird "db.relationship()" in der "1" Seite definiert. Dies vereinfacht den Zugriff
        auf die "*" Seite der Assoziation. Beim ersten Parameter handelt es sich um den Namen der Klasse von der "*" 
        Seite der Assoziation. Durch backref wird ein Feld angegeben, welches der "*" Seite verfügbar gemacht wird. D.h.,
        dass man dadurch (genauer gesagt, durch Zugpersonal.zug) von der "*" Seite auf das Objekt der "1" Seite zugreifen 
        kann. Durch "lazy" wird definiert, wie die Datenbankabfrage ausgeführt wird. Hier wird mit dynamic festgelegt, 
        dass die Abrage erst dann ausgeführt wird, wenn diese angefordert wird. '''
    zugpersonal = db.relationship('Zugpersonal', backref='zug', lazy='dynamic')
    ''' Der Cascade Constraint "all, delete" in der folgenden Variable bedeutet, dass alle Instanzen von dieser Variable
        gelöscht werden, wenn ein Zug gelöscht wird. Das bedeutet genauer gesagt, dass, wenn ein Zug gelöscht wird, alle
        dem Zug zugewiesenen Wartungen gelöscht werden. '''
    wartung = db.relationship('Wartung', backref='zug', lazy='dynamic', cascade='all, delete')
    triebwagen_nr = db.Column(db.Integer, db.ForeignKey('triebwagen.nr', onupdate='CASCADE', ondelete='CASCADE'), unique=True, nullable=False)
    personenwagen = db.relationship('Personenwagen', backref='zug', lazy='dynamic')

    def __repr__(self):
        return '<Zugnummer: {}>'.format(self.nr)

    ''' Mit der "to_dict" Methode wird angegeben, wie die Daten dann in der API angezeigt werden bzw. welche Daten
        angezeigt werden. Also werden die Daten eines Zugobjekts in eine Python repräsentation umgewandelt, welche
        anschließend in ein JSON Format konvertiert werden. '''
    def to_dict(self):
        data = {
            'nr': self.nr,
            'name': self.name,
            'triebwagen_nr': self.triebwagen_nr,
            '_links': {
                'self': url_for('api.getTrain', id=self.nr),
                'wartungen': url_for('api.getMaintenancesFromTrain', id=self.nr),
                'personenwagen': url_for('api.getPersonenwaggonsFromTrain', id=self.nr)
            }
        }
        return data

    ''' "from_dict" ist das Umgekehrte zur oberen Methode. Hier werden die Daten vom JSON Format zu einem Zug Objekt 
        umgewandelt. '''
    def from_dict(self, data):
        for field in ['nr', 'name', 'triebwagen_nr']:
            if field in data:
                setattr(self, field, data[field])



''' Für eine Erklärung der Auswahl dieser Klassenvererbungsart (also "AbstractConcreteBase") wird auf die
    Problembeschreibung von der Abgabe vom technischen Durchstrich (Abgabedatum: 17.12.2021) verwiesen, da
    dort genau erklärt wird, wie bei der Auswahl der Vererbungsart vorgegangen wurde. '''
class Mitarbeiter(UserMixin, APIMixin, db.Model, AbstractConcreteBase):
    mitarbeiterNr = db.Column(db.Integer, primary_key=True)
    svnr = db.Column(db.Integer, index=True, unique=True, nullable=False)
    vorname = db.Column(db.String(255), nullable=False)
    nachname = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), index=True, unique=True, nullable=False)
    passwort = db.Column(db.String(128), nullable=False)
    ''' Die nachfolgenden Felder werden generiert, damit der User ein Token zugewiesen bekommen kann. Diser Token 
        wird für die Authentifizierung in der API benötigt, da ein Client (wenn dieser mit der API interagieren will)
        sich bei der API mittels einem Token authentifizieren muss. Dieser Token steht dem User nur temporär zur 
        Verfügung, wobei "tokenDauer" die Zeit angibt, in der das Token gültig ist (bzw. gibt es an, wann die 
        Gültigkeit des Tokens verfällt) '''
    token = db.Column(db.String(32), index=True, unique=True)
    tokenDauer = db.Column(db.DateTime)

    ''' Die Methode "__repr__" dient dazu, um zu bestimmen, wie Objekte dieser Klasse ausgegeben werden.
        Hat man z.B. in der Variable "m" eine Mitarbeiterinstanz eingespeichert, dann wird durch das 
        eingeben von "m" genau der Inhalt dieser Methode zurückgegeben, also in diesem Fall der 
        String "<Mitarbeiter x y>", wobei das x hier für einen beliebigen Vornamen und das y für einen
        beliebigen Nachnamen steht '''
    def __repr__(self):
        return '<Mitarbeiter {} {}>'.format(self.vorname, self.nachname)
        
    def get_id(self):	# Hiermit wird die get_id Methode von "flask_login" (UserMixin) überschieben
        return self.mitarbeiterNr

    def set_password(self, password):   # Es wird der Hashwert des eingegebenen Passworts gebildet
        self.passwort = generate_password_hash(password)

    ''' In dieser Methode wird das gehashte Passwort überprüft, genauer gesagt wird überprüft, ob der 
        übergebene Parameter (bzw. das übergebene Passwort) mit dem originialen gehashten Passwort
        übereinstimmt '''
    def check_password(self, password):
        return check_password_hash(self.passwort, password)

    ''' Die folgenden drei Methoden wurden wurden aus der Flaskdokumentation entnommen (Kapitel 23: APIs). 
        Die erste Methode ist sozusagen ein Getter (man holt sich hier den Token, genauere Beschreibung in
        der Methode). '''
    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        ''' Zu allererst wird überprüft, ob ein Token existiert und die Gültigkeitsdauer des Tokens über einer
            Minute ist. Wenn dies der Fall ist, dann wird der Token zurückgegeben. '''
        if self.token and self.tokenDauer > now + timedelta(seconds=60):
            return self.token

        ''' Existiert kein Token oder ist die Gültigkeitsdauer des Tokens nicht länger als 60 Sekunden (1 Minute),
            dann wird ein neuer Token generiert. Die Dauer des Tokens wird mit dem übergebenen Parameter "expires_in"
            spezifiziert, d.h. dass grundsätzlich die Gültigkeit des Tokens 3600 Sekunden (also eine Stunde) hält. '''
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.tokenDauer = now + timedelta(seconds=expires_in)
        db.session.add(self)

        return self.token

    ''' Als nächstes wird in der folgenden Methode der Token des Users entzogen. Dies wird gemacht, indem man die
        Gültigkeitsdauer des Tokens (also die Variable "tokenDauer") verfallen lässt, d.h. es wird die jetzige 
        Zeit ermittelt ("datetime.utcnow()") und von dieser Zeit wird eine Sekunde abgezogen, welches anschließend
        der Variable "tokenDauer" zugewiesen wird. Somit ist dann die Gültigkeit des Tokens vor einer Sekunde 
        verfallen. '''
    def revoke_token(self):
        self.tokenDauer = datetime.utcnow() - timedelta(seconds=1)

    ''' In der folgenden Methode wird der Token eines bestimmten Mitarbeiters überprüft. Zunächst wird überprüft,
        ob der Mitarbeiter existiert (also ob es einen Mitarbeiter in der Datenbank gibt, der den im Parameter 
        übergebenen Token besitzt), gefolgt von einer Überprüfung der Tokendauer (also ob der Token des Mitarbeiters
        noch gültig ist). Trifft mindestens eines der beiden Bedingungen zu, dann wird nichts (None) zurückgegeben. 
        Falls diese if-Abfrage jedoch nicht aufgerufen wird, so wird der bestimmte Mitarbeiter zurückgegeben. '''
    @staticmethod
    def check_token(token):
        mitarbeiter = Mitarbeiter.query.filter_by(token=token).first()
        if mitarbeiter is None or mitarbeiter.tokenDauer < datetime.utcnow():
            return None
        return mitarbeiter

@login.user_loader
def load_user(id):
    return Mitarbeiter.query.get(int(id))

class Wartungspersonal(Mitarbeiter):
    __tablename__ = 'wartungspersonal'
    ''' Mit db.relationship wird die Assoziation mit der Klasse "Wartung" definiert. Beim ersten Ausdruck wird
        definiert, mit welcher Klasse die Assoziation stattfindet (in dem Fall "Wartung"). Als nächstes wird 
        durch "secondary" die Assoziationstabelle (bzw. Hilfstabelle) referenziert, welche für die Assoziation
        zwischen Wartungspersonal und Wartung benutzt wird. Durch backref kann auf diese Assoziation von der 
        anderen Seite (also von "Wartung") zugegriffen werden. D.h., dass man durch Wartung.wartungspersonal
        zugriff auf diese Assoziation hat. Durch "lazy" wird definiert, wie die Datenbankabfrage ausgeführt 
        wird. Hier wird mit dynamic festgelegt, dass die Abrage erst dann ausgeführt wird, wenn diese 
        angefordert wird. '''
    wartungen = db.relationship(
        'Wartung', secondary=ist_zugeteilt,
        backref=db.backref('wartungspersonal', lazy='dynamic'), lazy='dynamic')

    ''' Die folgende Zuweisung "__mapper_args__" ist für eine Concrete Klassenvererbungshierarchie notwendig, da 
        damit die Concrete Vererbung eingeschaltet bzw. möglich gemacht wird. '''
    __mapper_args__ = { 'polymorphic_identity':'wartungspersonal', 'concrete':True}
    
    def __repr__(self):
        return '<Wartungspersonal {} {}>'.format(self.vorname, self.nachname)

    def to_dict(self):
        data = {
            'mitarbeiterNr': self.mitarbeiterNr,
            'svnr': self.svnr,
            'vorname': self.vorname,
            'nachname': self.nachname,
            'email': self.email,
            '_links': {
                'self': url_for('api.getUser', id=self.mitarbeiterNr),
                'wartungen': url_for('api.getMaintenancesFromWorker', id=self.mitarbeiterNr)
            }
        }
        return data

    def from_dict(self, data, new_user=False):
        for field in ['mitarbeiterNr', 'svnr', 'vorname', 'nachname', 'email']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'passwort' in data:
            self.set_password(data['passwort'])
        
class Zugpersonal(Mitarbeiter):
    __tablename__ = 'zugpersonal'
    berufsbezeichnung = db.Column(db.String(255), nullable=False)
    ''' Mit "SET NULL" wird die zugewiesene Zugnummer auf Null gesetzt, falls die Zugpersonalinstanz gelöscht wird. '''
    zugNr = db.Column(db.String(255), db.ForeignKey('zug.nr', onupdate="CASCADE", ondelete="SET NULL"))
    
    __mapper_args__ = { 'polymorphic_identity':'zugpersonal', 'concrete':True}
    
    def __repr__(self):
        return '<Zugpersonal {} {}>'.format(self.vorname, self.nachname)

    def to_dict(self):
        data = {
            'mitarbeiterNr': self.mitarbeiterNr,
            'svnr': self.svnr,
            'vorname': self.vorname,
            'nachname': self.nachname,
            'email': self.email,
            'berufsbezeichnung': self.berufsbezeichnung,
            'zugNr': self.zugNr,
            '_links': {
                'self': url_for('api.getUser', id=self.mitarbeiterNr)
            }
        }
        return data

    def from_dict(self, data, new_user=False):
        for field in ['mitarbeiterNr', 'svnr', 'vorname', 'nachname', 'email', 'berufsbezeichnung', 'zugNr']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'passwort' in data:
            self.set_password(data['passwort'])
        
class Administrator(Mitarbeiter):
    __tablename__ = 'administrator'
    
    __mapper_args__ = { 'polymorphic_identity':'administrator', 'concrete':True}
    
    def __repr__(self):
        return '<Administrator {} {}>'.format(self.vorname, self.nachname)

    def to_dict(self):
        data = {
            'mitarbeiterNr': self.mitarbeiterNr,
            'svnr': self.svnr,
            'vorname': self.vorname,
            'nachname': self.nachname,
            'email': self.email,
            '_links': {
                'self': url_for('api.getUser', id=self.mitarbeiterNr)
            }
        }
        return data

    def from_dict(self, data, new_user=False):
        for field in ['mitarbeiterNr', 'svnr', 'vorname', 'nachname', 'email']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'passwort' in data:
            self.set_password(data['passwort'])
 

class Wagen(APIMixin, db.Model, AbstractConcreteBase):
    nr = db.Column(db.Integer, primary_key=True)
    spurweite = db.Column(db.Integer, index=True, nullable=False)

    def __repr__(self):
        return '<Wagen-Nr.: {}>'.format(self.nr)
        
class Triebwagen(Wagen):
    __tablename__ = 'triebwagen'
    maxZugkraft = db.Column(db.Integer, nullable=False)
    ''' Durch "uselist=False" wird die "1 zu 1"-Assoziation zwischen Triebwaggons und Zügen sichergestellt.
        D.h. dass man hier der Variable "zug" nur ein Wert zuweisen kann (und nicht eine Liste von Werten,
        wie es ursprünglich der Fall ist). Das Setzen von False in der "uselist" Variable führt zu einer
        weiteren Einschränkung: Hat die Variable "zug" einen Wert bereits zugewiesen bekommen und man fügt
        diesem noch einen Wert hinzu, dann wird der alte Wert überschrieben. '''
    zug = db.relationship('Zug', backref='triebwagen', uselist=False, cascade='all, delete')
    
    __mapper_args__ = { 'polymorphic_identity':'triebwagen', 'concrete':True}

    def to_dict(self):
        data = {
            'nr': self.nr,
            'spurweite': self.spurweite,
            'maxZugkraft': self.maxZugkraft,
            '_links': {
                'self': url_for('api.getWaggon', id=self.nr),
            }
        }
        return data

    def from_dict(self, data):
        for field in ['nr', 'spurweite', 'maxZugkraft']:
            if field in data:
                setattr(self, field, data[field])
    
        
class Personenwagen(Wagen):
    __tablename__ = 'personenwagen'
    sitzanzahl = db.Column(db.Integer, nullable=False)
    maximalgewicht = db.Column(db.Integer, nullable=False)
    zugNr = db.Column(db.String(255), db.ForeignKey('zug.nr', onupdate='CASCADE', ondelete='CASCADE'))
    
    __mapper_args__ = { 'polymorphic_identity':'personenwagen', 'concrete':True}

    def to_dict(self):
        data = {
            'nr': self.nr,
            'spurweite': self.spurweite,
            'sitzanzahl': self.sitzanzahl,
            'maximalgewicht': self.maximalgewicht,
            '_links': {
                'self': url_for('api.getWaggon', id=self.nr)
                #'wartung': url_for('api.')
            }
        }
        return data

    def from_dict(self, data):
        for field in ['nr', 'spurweite', 'maxZugkraft']:
            if field in data:
                setattr(self, field, data[field])
        

class Wartung(APIMixin, db.Model):
    wartungsNr = db.Column(db.Integer, primary_key=True)
    von = db.Column(db.DateTime, nullable=False)
    bis = db.Column(db.DateTime, nullable=False)
    zugNr = db.Column(db.String(255), db.ForeignKey('zug.nr', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return '<Wartungsnummer: {}>'.format(self.wartungsNr)

    ''' In der folgenden Methode werden die Mitarbeiter der Klasse "Wartungspersonal" zurückgegeben, die sich in 
        der Assoziationstabelle der jeweiligen Wartung befinden (die also eine Wartung eines bestimmten Zuges
        durchführen). Dabei wird im ersten Ausdruck ein Join durchgeführt, d.h., dass die Tabelle "Wartungspersonal"
        mit der Assoziationstabelle "ist_zugeteilt" gejoint wird. Also entfallen hier schon alle Wartungspersonal-
        instanzen, die noch keine Wartung durchgeführt haben bzw. sich nicht in der Assoziationstabelle befinden.
        Als nächstes wird durch den Ausdruck "filter" alle Instanzen rausgefiltert, die nicht der jeweiligen
        Wartungsnummer zugehören. Es werden also durch den "filter" Ausdruck nur jene Instanzen aus der Assoziations-
        tabelle geholt, die auch zu der jeweiligen Wartung gehören. '''
    def zugeordnetes_wartungspersonal(self):
        return Wartungspersonal.query.join(
            ist_zugeteilt, (ist_zugeteilt.c.wartungspersonal_id == Wartungspersonal.mitarbeiterNr)).filter(
            ist_zugeteilt.c.wartung_id == self.wartungsNr)

    ''' In dieser Methode wird überprüft, ob der übergebene Mitarbeiter in der jeweiligen Wartung eingeteilt ist.
        Durch "self.wartungspersonal" wird auf die Assoziationstabelle der jeweiligen Wartung zugegriffen. Mit
        "filter" wird in dieser Assoziationstabelle abgefragt, ob der jeweilige Mitarbeiter dort vorhanden ist.
        Durch "count()" wird gezählt, wie oft dieser Mitarbeiter in der Assoziationstabelle der jeweiligen 
        Wartung vorhanden ist, welches maximal den Wert 1 annehmen kann (da ein Mitarbeiter in einer jeweiligen
        Wartung nur einmal und nicht öfters vorkommt), also wäre der Ausdruck "count() == 1" genauso richtig gewesen. '''
    def ist_zugeordnet(self, personal):
        return self.wartungspersonal.filter(ist_zugeteilt.c.wartungspersonal_id == personal.mitarbeiterNr)\
                   .count() > 0

    ''' In der folgenden Methode wird ein Wartungspersonal in die Assoziationstabelle der jeweiligen Wartung hinzugefügt. 
        Damit dieser nicht öfters in die Assoziationstabelle hinzugefügt wird, wird durch ein Aufruf der Methode 
        "ist_zugeordnet" überprüft, ob dieser Mitarbeiter sich schon in dieser Tabelle befindet. '''
    def wartungspersonal_hinzufuegen(self, personal):
        if not self.ist_zugeordnet(personal):
            self.wartungspersonal.append(personal)

    ''' Im Unterschied zur vorherigen Methode wird in der folgenden ein Wartungspersonal entfernt. Damit dieser entfernt
        werden kann, wird überprüft (durch Aufruf der Methode "ist_zugeordnet"), ob sich dieser überhaupt in der 
        Assoziationstabelle befindet. '''
    def wartungspersonal_entfernen(self, personal):
        if self.ist_zugeordnet(personal):
            self.wartungspersonal.remove(personal)

    def to_dict(self):
        data = {
            'wartungsNr': self.wartungsNr,
            'von': self.von,
            'bis': self.bis,
            'zugNr': self.zugNr,
            '_links': {
                'self': url_for('api.getMaintenance', id=self.wartungsNr)
            }
        }
        return data

    def from_dict(self, data):
        for field in ['wartungsNr', 'von', 'bis', 'zugNr']:
            if field in data:
                setattr(self, field, data[field])

''' Der nachfolgende Ausdruck wird bei normaler Klassenvererbung (z.B. ConcreteBase) automatisch generiert. Da in unserem 
    Fall "AbstractConcreteBase" für die Klassenvererbung angewandt wird, ist eine explizite Angabe notwendig, womit dann 
    durch alle konfigurierten Subklassen gescannt und das mapping (welches eine Abfrage aller Subklassen auf einmal ermöglicht)
    eingerichtet wird. Dies ermöglicht dann eine Abfrage über alle Subklassen hinweg (also man kann dann bei der abstrakten 
    Base-Klasse Abfragen durchführen und dieser führt dann anschließend eine Abfrage über all seine Subklassen hinweg). '''
configure_mappers()
