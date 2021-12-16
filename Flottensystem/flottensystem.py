from app import app, db
from app.models import Mitarbeiter, Wartungspersonal, Zugpersonal, Administrator


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Mitarbeiter': Mitarbeiter, 'Wartungspersonal': Wartungspersonal, 'Zugpersonal': Zugpersonal, 'Administrator': Administrator}
