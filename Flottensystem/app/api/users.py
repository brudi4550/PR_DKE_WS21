from app.api import bp
from flask import jsonify, request, url_for, abort
from app.models import Mitarbeiter, Administrator, Wartungspersonal, Zugpersonal
from app import db
from app.api.errors import bad_request
from app.api.auth import token_auth

''' Für Testzwecke sollte bei den einzelnen API View Functions "@token_auth.login_required" 
    auskommentiert werden, da man sonst ohne gültigem Token bzw. ohne angemeldetem User 
    keinen Zugriff auf die API hat und dies das Testen der Funktionalitäten der API erschwert. '''

@bp.route('/Mitarbeiter', methods=['GET'])
#@token_auth.login_required
def getUsers():
    ''' Hier wird die Funktion to_collection_dict() von APIMiixin aufgerufen. Als Parameter
        nimmt dieser eine Abfrage. Hier wurde nach allen Mitarbeitern in der Datenbank abgefragt. '''
    data = Mitarbeiter.to_collection_dict(Mitarbeiter.query.all(), 'api.getUsers')
    return jsonify(data)

@bp.route('/Administrator', methods=['GET'])
#@token_auth.login_required
def getAdministrators():
    data = Administrator.to_collection_dict(Administrator.query.all(), 'api.getAdministrators')
    return jsonify(data)

@bp.route('/Zugpersonal', methods=['GET'])
#@token_auth.login_required
def getZugpersonal():
    data = Zugpersonal.to_collection_dict(Zugpersonal.query.all(), 'api.getZugpersonal')
    return jsonify(data)

@bp.route('/Wartungspersonal', methods=['GET'])
#@token_auth.login_required
def getWartungspersonal():
    data = Wartungspersonal.to_collection_dict(Wartungspersonal.query.all(), 'api.getWartungspersonal')
    return jsonify(data)


@bp.route('/Mitarbeiter/<int:id>', methods=['GET'])
#@token_auth.login_required
def getUser(id):
    return jsonify(Mitarbeiter.query.get_or_404(id).to_dict())

@bp.route('/Wartungspersonal/<int:id>/Wartungen', methods=['GET'])
#@token_auth.login_required
def getMaintenancesFromWorker(id):
    wartungspersonal = Wartungspersonal.query.get_or_404(id)
    data = wartungspersonal.to_collection_dict(wartungspersonal.wartungen, 'api.getMaintenancesFromWorker', id=id)
    return jsonify(data)

''' Bei den folgenden POST und PUT Requests wird der Token nicht auskommentiert, da dies Schreibrechte sind und hier
    die Sicherheit gewährleistet wird. Zu Testzwecken können diese aber auskommentiert werden (zusätzlich muss aber auch
    die erste Abfrage in diesen API View Functions auskommentiert werden). '''

