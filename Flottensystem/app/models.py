from datetime import datetime
from hashlib import md5
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.declarative import AbstractConcreteBase
from sqlalchemy.orm import configure_mappers


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

    def set_password(self, password):
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
    
    __mapper_args__ = { 'polymorphic_identity':'wartungspersonal', 'concrete':True}
    
    def __repr__(self):
        return '<Wartungspersonal {} {}>'.format(self.vorname, self.nachname)
        
class Zugpersonal(Mitarbeiter):
    __tablename__ = 'zugpersonal'
    berufsbezeichnung = db.Column(db.String(255), nullable=False)
    
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
    
    def __repr__(self):
        return '<Wagen-Nr.: {}>'.format(self.nr)
        
class Personenwagen(Wagen):
    __tablename__ = 'personenwagen'
    sitzanzahl = db.Column(db.Integer, nullable=False)
    maximalgewicht = db.Column(db.Integer, nullable=False)
    
    __mapper_args__ = { 'polymorphic_identity':'personenwagen', 'concrete':True}
    
    def __repr__(self):
        return '<Wagen-Nr.: {}>'.format(self.nr)
        
configure_mappers()
