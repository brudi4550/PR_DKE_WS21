from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app import login


@login.user_loader
def load_user(id):
    return Employee.query.get(int(id))


class RouteWarning(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    msg = db.Column(db.String(512))
    route_start = db.Column(db.String(128))
    route_end = db.Column(db.String(128))
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    system_id = db.Column(db.Integer, db.ForeignKey('system.id'))


class TrainWarning(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    msg = db.Column(db.String(512))
    train_nr = db.Column(db.String(128))
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    system_id = db.Column(db.Integer, db.ForeignKey('system.id'))


class Rushhour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    tour_id = db.Column(db.Integer, db.ForeignKey('tour.id'))


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
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    start_time = db.Column(db.Time, index=True, default=datetime.now().time())
    end_time = db.Column(db.Time, index=True, default=datetime.now().time())
    weekdays = db.Column(db.String(64))
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
    rushhours = db.relationship('Rushhour', backref='tour', cascade='all,delete', lazy='dynamic')

    def trip_count(self):
        single_trips = self.trips.count()
        interval_trips = 0
        for interval in self.intervals:
            interval_trips += interval.trips.count()
        return single_trips + interval_trips

    def future_trip_count(self):
        count = 0
        for trip in self.trips:
            if not trip.is_before_current_datetime():
                count += 1
        for interval in self.intervals:
            for trip in interval.trips:
                if not trip.is_before_current_datetime():
                    count += 1
        return count

    def past_trip_count(self):
        count = 0
        for trip in self.trips:
            if trip.is_before_current_datetime():
                count += 1
        for interval in self.intervals:
            for trip in interval.trips:
                if trip.is_before_current_datetime():
                    count += 1
        return count

    # next_trip returns a trip that lies in the future. Past, not yet deleted, trips are ignored
    # if there is no trip in the future for this tour next_trip returns None
    def next_trip(self):
        next_trip = None
        for trip in self.trips:
            next_trip = earlier_upcoming_trip(next_trip, trip)
        for interval in self.intervals:
            for trip in interval.trips:
                next_trip = earlier_upcoming_trip(next_trip, trip)
        return next_trip

    def time_until_next_trip(self):
        next_trip = self.next_trip()
        if next_trip is None:
            return None
        now = datetime.now()
        until = next_trip.start_datetime - now
        return until.total_seconds()


# trips whose datetime lies in the past are ignored
# expects that a trip might be None
def earlier_upcoming_trip(trip1, trip2):
    trip1_in_past = True
    trip2_in_past = True
    if trip1 is not None:
        trip1_in_past = trip1.is_before_current_datetime()
    if trip2 is not None:
        trip2_in_past = trip2.is_before_current_datetime()
    # None trips get treated as if they were in the past
    if not trip1_in_past and not trip2_in_past:
        return min(trip1, trip2, key=lambda t: t.start_datetime)
    elif not trip1_in_past and trip2_in_past:
        return trip1
    elif trip1_in_past and not trip2_in_past:
        return trip2
    elif trip1_in_past and trip2_in_past:
        return None


class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_datetime = db.Column(db.DateTime, index=True, default=datetime.now())
    crew_id = db.Column(db.Integer, db.ForeignKey('crew.id'))
    tour_id = db.Column(db.Integer, db.ForeignKey('tour.id'))
    interval_id = db.Column(db.Integer, db.ForeignKey('interval.id'))

    def is_before_current_datetime(self):
        return self.start_datetime < datetime.now()

    def __repr__(self):
        return '<Trip {}>'.format(self.id)
