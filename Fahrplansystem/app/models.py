from datetime import datetime, timedelta, time, date
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from flask_login import UserMixin
from app import login


@login.user_loader
def load_user(id):
    return Employee.query.get(int(id))


class Rushhour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    system_id = db.Column(db.Integer, db.ForeignKey('system.id'))


def update_timetable():
    start_date = date.today()
    end_date = start_date + timedelta(weeks=4)
    tours = Tour.query.all()
    for tour in tours:
        for interval in tour.intervals:
            for trip in interval.trips:
                if trip.date < start_date:
                    db.session.delete(trip)
            start_time = interval.start_time
            end_time = interval.end_time
            iv_minutes_delta = timedelta(minutes=interval.interval_minutes)
            while start_date < end_date:
                t = Trip.query.filter_by(interval_id=interval.id)\
                    .filter_by(date=start_date)
                while start_time < end_time:
                    if not isinstance(t, Trip):
                        t = t.filter_by(time=start_time).first()
                    if t is None:
                        t = Trip()
                        t.date = start_date
                        t.time = start_time
                        t.interval_id = interval.id
                        db.session.add(t)
                    # Converting datetime.time to datetime.datetime and back
                    # because time doesn't support addition, datetime does
                    dummy_time = datetime(2021, 1, 1, hour=start_time.hour, minute=start_time.minute)
                    dummy_time = iv_minutes_delta + dummy_time
                    start_time = time(hour=dummy_time.hour, minute=dummy_time.minute)
                start_date = start_date + timedelta(days=1)
                start_time = interval.start_time
        for trip in tour.trips:
            if trip.date < date.today():
                db.session.delete(trip)
    sys = System.query.get(1)
    sys.last_system_check = datetime.today()
    db.session.commit()


class System(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    last_system_check = db.Column(db.DateTime)
    rushhours = db.relationship('Rushhour', backref='system', cascade='all,delete', lazy='dynamic')


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
    start_time = db.Column(db.Time, index=True, default=datetime.now().time())
    end_time = db.Column(db.Time, index=True, default=datetime.now().time())
    interval_minutes = db.Column(db.Integer)
    trips = db.relationship('Trip', backref='interval', cascade='all,delete', lazy='dynamic')
    tour_id = db.Column(db.Integer, db.ForeignKey('tour.id'))


class Tour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.String(64), nullable=False)
    end = db.Column(db.String(64), nullable=False)
    train = db.Column(db.String(64))
    intervals = db.relationship('Interval', backref='tour', cascade='all,delete', lazy='dynamic')
    rushHourMultiplicator = db.Column(db.Float, nullable=False)
    trips = db.relationship('Trip', backref='tour', cascade='all,delete', lazy='dynamic')

    def trip_count(self):
        single_trips = self.trips.count()
        interval_trips = 0
        for interval in self.intervals:
            interval_trips += interval.trips.count()
        return single_trips + interval_trips

    def next_trip(self):
        next_trip = self.trips.first()
        for trip in self.trips:
            if trip.date < next_trip.date:
                next_trip = trip
            elif trip.date == next_trip.date:
                if trip.time.hour < next_trip.time.hour:
                    next_trip = trip
                elif trip.time.hour == next_trip.time.hour:
                    if trip.time.minute < next_trip.time.minute:
                        next_trip = trip
        for interval in self.intervals:
            for trip in interval.trips:
                if trip.date < next_trip.date:
                    next_trip = trip
                elif trip.date == next_trip.date:
                    if trip.time.hour < next_trip.time.hour:
                        next_trip = trip
                    elif trip.time.hour == next_trip.time.hour:
                        if trip.time.minute < next_trip.time.minute:
                            next_trip = trip
        return next_trip


class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, index=True, default=datetime.today())
    time = db.Column(db.Time, index=True, default=datetime.now().time())
    crew_id = db.Column(db.Integer, db.ForeignKey('crew.id'))
    tour_id = db.Column(db.Integer, db.ForeignKey('tour.id'))
    interval_id = db.Column(db.Integer, db.ForeignKey('interval.id'))

    def __repr__(self):
        return '<Trip {}>'.format(self.id)
