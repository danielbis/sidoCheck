# Author: DANIEL BIS

from app import db
from app.mod_auth.models import User, Shop
from flask_login import UserMixin
from sqlalchemy import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship


class Appointment(db.Model):

    __tablename__ = "Appointments"

    appointmentId = db.Column(db.Integer, primary_key = True)
    date_created = db.Column(db.DateTime, default = db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default = db.func.current_timestamp(), onupdate = db.func.current_timestamp())
    date_scheduled = db.Column(db.DateTime, nullable = False)
    client_first = db.Column(db.String(60), nullable = False)
    client_last = db.Column(db.String(60), nullable = False)
    client_phone = db.Column(db.String(15))
    client_email = db.Column(db.String(60))

    employeeId = db.Column(db.Integer, ForeignKey("Users.id"))
    userId = db.Column(db.Integer)

    service_id = db.Column(db.Integer)

    def __init__(self, datescheduled, username, user_last_name, userphone, useremail, userId, service_id):
        self.date_scheduled = datescheduled
        self.client_first = username
        self.client_last = user_last_name
        self.client_phone = userphone
        self.client_email = useremail
        self.userId = userId
        self.service_id = service_id
        
 
    def __repr__(self):
        return '<Client Name %r, User Email %r, Date and Time %r, EmployeeID %r>' \
               % (self.client_first, self.client_email, self.date_scheduled, self.employeeId)


"""Schedule class representing a daily availability for each of the employees. 
   It stores the WeekDay (0-6), ServiceLength (intervals), 
   StartTime (Employess start), EndTime(Emplouees End Time)                                                             
                                                                """
class Schedule(db.Model):

    __tablename__ = "Schedules"

    scheduleId = db.Column(db.Integer, primary_key = True)
    #week_start_date = db.Column(db.DateTime, nullable = False)
    weekday = db.Column(db.Integer, default = -1) #0-6 0 = Moday 6 = Sunday
    interval_length = db.Column(db.Integer, nullable = False, default=20) #for example 20 minutes
    start_time = db.Column(db.DateTime, nullable = False)
    end_time = db.Column(db.DateTime, nullable = False)

    emplId = db.Column(db.Integer, ForeignKey("Users.id"))

    def __init__(self, starttime, endtime, weekday = -1, interval_len = 20):
        self.weekDay = weekday
        self.interval_length = interval_len
        self.start_time = starttime
        self.end_time = endtime


    def __repr__(self):
        return '<Employee ID %r, Week Day %r, StartTime %r, EndTime %r, Service Length %r>' \
               % (self.emplId, self.weekday, self.start_time, self.end_time, self.interval_length)

"""
    Definition of many to many relationship between services offered by a given shop
    and employees that provide them.
"""

service_identifier = db.Table('service_identifier',
    db.Column('service_id', db.Integer, db.ForeignKey('Services.service_id')),
    db.Column('user_id', db.Integer, db.ForeignKey('Users.id'))
)

class Service(db.Model):
    __tablename__ = 'Services'
    service_id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(128))
    service_length = db.Column(db.Integer) #preferebly multiples of 20 
    service_price = db.Column(db.Integer)
    providers = db.relationship("User", secondary=service_identifier, backref=db.backref('Services'))

    def __init__(self, service_name, service_length, service_price):
        self.service_name = service_name
        self.service_length = service_length
        self.service_price = service_price
    def __repr__(self):
        return '<Service ID %r, Service name %r, Length %r, Price %r>' \
               % (self.service_id, self.service_name, self.service_length, self.service_price)

