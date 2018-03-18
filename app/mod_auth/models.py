from app import db
from flask_login import UserMixin
from sqlalchemy import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin, SQLAlchemyBackend
# Author: DANIEL BIS
# define user model


class User(UserMixin, db.Model):

    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(128), nullable = False)
    last_name = db.Column(db.String(128), nullable = False)
    password = db.Column(db.String(128), nullable=False)
        #identification data email&password
    email = db.Column(db.String(128), nullable = False, unique = True)
    date_created = db.Column(db.DateTime, default = db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default = db.func.current_timestamp(), onupdate = db.func.current_timestamp())


    shops = relationship("Shop", backref="Users")
    employee = relationship("Employee", backref="Users")

    #relationships (will be defined later)
    #Appointments = relationship("Appointment", backref = "Users")

    def __init__(self, firstname, lastname, email, password):
        self.first_name = firstname
        self.last_name = lastname
        self.email = email
        self.password = password

    def __repr__(self):
        return '<Name %r, Email %r>' % (self.name, self.Email)


class OAuth(OAuthConsumerMixin, db.Model):
    provider_user_id = db.Column(db.String(256), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)


class Shop(db.Model):
    __tablename__ = "Shops"
    shopId = db.Column(db.Integer, primary_key = True)
    users = relationship("User", backref="Shops")
    db.Column(db.Integer, ForeignKey("Users.id"))
    shopname = db.Column(db.String(80), nullable=False)
    location = db.Column(db.String(80), nullable=False)
    img_path = db.Column(db.String(120), nullable=True)
    employees = relationship("Employee", backref="Shops")
    #Enable backpropagation between Shops and their working hours
    schedules = relationship("Schedule", backref="Shops")

    def __init__(self, shopname, location, password, phonenumber, img = ""):
        self.shopname = shopname
        self.location = location
        self.img_path = img

    def __repr__(self):
        return '<Name %r>' %self.Name


class Employee(db.Model):

    __tablename__  = "Employees"

    employeeId = db.Column(db.Integer, primary_key = True)
    userId = db.Column(db.Integer, ForeignKey("Users.id"))
    shopId = db.Column(db.Integer, ForeignKey("Shops.shopId"))
    first_name = db.Column(db.String(128), nullable = False)
    last_name = db.Column(db.String(128), nullable = False)
    manager = db.Column(db.Integer, unique = False, default = 0) #default to false

    #Enable backpropagation between Employees and their Appointments
    #Appointments = relationship("Appointment", backref = "Employees")
    #Enable backpropagation between Employees and their Schedules
    schedules = relationship("Schedule", backref="Employees")

    def __init__(self, firstname, lastname, manager = 0):
        self.first_name = firstname
        self.last_name = lastname
        self.manager = manager

    def __repr__(self):
        name = self.first_name + self.last_name
        return '<Name %r>' %(name)