@bp.route('/Administrator', methods=['POST'])
@token_auth.login_required
def createAdministrator():
    ''' In dieser API View Function wird zunächst überprüft, ob es sich beim current_user, der
        ein POST durchführen will, um einen Administrator handelt (da nur Administratoren
        Schreibrechte haben). Ist dies nicht der Fall, dann wird der Error "403" geworfen. '''
    if Administrator.query.filter_by(mitarbeiterNr=token_auth.current_user.mitarbeiterNr).first() is None:
        abort(403)

    data = request.get_json() or {}
    if 'mitarbeiterNr' not in data or 'svnr' not in data or 'vorname' not in data\
            or 'nachname' not in data or 'email' not in data or 'passwort' not in data:
        return bad_request('Es muss die Mitarbeiternummer, die Sozialversicherungsnummer, der Vorname, '
                           'der Nachname, die E-Mail und das Passwort angegeben werden!')
    if Mitarbeiter.query.filter_by(mitarbeiterNr=data['mitarbeiterNr']).first():
        return bad_request('Die Mitarbeiternummer ist bereits vergeben! Bitte geben Sie eine andere Mitarbeiternummer ein')
    if Mitarbeiter.query.filter_by(svnr=data['svnr']).first():
        return bad_request('Die Sozialversicherungsnummer ist bereits vergeben! Bitte geben Sie eine andere Sozialversicherungsnummer ein')
    if Mitarbeiter.query.filter_by(email=data['email']).first():
        return bad_request('Die E-Mail Adresse ist bereits vergeben! Bitte geben Sie eine andere E-Mail Adress ein')

    administrator = Administrator()
    administrator.from_dict(data, new_user=True)
    db.session.add(administrator)
    db.session.commit()

    response = jsonify(administrator.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.getUser', id=administrator.mitarbeiterNr)

    return response

@bp.route('/Zugpersonal', methods=['POST'])
@token_auth.login_required
def createZugpersonal():
    if Administrator.query.filter_by(mitarbeiterNr=token_auth.current_user.mitarbeiterNr).first() is None:
        abort(403)

    data = request.get_json() or {}
    if 'mitarbeiterNr' not in data or 'svnr' not in data or 'vorname' not in data \
            or 'nachname' not in data or 'email' not in data or 'passwort' not in data or 'berufsbezeichnung' not in data:
        return bad_request('Es muss die Mitarbeiternummer, die Sozialversicherungsnummer, der Vorname, '
                           'der Nachname, die E-Mail, das Passwort und die Berufsbezeichnung angegeben werden!')
    if Mitarbeiter.query.filter_by(mitarbeiterNr=data['mitarbeiterNr']).first():
        return bad_request('Die Mitarbeiternummer ist bereits vergeben! Bitte geben Sie eine andere Mitarbeiternummer ein')
    if Mitarbeiter.query.filter_by(svnr=data['svnr']).first():
        return bad_request('Die Sozialversicherungsnummer ist bereits vergeben! Bitte geben Sie eine andere Sozialversicherungsnummer ein')
    if Mitarbeiter.query.filter_by(email=data['email']).first():
        return bad_request('Die E-Mail Adresse ist bereits vergeben! Bitte geben Sie eine andere E-Mail Adress ein')

    zugpersonal = Zugpersonal()
    zugpersonal.from_dict(data, new_user=True)
    db.session.add(zugpersonal)
    db.session.commit()

    response = jsonify(zugpersonal.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.getUser', id=zugpersonal.mitarbeiterNr)

    return response

''' Anmerkung: Es wurde keine API View Function zum erstellen eines Wartungspersonalmitarbeiters erstellt, da
    ich nicht weiß wie man die Wartungen in der API angeben kann (da diese eine "*" Assoziation haben). '''


@bp.route('/Administrator/<int:id>', methods=['PUT'])
@token_auth.login_required
def updateAdministrator(id):
    ''' Auch hier wird (wie in der API View Function "createAdministrator") zunächst überprüft, ob es sich
        beim current_user um einen Administrator handelt. '''
    if Administrator.query.filter_by(mitarbeiterNr=token_auth.current_user.mitarbeiterNr).first() is None:
        abort(403)

    administrator = Administrator.query.get_or_404(id)
    ''' Zusätzlich wird überprüft, ob der Administrator einen anderen Administrator bearbeiten will. Ist dies der Fall,
        dann wird ein Fehler ausgegeben'''
    if administrator != Administrator.query.filter_by(mitarbeiterNr=token_auth.current_user.mitarbeiterNr).first():
        return bad_request('Ein Administrator kann keine anderen Administratoren bearbeiten, sondern nur sich selbst!')

    data = request.get_json() or {}
    ''' In der folgenden Abfrage wird überprüft, ob die Mitarbeiternummer des Administrators geändert wurde. Falls 
        dies geändert wurde und die geänderte Mitarbeiternummer in der Datenbank enthalten ist, wird ein Error 
        ausgelöst. '''
    if 'mitarbeiterNr' in data and data['mitarbeiterNr'] != administrator.mitarbeiterNr and \
            Mitarbeiter.query.filter_by(mitarbeiterNr=data['mitarbeiterNr']).first():
        return bad_request('Die einegegebene Mitarbeiternummer ist bereits vergeben! Bitte geben Sie eine andere Mitarbeiternummer ein')

    ''' Analog zur Mitarbeiternummer wird die selbe Abfrage bei der Sozialversicherungsnummer (und auch für
        die E-Mail Adresse) durchgeführt. '''
    if 'svnr' in data and data['svnr'] != administrator.svnr and \
            Mitarbeiter.query.filter_by(svnr=data['svnr']).first():
        return bad_request('Die einegegebene Sozialversicherungsnummer ist bereits vergeben! Bitte geben Sie eine andere Sozialversicherungsnummer ein')

    if 'email' in data and data['email'] != administrator.email and \
            Mitarbeiter.query.filter_by(email=data['email']).first():
        return bad_request('Die einegegebene E-Mail Adresse ist bereits vergeben! Bitte geben Sie eine andere E-Mail Adresse ein')

    administrator.from_dict(data, new_user=False)
    db.session.commit()

    return jsonify(administrator.to_dict())

@bp.route('/Zugpersonal/<int:id>', methods=['PUT'])
@token_auth.login_required
def updateZugpersonal(id):
    ''' Auch hier wird (wie in der API View Function "createAdministrator") zunächst überprüft, ob es sich
        beim current_user um einen Administrator handelt. '''
    if Administrator.query.filter_by(mitarbeiterNr=token_auth.current_user.mitarbeiterNr).first() is None:
        abort(403)

    zugpersonal = Zugpersonal.query.get_or_404(id)
    data = request.get_json() or {}
    if 'mitarbeiterNr' in data and data['mitarbeiterNr'] != zugpersonal.mitarbeiterNr and \
            Mitarbeiter.query.filter_by(mitarbeiterNr=data['mitarbeiterNr']).first():
        return bad_request('Die einegegebene Mitarbeiternummer ist bereits vergeben! Bitte geben Sie eine andere Mitarbeiternummer ein')

    ''' Analog zur Mitarbeiternummer wird die selbe Abfrage bei der Sozialversicherungsnummer (und auch für
        die E-Mail Adresse) durchgeführt. '''
    if 'svnr' in data and data['svnr'] != zugpersonal.svnr and \
            Mitarbeiter.query.filter_by(svnr=data['svnr']).first():
        return bad_request('Die einegegebene Sozialversicherungsnummer ist bereits vergeben! Bitte geben Sie eine andere Sozialversicherungsnummer ein')

    if 'email' in data and data['email'] != zugpersonal.email and \
            Mitarbeiter.query.filter_by(email=data['email']).first():
        return bad_request('Die einegegebene E-Mail Adresse ist bereits vergeben! Bitte geben Sie eine andere E-Mail Adresse ein')

    zugpersonal.from_dict(data, new_user=False)
    db.session.commit()

    return jsonify(zugpersonal.to_dict())