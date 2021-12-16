from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from flask_login import UserMixin
from app import login


@login.user_loader
def load_user(id):
    return Employee.query.get(int(id))


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    msg = db.Column(db.String(256))
    time = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return f'{self.time.strftime("%H:%M:%S")} - {self.msg}'


class Employee(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ssn = db.Column(db.Integer, nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    employee_type = db.Column(db.String(32), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    crew_id = db.Column(db.Integer, db.ForeignKey('crew.id'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Employee Id {self.id}, {self.first_name} {self.last_name}, {self.employee_type}>'

    __mapper_args__ = {
        'polymorphic_identity': 'employee',
        'polymorphic_on': employee_type
    }


class TicketInspector(Employee):
    __mapper_args__ = {
        'polymorphic_identity': 'ticket_inspector'
    }


class TrainDriver(Employee):
    __mapper_args__ = {
        'polymorphic_identity': 'train_driver'
    }


class Admin(Employee):
    __mapper_args__ = {
        'polymorphic_identity': 'admin'
    }


class Crew(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employees = db.relationship('Employee', backref='crewMembers', lazy='dynamic')
    trips = db.relationship('Trip', backref='assigned_crew', lazy='dynamic')


class Interval(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fromHour = db.Column(db.Integer)
    toHour = db.Column(db.Integer)


class Tour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.String(64), nullable=False)
    end = db.Column(db.String(64), nullable=False)
    interval = db.Column(db.Integer, db.ForeignKey('interval.id'))
    rushHourMultiplicator = db.Column(db.Float, nullable=False)
    trips = db.relationship('Trip', backref='tour', lazy='dynamic')


class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, index=True, default=datetime.date)
    time = db.Column(db.Time, index=True, default=datetime.time)
    crew_id = db.Column(db.Integer, db.ForeignKey('crew.id'))
    tour_id = db.Column(db.Integer, db.ForeignKey('tour.id'))

    def __repr__(self):
        return '<Trip {}>'.format(self.id)
