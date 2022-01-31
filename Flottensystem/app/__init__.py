import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from flask_bootstrap import Bootstrap
from sqlalchemy import MetaData, event

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
''' Als nächstes wird die Überprüfung der Foreignkeys explizit aktiviert. Diese Lösung konnte
    durch ein Forumseintrag realisiert werden. '''
event.listen(db.engine, 'connect', lambda c, _: c.execute('pragma foreign_keys=on'))
migrate = Migrate(app, db, render_as_batch=True)
login = LoginManager(app)
login.login_view = 'login'
bootstrap = Bootstrap(app)

''' Als nächstes wird eine Log Datei für das Flottensystem erstellt. Hier werden die Errors geloggt. '''
if not app.debug:
    ''' Existiert noch kein "logs"-Ordner, so wird eines erstellt. Dies wird in der nachfolgenden
        if-Condition abgefragt. '''
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/flottensystem.log', maxBytes=10240, backupCount=10)
    ''' Als nächstes wird die Anzeige der Logs festgelegt (also wie die log-Messages angezeigt werden). '''
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Flottensystem startup')

from app.api import bp as api_bp
app.register_blueprint(api_bp, url_prefix='/api')

from app import routes, models, errors
