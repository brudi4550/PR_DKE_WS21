from datetime import datetime
from hashlib import md5
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.declarative import AbstractConcreteBase
from sqlalchemy.orm import configure_mappers


''' Da zwischen Wartungspersonal und Wartung eine "* zu *" Assoziation besteht, wird nachfolgend eine Hilfstabelle
    definiert, welches die Primärschlüssel der Klassen enthält, die durch die Assoziation verknüpft sind '''
ist_zugeteilt = db.Table('ist_zugeteilt',
                         db.Column('wartungspersonal_id', db.Integer, db.ForeignKey('wartungspersonal.mitarbeiterNr')),
                         db.Column('wartung_id', db.Integer, db.ForeignKey('wartung.wartungsNr'))
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
    wartung = db.relationship('Wartung', backref='zug', lazy='dynamic')

    def __repr__(self):
        return '<Zugnummer: {}>'.format(self.nr)


class Mitarbeiter(UserMixin, db.Model, AbstractConcreteBase):
    mitarbeiterNr = db.Column(db.Integer, primary_key=True)
    svnr = db.Column(db.Integer, index=True, unique=True, nullable=False)
    vorname = db.Column(db.String(255), nullable=False)
    nachname = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), index=True, unique=True, nullable=False)
    passwort = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<Mitarbeiter {} {}>'.format(self.vorname, self.nachname)
        
    def get_id(self):	# Hiermit wird die get_id Methode von flask_login überschieben
        return self.mitarbeiterNr

    def set_password(self, password):   # Es wird der Hashwert des eingegebenen Passworts gebildet
        self.passwort = generate_password_hash(password)

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
        backref=db.backref('wartungspersonal', lazy='dynamic'), lazy='dynamic')
    
    __mapper_args__ = { 'polymorphic_identity':'wartungspersonal', 'concrete':True}
    
    def __repr__(self):
        return '<Wartungspersonal {} {}>'.format(self.vorname, self.nachname)
        
class Zugpersonal(Mitarbeiter):
    __tablename__ = 'zugpersonal'
    berufsbezeichnung = db.Column(db.String(255), nullable=False)
    zug_nr = db.Column(db.String(255), db.ForeignKey('zug.nr'), nullable=False)
    
    __mapper_args__ = { 'polymorphic_identity':'zugpersonal', 'concrete':True}
    
    def __repr__(self):
        return '<Zugpersonal {} {}>'.format(self.vorname, self.nachname)
        
class Administrator(Mitarbeiter):
    __tablename__ = 'administrator'
    
    __mapper_args__ = { 'polymorphic_identity':'administrator', 'concrete':True}
    
    def __repr__(self):
        return '<Administrator {} {}>'.format(self.vorname, self.nachname)
        
configure_mappers()


class Wagen(db.Model, AbstractConcreteBase):
    nr = db.Column(db.Integer, primary_key=True)
    spurweite = db.Column(db.Integer, index=True, nullable=False)

    def __repr__(self):
        return '<Wagen-Nr.: {}>'.format(self.nr)
        
class Triebwagen(Wagen):
    __tablename__ = 'triebwagen'
    maxZugkraft = db.Column(db.Integer, nullable=False)
    
    __mapper_args__ = { 'polymorphic_identity':'triebwagen', 'concrete':True}
    
    def __repr__(self): # ANSCHAUEN !!!!!!!!!!!!
        return '<Wagen-Nr.: {}>'.format(self.nr)
        
class Personenwagen(Wagen):
    __tablename__ = 'personenwagen'
    sitzanzahl = db.Column(db.Integer, nullable=False)
    maximalgewicht = db.Column(db.Integer, nullable=False)
    
    __mapper_args__ = { 'polymorphic_identity':'personenwagen', 'concrete':True}
    
    def __repr__(self): # ANSCHAUEN !!!!!!!!!!!!
        return '<Wagen-Nr.: {}>'.format(self.nr)
        
configure_mappers()


class Wartung(db.Model):
    wartungsNr = db.Column(db.Integer, primary_key=True)
    von = db.Column(db.DateTime, index=True, nullable=False)
    bis = db.Column(db.DateTime, index=True, nullable=False)
    zug_nr = db.Column(db.String(255), db.ForeignKey('zug.nr'), nullable=False)

    def __repr__(self):
        return '<Wartungsnummer: {}>'.format(self.wartungsNr)
        

