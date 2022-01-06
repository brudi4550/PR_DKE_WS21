import logging
import os
import locale
from functools import wraps
from logging.handlers import RotatingFileHandler

from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

from app.config import Config

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
locale.setlocale(locale.LC_ALL, 'de_AT')
metadata = MetaData(naming_convention=convention)
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db, render_as_batch=True)
login = LoginManager(app)
bootstrap = Bootstrap(app)
login.login_view = 'login'


def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_user.employee_type == 'admin':
            return func(*args, **kwargs)
        url = request.path
        method = request.method
        employee_id = current_user.id
        fn = current_user.first_name
        ln = current_user.last_name
        return render_template('errors/404.html', url=url), 404
    return decorated_view


from app import errors
from app.models import System, update_timetable
from app.routes import general, employee, crew, tour, trip, interval, api

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/timetableSystem.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Fahrplansystem gestartet')


if 'system' not in db.metadata.tables.keys():
    db.create_all()
else:
    timetable_system = System.query.get(1)
    if timetable_system is None:
        timetable_system = System()
        db.session.add(timetable_system)
        db.session.commit()
