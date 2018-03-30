from app import db
from flask_login import UserMixin
from sqlalchemy import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin, SQLAlchemyBackend

#Author: DANIEL BIS

"""
User to Employee = One to One
User to Shop = One to One
Shop to User = Many to One
Shop to Employe = One to Many

"""

#define user model
class User(UserMixin, db.Model):

    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key = True);
    first_name = db.Column(db.String(128), nullable = False)
    last_name = db.Column(db.String(128), nullable = False)
        #identification data email&password
    email = db.Column(db.String(64), nullable = False, unique = True)
    password = db.Column(db.String(128), nullable = False)
    role = db.Column(db.String(32), nullable=False )
    manager = db.Column(db.Integer, default=0)
    phonenumber = db.Column(db.String(60), nullable=True)
    date_created = db.Column(db.DateTime, default = db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default = db.func.current_timestamp(), onupdate = db.func.current_timestamp())
    img_path = db.Column(db.String(120), nullable=True)


    shopId = db.Column(db.Integer, ForeignKey("Shops.shopId"))
    schedules = relationship("Schedule", backref="Users")
    appointments = relationship("Appointment", backref="Users")

    #relationships (will be defined later)
    #Appointments = relationship("Appointment", backref = "Users")

    def __init__(self, firstname, lastname, email, password, role,manager = 0, phonenumber = "", img=""):
        self.first_name = firstname
        self.last_name = lastname
        self.email = email
        self.password = password
        self.phonenumber = phonenumber
        self.role = role
        self.manager = manager
        self.img_path = img

    def __repr__(self):
        return '<Name %r, Email %r>' % (self.first_name, self.email)


class Shop(db.Model):
    __tablename__ = "Shops"
    shopId = db.Column(db.Integer, primary_key = True)
    users = relationship("User", backref="Shops")   #db.Column(db.Integer, ForeignKey("Users.id"))
    shopname = db.Column(db.String(80), nullable=False, unique=True)
    location = db.Column(db.String(80), nullable=False)
    img_path = db.Column(db.String(120), nullable=True)
    #Enable backpropagation between Shops and their working hours

    def __init__(self, shopname, location, img=""):
        self.shopname = shopname
        self.location = location
        self.img_path = img

    def __repr__(self):
        return '<Name %r>' %self.shopname


class OAuth(OAuthConsumerMixin, db.Model):
    provider_user_id = db.Column(db.String(256), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)
