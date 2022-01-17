from app.api import bp
from flask import jsonify, request, url_for
from app.models import Wartung
from app import db
from app.api.errors import bad_request

@bp.route('/Wartungen', methods=['GET'])
def getMaintenances():
    data = Wartung.to_collection_dict(Wartung.query.all(), 'api.getMaintenances')
    return jsonify(data)

@bp.route('/Wartungen/<int:id>', methods=['GET'])
def getMaintenance(id):
    return jsonify(Wartung.query.get_or_404(id).to_dict())
