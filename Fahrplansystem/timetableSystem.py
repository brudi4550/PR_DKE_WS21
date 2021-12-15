from app import app, db
from app.models import Employee, Activity, Tour, Trip, Crew, Interval


@app.shell_context_processor
def make_shell_context():
    return {'db': db,
            'Employee': Employee,
            'Activity': Activity,
            'Tour': Tour,
            'Trip': Trip,
            'Crew': Crew,
            'Interval': Interval
            }
