from app.api import bp
from flask import jsonify, request, url_for
from app.models import Zug, Triebwagen
from app import db
from app.api.errors import bad_request

@bp.route('/Züge', methods=['GET'])
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
def getTrain(id):
    return jsonify(Zug.query.get_or_404(id).to_dict())

@bp.route('/Züge/<string:id>/Wartungen', methods=['GET'])
def getMaintenancesFromTrain(id):
    zug = Zug.query.get_or_404(id)
    data = Zug.to_collection_dict(zug.wartung, 'api.getMaintenancesFromTrain', id=id)
    return jsonify(data)

@bp.route('/Züge/<string:id>/Personenwaggons', methods=['GET'])
def getPersonenwaggonsFromTrain(id):
    zug = Zug.query.get_or_404(id)
    data = Zug.to_collection_dict(zug.personenwagen, 'api.getPersonenwaggonsFromTrain', id=id)
    return jsonify(data)

@bp.route('/Züge', methods=['POST'])
def createTrain():
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
def updateTrain(id):
    zug = Zug.query.get_or_404(id)
    data = request.get_json() or {}
    ''' In der folgenden Abfrage wird überprüft, ob die Zugnummer des bestimmten Zuges geändert wurde. Falls 
        dies geändert wurde und die geänderte Zugnummer in der Datenbank enthalten ist, wird ein Error 
        ausgelöst. '''
    if 'nr' in data and data['nr'] != zug.nr and Zug.query.filter_by(nr=data['nr']).first():
        return bad_request('Die einegegebene Zugnummer ist bereits vergeben! Bitte geben Sie eine andere Zugnummer ein')

    if 'triebwagen_nr' in data and Triebwagen.query.filter_by(nr=data['triebwagen_nr']).first().nr != zug.triebwagen_nr and \
        Triebwagen.query.filter_by(nr=data['triebwagen_nr']).first().zug:
        return bad_request('Der eingegebene Triebwagen wurde bereits einem Zug zugeordnet, bitte geben Sie einen anderen Triebwagen ein')
    spurweite = Triebwagen.query.filter_by(nr=data['triebwagen_nr']).first().spurweite
    '''for w in data['personenwagen']:
        if spurweite != w.spurweite:
            return bad_request('Die Spurweiten der ausgewählten Waggons stimmen nicht überein! Bitte wählen Sie Waggons mit einer einheitlichen Spurweite aus.')'''

    zug.from_dict(data)
    db.session.commit()

    return jsonify(zug.to_dict())
