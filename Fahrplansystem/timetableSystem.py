from app import app, db, print_query_result
from app.models import Employee


@app.shell_context_processor
def make_shell_context():
    return {'db': db,
            'Employee': Employee,
            'print_query_result': print_query_result}
