from flask import jsonify
from app import db
from app.api import bp
from app.api.auth import basic_auth, token_auth

''' Dieses File wurde aus der Flaskdokumentation entnommen (Kapitel 23: APIs). '''

''' In der folgenden View Function wird mit "...login_required" vom User verlangt, dass dieser angemeldet ist,
    sonst hat dieser keinen Zugriff auf diese View Function. Somit wird dann die "get_token()" Methode von
    dem momentan angemeldeten User aufgerufen und es wird somit ein Token generiert und in der Datenbank
    persistiert. '''
@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    token = basic_auth.current_user().get_token()
    db.session.commit()
    return jsonify({'token': token})

''' Als nächstes wird die "revoke_token()" Methode von dem momentan angemeldeten User aufgerufen, wodurch
    dessen Token entzogen wird. Dies wird anschließend in der Datenbank persistiert. Am Ende wird ein leerer
    String und ein Statuscode "204" zurückgegeben'''
@bp.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    token_auth.current_user().revoke_token()
    db.session.commit()
    return '', 204
