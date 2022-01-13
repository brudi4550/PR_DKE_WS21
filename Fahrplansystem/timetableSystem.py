from app.models import *


@app.shell_context_processor
def make_shell_context():
    return {'db': db,
            'Employee': Employee,
            'Activity': Activity,
            'Tour': Tour,
            'Trip': Trip,
            'Crew': Crew,
            'Interval': Interval,
            'System': System,
            'RouteWarning': RouteWarning,
            'TrainWarning': TrainWarning
            }
