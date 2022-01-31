from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from app.models import Mitarbeiter
from app.api.errors import error_response

''' Dieses File wurde aus der Flaskdokumentation entnommen (Kapitel 23: APIs). '''

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

''' Flask-HTTPAuth ermöglicht, dass die Nutzer, die keinen Webbrowser benutzen, sich mit der Applikation verbinden 
    können bzw. auf die Applikation zugreifen können. In der ersten Methode wird hier der Mitarbeiter verifiziert. 
    Es wird also überprüft, ob das Passwort des Mitarbeiters (welches durch die Email gefiltert wird) richtig ist.
    Ist kein Mitarbeiter unter der übergebenen Email verfügbar oder ist das Passwort falsch, so wird nichts
    (None) zurückgegeben. Stimmt jedoch das Passwort des Mitarbeiters, so wird der authentifizierte Mitarbeiter
    zurückgegeben. '''
@basic_auth.verify_password
def verify_password(email, passwort):
    mitarbeiter = Mitarbeiter.query.filter_by(email=email).first()
    if mitarbeiter and mitarbeiter.check_password(passwort):
        return mitarbeiter

''' Falls die Authentifizierung fehlschlägt, so wird ein Error ausgelöst. Dieser gibt den HTTP-Statuscode "401" aus,
    da dies grundsätzlich bei Authentifizierungsfehlschlägen der Standardcode ist. '''
@basic_auth.error_handler
def basic_auth_error(status):
    return error_response(status)

''' In der folgenden Methode wird ein Token authentifiziert. Dazu wird die Methode "check_token" von der Mitarbeiterklasse
    aufgerufen und der Mitarbeiter gesucht, zu dem der Token gehört. Falls ein Mitarbeiter gefunden wird, wird dieser 
    zurückgegeben. Falls nicht, dann wird None zurückgegeben. Dies bedeutet, dass der übergebene Token vom User nicht 
    authentifizert werden konnte und dieser somit abgewiesen wird und keinen Zugriff bekommt. '''
@token_auth.verify_token
def verify_token(token):
    return Mitarbeiter.check_token(token) if token else None

''' Auch hier wird ein Error augelöst, falls eine Authentifizierung fehlschlägt. '''
@token_auth.error_handler
def token_auth_error(status):
    return error_response(status)