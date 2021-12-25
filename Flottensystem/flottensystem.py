from app import app, db
from app.models import Mitarbeiter, Wartungspersonal, Zugpersonal, Administrator, Wagen, Triebwagen, Personenwagen, Wartung, Zug


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Mitarbeiter': Mitarbeiter, 'Wartungspersonal': Wartungspersonal, 'Zugpersonal': Zugpersonal, 'Administrator': Administrator, 'Wagen': Wagen, 'Triebwagen': Triebwagen, 'Personenwagen': Personenwagen, 'Wartung': Wartung, 'Zug': Zug}
