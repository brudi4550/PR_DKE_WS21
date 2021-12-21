from flask import render_template, request
from app import app, db


@app.errorhandler(404)
def not_found_error(error):
    url = request.path
    return render_template('errors/404.html', url=url), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
