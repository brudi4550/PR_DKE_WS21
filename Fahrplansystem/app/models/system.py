from app import db


class System(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    last_system_check = db.Column(db.DateTime)
    days_to_keep_old_trips = db.Column(db.Integer, default=0)
    known_route_warnings = db.relationship('RouteWarning', backref='system', cascade='all,delete', lazy='dynamic')
    known_train_warnings = db.relationship('TrainWarning', backref='system', cascade='all,delete', lazy='dynamic')
