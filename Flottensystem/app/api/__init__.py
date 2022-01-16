from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import trains, maintenance, waggons,  errors, tokens