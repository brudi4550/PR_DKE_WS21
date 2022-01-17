from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES

def error_response(status_code, message=None):
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unbekannter Fehler')}
    if message:
        payload['message'] = message
    ''' Mit der nachfolgenden Methode "jsonify" wird ein Flask Response-Objekt zurückgegeben.
        Dieses Objekt hat den als Standard gesetzten Statuscode "200". Um diesen als Standard
        gesetzten Statuscode mit dem tatsächlichen zu überschreiben, wird nach der Erstellung
        des Response-Objekts der tatsächliche Statuscodewert zugewiesen. '''
    response = jsonify(payload)
    response.status_code = status_code
    return response

def bad_request(message):
    return error_response(400, message)
