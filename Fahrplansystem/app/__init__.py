from functools import wraps
from flask import Flask, url_for, redirect, request, render_template
from app.config import Config
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
import logging
from logging.handlers import RotatingFileHandler
import os
from flask_bootstrap import Bootstrap

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata = MetaData(naming_convention=convention)
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db, render_as_batch=True)
login = LoginManager(app)
bootstrap = Bootstrap(app)
login.login_view = 'login'


from app.routes.general import append_activity


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
        append_activity(f'Mitarbeiter {fn} {ln} (ID:{employee_id}) hat versucht {url} aufzurufen, Method:{method}')
        return render_template('errors/404.html', url=url), 404
    return decorated_view


from app import models, errors
from app.routes import general, employee, crew, tour, trip, api

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
