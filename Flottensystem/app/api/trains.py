from app.api import bp
from flask import jsonify, request, url_for, abort
from app.models import Zug, Triebwagen, Administrator
from app import db
from app.api.errors import bad_request
from app.api.auth import token_auth

''' Für Testzwecke sollte bei den einzelnen API View Functions "@token_auth.login_required" 
    auskommentiert werden, da man sonst ohne gültigem Token bzw. ohne angemeldetem User 
    keinen Zugriff auf die API hat und dies das Testen der Funktionalitäten der API erschwert.
    Anmerkung: Die "POST" und "PUT" API View Function ist nicht ganz richtig, da man noch die
    Personenwaggons angeben sollte. Da dies aber eine "*" Assoziation ist, weiß ich nicht, 
    wie das gemacht wird (für nähere Infos, siehe Problembeschreibung der Projektabgabe). '''

@bp.route('/Züge', methods=['GET'])
#@token_auth.login_required
def getTrains():
    ''' Hier wird die Funktion to_collection_dict() von APIMiixin aufgerufen. Als Parameter
        nimmt dieser eine Abfrage. Hier wurde nach allen Zügen in der Datenbank abgefragt. '''
    data = Zug.to_collection_dict(Zug.query.all(), 'api.getTrains')
    return jsonify(data)

''' Ein Problem, welches bei ID's auftaucht, welche Strings sind, ist, dass, wenn
    diese ID einen Abstand enthält (z.B.: "RJ 40"), bei der Eingabe der URL
    beim Safari Browser eine Googlesuche gestartet wird. Dieses Problem tritt
    beim Firefox Browser nicht auf. '''
@bp.route('/Züge/<string:id>', methods=['GET'])
#@token_auth.login_required
def getTrain(id):
    return jsonify(Zug.query.get_or_404(id).to_dict())

@bp.route('/Züge/<string:id>/Wartungen', methods=['GET'])
#@token_auth.login_required
def getMaintenancesFromTrain(id):
    zug = Zug.query.get_or_404(id)
    data = Zug.to_collection_dict(zug.wartung, 'api.getMaintenancesFromTrain', id=id)
    return jsonify(data)

@bp.route('/Züge/<string:id>/Personenwaggons', methods=['GET'])
#@token_auth.login_required
def getPersonenwaggonsFromTrain(id):
    zug = Zug.query.get_or_404(id)
    data = Zug.to_collection_dict(zug.personenwagen, 'api.getPersonenwaggonsFromTrain', id=id)
    return jsonify(data)

@bp.route('/Züge', methods=['POST'])
@token_auth.login_required
def createTrain():
    ''' In dieser API View Function wird zunächst überprüft, ob es sich beim current_user, der
        ein POST durchführen will, um einen Administrator handelt (da nur Administratoren
        Schreibrechte haben). Ist dies nicht der Fall, dann wird der Error "403" geworfen. '''
    if Administrator.query.filter_by(mitarbeiterNr=token_auth.current_user.mitarbeiterNr).first() is None:
        abort(403)

    data = request.get_json() or {}
    if 'nr' not in data or 'name' not in data or 'triebwagen_nr' not in data:
        return bad_request('Es muss der Zugname, die Zugnummer, die Triebwagennummer und '
                           'die zugeteilten Personenwaggons angegeben werden')
    if Zug.query.filter_by(nr=data['nr']).first():
        return bad_request('Die Zugnummer ist bereits vergeben! Bitte geben Sie eine andere Zugnunmmer ein')
    if Triebwagen.query.filter_by(nr=data['triebwagen_nr']).first().zug:
        return bad_request('Der eingegebene Triebwagen wurde bereits einem Zug zugeordnet, bitte geben Sie einen anderen Triebwagen ein')

    zug = Zug()
    zug.from_dict(data)
    db.session.add(zug)
    db.session.commit()

    response = jsonify(zug.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.getTrain', id=zug.nr)

    return response


@bp.route('/Züge/<string:id>', methods=['PUT'])
@token_auth.login_required
def updateTrain(id):
    ''' Auch hier wird (wie in der API View Function "createTrain") zunächst überprüft, ob es sich
        beim current_user um einen Administrator handelt. '''
    if Administrator.query.filter_by(mitarbeiterNr=token_auth.current_user.mitarbeiterNr).first() is None:
        abort(403)

    zug = Zug.query.get_or_404(id)
    data = request.get_json() or {}
    ''' In der folgenden Abfrage wird überprüft, ob die Zugnummer des bestimmten Zuges geändert wurde. Falls 
        dies geändert wurde und die geänderte Zugnummer in der Datenbank enthalten ist, wird ein Error 
        ausgelöst. '''
    if 'nr' in data and data['nr'] != zug.nr and Zug.query.filter_by(nr=data['nr']).first():
        return bad_request('Die einegegebene Zugnummer ist bereits vergeben! Bitte geben Sie eine andere Zugnummer ein')

    ''' Als nächstes wird überprüft, ob der Triebwagen geändert wurde und falls dies der Fall ist wird weiters überprüft,
        ob der Triebwagen, auf welchen man umändern möchte, bereits einem Zug zugeordnet ist. Ist dies der Fall, so wird 
        ein Error ausgelöst. '''
    if 'triebwagen_nr' in data and Triebwagen.query.filter_by(nr=data['triebwagen_nr']).first().nr != zug.triebwagen_nr and \
        Triebwagen.query.filter_by(nr=data['triebwagen_nr']).first().zug:
        return bad_request('Der eingegebene Triebwagen wurde bereits einem Zug zugeordnet, bitte geben Sie einen anderen Triebwagen ein')

    ''' Als nächstes wird überprüft, ob die Spurweiten der einzelnen Waggons übereinstimmen. Ist dies nicht der Fall,
        so wird ein Error ausgelöst.'''
    spurweite = Triebwagen.query.filter_by(nr=data['triebwagen_nr']).first().spurweite
    for w in data['personenwagen']:
        if spurweite != w.spurweite:
            return bad_request('Die Spurweiten der ausgewählten Waggons stimmen nicht überein! Bitte wählen Sie Waggons mit einer einheitlichen Spurweite aus.')

    zug.from_dict(data)
    db.session.commit()

    return jsonify(zug.to_dict())
