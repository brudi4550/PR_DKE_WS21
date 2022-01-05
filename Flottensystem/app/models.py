from datetime import datetime
from hashlib import md5
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.declarative import AbstractConcreteBase
from sqlalchemy.orm import configure_mappers


''' Anmerkung: Bei der Beschreibung des Codes wurde darauf beachtet, den Code möglichst wenig doppelt zu beschreiben. '''

''' Da zwischen Wartungspersonal und Wartung eine "* zu *" Assoziation besteht, wird nachfolgend eine Hilfstabelle
    definiert, welches die Primärschlüssel der Klassen enthält, die durch die Assoziation verknüpft sind '''
ist_zugeteilt = db.Table('ist_zugeteilt',
                         db.Column('wartungspersonal_id', db.Integer, db.ForeignKey('wartungspersonal.mitarbeiterNr', onupdate='CASCADE', ondelete='CASCADE')),
                         db.Column('wartung_id', db.Integer, db.ForeignKey('wartung.wartungsNr', onupdate='CASCADE', ondelete='CASCADE'))
)


class Zug(db.Model):
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
    wartung = db.relationship('Wartung', backref='zug', lazy='dynamic', cascade='all, delete')
    triebwagen_nr = db.Column(db.Integer, db.ForeignKey('triebwagen.nr', onupdate='CASCADE'), unique=True, nullable=False)
    personenwagen = db.relationship('Personenwagen', backref='zug', lazy='dynamic')

    def __repr__(self):
        return '<Zugnummer: {}>'.format(self.nr)


class Mitarbeiter(UserMixin, db.Model, AbstractConcreteBase):
    mitarbeiterNr = db.Column(db.Integer, primary_key=True)
    svnr = db.Column(db.Integer, index=True, unique=True, nullable=False)
    vorname = db.Column(db.String(255), nullable=False)
    nachname = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), index=True, unique=True, nullable=False)
    passwort = db.Column(db.String(128), nullable=False)

    ''' Die Methode "__repr__" dient dazu, um zu bestimmen, wie Objekte dieser Klasse ausgegeben werden.
        Hat man z.B. in der Variable "m" eine Mitarbeiterinstanz eingespeichert, dann wird durch das 
        eingeben von "m" genau der Inhalt dieser Methode zurückgegeben, also in diesem Fall der 
        String "<Mitarbeiter x y>", wobei das x hier für einen beliebigen Vornamen und das y für einen
        beliebigen Nachnamen steht '''
    def __repr__(self):
        return '<Mitarbeiter {} {}>'.format(self.vorname, self.nachname)
        
    def get_id(self):	# Hiermit wird die get_id Methode von flask_login (UserMixin) überschieben
        return self.mitarbeiterNr

    def set_password(self, password):   # Es wird der Hashwert des eingegebenen Passworts gebildet
        self.passwort = generate_password_hash(password)

    ''' In dieser Methode wird das gehashte Passwort überprüft, genauer gesagt wird überprüft, ob der 
        übergebene Parameter (bzw. das übergebene Passwort) mit dem originialen gehashten Passwort
        übereinstimmt '''
    def check_password(self, password):
        return check_password_hash(self.passwort, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

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
        backref=db.backref('wartungspersonal', lazy='dynamic'), lazy='dynamic', cascade='all, delete')
    
    __mapper_args__ = { 'polymorphic_identity':'wartungspersonal', 'concrete':True}
    
    def __repr__(self):
        return '<Wartungspersonal {} {}>'.format(self.vorname, self.nachname)
        
class Zugpersonal(Mitarbeiter):
    __tablename__ = 'zugpersonal'
    berufsbezeichnung = db.Column(db.String(255), nullable=False)
    zugNr = db.Column(db.String(255), db.ForeignKey('zug.nr'))
    
    __mapper_args__ = { 'polymorphic_identity':'zugpersonal', 'concrete':True}
    
    def __repr__(self):
        return '<Zugpersonal {} {}>'.format(self.vorname, self.nachname)
        
class Administrator(Mitarbeiter):
    __tablename__ = 'administrator'
    
    __mapper_args__ = { 'polymorphic_identity':'administrator', 'concrete':True}
    
    def __repr__(self):
        return '<Administrator {} {}>'.format(self.vorname, self.nachname)
 

class Wagen(db.Model, AbstractConcreteBase):
    nr = db.Column(db.Integer, primary_key=True)
    spurweite = db.Column(db.Integer, index=True, nullable=False)

    def __repr__(self):
        return '<Wagen-Nr.: {}>'.format(self.nr)
        
class Triebwagen(Wagen):
    __tablename__ = 'triebwagen'
    maxZugkraft = db.Column(db.Integer, nullable=False)
    zug = db.relationship('Zug', backref='triebwagen', uselist=False, cascade='all, delete-orphan')
    
    __mapper_args__ = { 'polymorphic_identity':'triebwagen', 'concrete':True}
    
        
class Personenwagen(Wagen):
    __tablename__ = 'personenwagen'
    sitzanzahl = db.Column(db.Integer, nullable=False)
    maximalgewicht = db.Column(db.Integer, nullable=False)
    zugNr = db.Column(db.String(255), db.ForeignKey('zug.nr', onupdate='CASCADE', ondelete='CASCADE'))
    
    __mapper_args__ = { 'polymorphic_identity':'personenwagen', 'concrete':True}
        

class Wartung(db.Model):
    wartungsNr = db.Column(db.Integer, primary_key=True)
    von = db.Column(db.DateTime, index=True, nullable=False)
    bis = db.Column(db.DateTime, index=True, nullable=False)
    zugNr = db.Column(db.String(255), db.ForeignKey('zug.nr', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)

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
        Wartung nur einmal und nicht öfters vorkommt), also wäre der Ausdruck "count() == 1" genauso richtig gewesen '''
    def ist_zugeordnet(self, personal):
        return self.wartungspersonal.filter(ist_zugeteilt.c.wartungspersonal_id == personal.mitarbeiterNr)\
                   .count() > 0

    ''' In der folgenden Methode wird ein Wartungspersonal in die Assoziationstabelle der jeweiligen Wartung hinzugefügt. 
        Damit dieser nicht öfters in die Assoziationstabelle hinzugefügt wird, wird durch ein Aufruf der Methode 
        "ist_zugeordnet" überprüft, ob dieser Mitarbeiter sich schon in dieser Tabelle befindet '''
    def wartungspersonal_hinzufuegen(self, personal):
        if not self.ist_zugeordnet(personal):
            self.wartungspersonal.append(personal)

    ''' Im Unterschied zur vorherigen Methode wird in der folgenden ein Wartungspersonal entfernt. Damit dieser entfernt
        werden kann, wird überprüft (durch Aufruf der Methode "ist_zugeordnet"), ob sich dieser überhaupt in der 
        Assoziationstabelle befindet '''
    def wartungspersonal_entfernen(self, personal):
        if self.ist_zugeordnet(personal):
            self.wartungspersonal.remove(personal)

    def __repr__(self):
        return '<Wartungsnummer: {}>'.format(self.wartungsNr)

configure_mappers()
