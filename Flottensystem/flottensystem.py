from app import app, db
from app.models import Mitarbeiter, Wartungspersonal, Zugpersonal, Administrator, Wagen, Triebwagen, Personenwagen, Wartung, Zug


''' Nachfolgend wird ein shell context erstellt, d.h. dass es durch den Aufruf von "flask shell" im Terminal nicht mehr notwendig ist, jedes mal die 
    benötigten Klassen zu importieren, da diese schon im Vorhinein importiert werden (voraussgesetzt, die Klassen wurden im shell context eingefügt). '''
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Mitarbeiter': Mitarbeiter, 'Wartungspersonal': Wartungspersonal,
            'Zugpersonal': Zugpersonal, 'Administrator': Administrator, 'Wagen': Wagen,
            'Triebwagen': Triebwagen, 'Personenwagen': Personenwagen, 'Wartung': Wartung,
            'Zug': Zug}
