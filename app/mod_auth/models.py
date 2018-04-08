from app import db
from flask_login import UserMixin
from sqlalchemy import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin, SQLAlchemyBackend
from time import time
import jwt
from app import app

"""
    Below database models are implemented. 
    Models are implemented using sqlalchemy and flask-sqlalchemy wrappers for SQL database. 
    Models defined in this file define the user classes of the platform.
    
    Relations:
    User to Employee = One to One
    User to Shop = One to One
    Shop to User = Many to One
    Shop to Employe = One to Many

"""

"""
    Implementation: Daniel Bis, Abraham D'mitri Joseph
    
    User model (table)
    Stores basic profile information. 
    
    role specifies the type of user ['customer', 'shop', 'employee']
    img_path is reality a name of the .jpg file stored in the ./static/img directory
    img_path is a file that will be used as a profile picture (assuming that the user is of type employee)
    shop_id is a foreign key bonding user with his/her employee
    schedules is a list of schedules for the given user (assuming that the user is of type employee)
    appointments is a list of appointments booked for the given user (assuming that the user is of type employee)
    
"""


class User(UserMixin, db.Model):

    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(128), nullable = False)
    last_name = db.Column(db.String(128), nullable = False)
    #   identification data email&password
    email = db.Column(db.String(64), nullable = False, unique = True)
    password = db.Column(db.String(128), nullable = False)
    role = db.Column(db.String(32), nullable=False )
    manager = db.Column(db.Integer, default=0)
    phone_number = db.Column(db.String(60), nullable=True)
    date_created = db.Column(db.DateTime, default = db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default = db.func.current_timestamp(), onupdate = db.func.current_timestamp())
    img_path = db.Column(db.String(120), nullable=True)

    shop_id = db.Column(db.Integer, ForeignKey("Shops.shop_id"))
    schedules = relationship("Schedule", backref="Users")
    appointments = relationship("Appointment", backref="Users")

    #   relationships (will be defined later)
    #   Appointments = relationship("Appointment", backref = "Users")

    def __init__(self, first_name, last_name, email, password, role,manager = 0, phone_number = "", img=""):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.phone_number = phone_number
        self.role = role
        self.manager = manager
        self.img_path = img

    def __repr__(self):
        return '<Name %r, Email %r>' % (self.first_name, self.email)

    def get_reset_password_token(self, expires_in=6000):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

"""
    Implementation: Daniel Bis

    If a user is of type shop, he/she has a relationship with a shop.
    Shop HAS a list of users (employees), the very first user on that list is an owner (person who created the account).
    This user has the highest privileges and permissions. 
    This user is not treated as an employee anywhere in the later code.
    This user is a global/main user whose credentials are used in shop to perform all of the management type of operations.
    img_path is reality a name of the .jpg file stored in the ./static/img directory
    This file is going to be used as shops profile picture
    
"""


class Shop(db.Model):

    __tablename__ = "Shops"
    shop_id = db.Column(db.Integer, primary_key = True)
    users = relationship("User", backref="Shops")
    shop_name = db.Column(db.String(80), nullable=False, unique=True)
    location = db.Column(db.String(80), nullable=False)
    img_path = db.Column(db.String(120), nullable=True)
    #   Enable backpropagation between Shops and their working hours

    def __init__(self, shop_name, location, img=""):
        self.shop_name = shop_name
        self.location = location
        self.img_path = img

    def __repr__(self):
        return '<Name %r>' %self.shop_name


"""
    Implementation: Abraham Dmitri Joseph
    
    This class is responsible for storing id of users who register with social authentication methods.
    like Facebook or Google Gmail.

"""


class OAuth(OAuthConsumerMixin, db.Model):
    provider_user_id = db.Column(db.String(256), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)
