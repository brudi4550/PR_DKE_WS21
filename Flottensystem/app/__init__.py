import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from flask_bootstrap import Bootstrap
from sqlalchemy import MetaData

''' Nachfolgend wird ein MetaData Objekt hinzugefügt, um damit bei Datenbankmigrationen (flask db migrate) 
    automatisch die Namensgebung der Constraints durchzuführen, da diese sonst in den Migrationsdateien mit 
    None definiert werden und es somit zu einem "ValueError: Constraint must have a name" Fehler kommt '''
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
login.login_view = 'login'
bootstrap = Bootstrap(app)

from app.api import bp as api_bp
app.register_blueprint(api_bp, url_prefix='/api')

from app import routes, models
