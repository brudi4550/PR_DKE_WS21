from flask import render_template, request
from app import db
from app.errors import bp
from app.api.errors import error_response as api_error_response

''' Dieses File wurde aus der Flaskdokumentation entnommen (Kapitel 23: APIs). '''

''' Hier wird überprüft, in welchem Format der User auf die Applikation zugreift. '''
def wants_json_response():
    return request.accept_mimetypes['application/json'] >= \
           request.accept_mimetypes['text/html']

''' Durch die folgenden zwei Methoden kann bestimmt werden, wie die Errors formatiert werden.
    Greift der User auf die API Schnittstelle zu, dann wird auch ein Error im API (bzw. JSON)
    Format zurükgegeben. Greift der User nicht auf die API Schnittstelle, sondern ganz normal
    auf die Applikation zu (mittels Webbrowser), dann wird ein Error im HTML Format zurückgegeben. '''
@bp.app_errorhandler(404)
def not_found_error(error):
    if wants_json_response():
        return api_error_response(404)
    return render_template('errors/404.html'), 404

@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if wants_json_response():
        return api_error_response(500)
    return render_template('errors/500.html'), 500