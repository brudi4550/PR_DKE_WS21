from app.api import bp
from flask import jsonify, request, url_for
from app.models import Wagen, Triebwagen, Personenwagen
from app import db
from app.api.errors import bad_request

@bp.route('/Waggons', methods=['GET'])
#@token_auth.login_required
def getWaggons():
    data = Wagen.to_collection_dict(Wagen.query.all(), 'api.getWaggons')
    return jsonify(data)

@bp.route('/Triebwaggons', methods=['GET'])
#@token_auth.login_required
def getTriebwaggons():
    data = Triebwagen.to_collection_dict(Triebwagen.query.all(), 'api.getTriebwaggons')
    return jsonify(data)

@bp.route('/Personenwaggons', methods=['GET'])
#@token_auth.login_required
def getPersonenwaggons():
    data = Personenwagen.to_collection_dict(Personenwagen.query.all(), 'api.getPersonenwaggons')
    return jsonify(data)

@bp.route('/Waggons/<string:id>', methods=['GET'])
#@token_auth.login_required
def getWaggon(id):
    return jsonify(Wagen.query.get_or_404(id).to_dict())

