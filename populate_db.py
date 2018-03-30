from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from sqlalchemy.orm import relationship
from datetime import datetime
from app.mod_auth.models import User, Shop
from app.mod_provider.models import Appointment, Schedule, Service
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db

"""
	Create sample users to populate db
	__init__(self, firstname, lastname, email, password, role, manager = 0, phonenumber = "")
"""

for i in range(1, 21):
    name = "test_user" + str(i)
    lastname = "test_user_last" + str(i)
    email = "test_user" + str(i) + "@email.com"
    password = generate_password_hash("password", method='sha256')
    role = "customer"
    manager = 0
    phonenumber = "123456000" + str(i)
    user = User(name, lastname, email, password, role, manager, phonenumber)
    db.session.add(user)

"""
	Create Shops
"""

for i in range(1, 7):
    name = "test_shop" + str(i)
    lastname = "test_shop_last" + str(i)
    email = "test_shop" + str(i) + "@email.com"
    password = generate_password_hash("password", method='sha256')
    role = "shop"
    manager = 1
    phonenumber = "123456000" + str(i)
    new_user = User(firstname=name, lastname=lastname, phonenumber=phonenumber, email=email, password=password,
                    role="shop")
    new_shop = Shop(shopname=name, location="location")
    # db.session.add(new_shop)
    new_shop.users.append(new_user)
    # Params: service_name, service_length, service_price
    s1 = Service('Simple Hair Cut', 20, 20)
    s1.providers.append(new_user)
    s2 = Service('Perm', 40, 75)
    s2.providers.append(new_user)
    s3 = Service('Hair Dye', 60, 80)
    s3.providers.append(new_user)
    db.session.add(s1)
    db.session.add(s2)
    db.session.add(s3)

    """ add employees hired by that shop """
    for e in range(1, 10):
        empl_name = "test_empl" + str(i) + str(e)
        empl_lastname = "test_empl_last" + str(i) + str(e)
        empl_email = "test_empl" + str(i) + str(e) + "@email.com"
        empl_password = generate_password_hash("password", method='sha256')
        empl_role = "employee"
        empl_manager = 0
        empl_phonenumber = "123456000" + str(i) + str(e)
        empl = User(firstname=empl_name, lastname=empl_lastname, email=empl_email, phonenumber=empl_phonenumber,
                    password=empl_password, role=empl_role, manager=empl_manager)
        if e % 3 == 0:
            s1.providers.append(empl)
        elif e % 3 == 1:
            s2.providers.append(empl)
        else:
            s3.providers.append(empl)
        new_shop.users.append(empl)
        # add schedules
        for d in range(10, 30):
            schedule = Schedule(starttime=datetime(2018, 3, d, 11, 0, 0), endtime=datetime(2018, 3, d, 18, 0, 0))
            empl.schedules.append(schedule)

            # add appointments __init__(self, datescheduled, username, user_last_name userphone, useremail, userId):
            for a in range(1, 6):
                ap = None
                if a < 3:
                    ap = Appointment(datetime(2018, 3, d, 11, a * 20, 0), "test_user" + str(a),
                                     "test_user_last" + str(a), "123456000" + str(a),
                                     "test_user" + str(a) + "@email.com", a, 1)
                elif a < 5:
                    ap = Appointment(datetime(2018, 3, d, 12, (a - 2) * 20, 0), "test_user" + str(a),
                                     "test_user_last" + str(a), "123456000" + str(a),
                                     "test_user" + str(a) + "@email.com", a, 2)
                else:
                    ap = Appointment(datetime(2018, 3, d, 2, (a - 4) * 20, 0), "test_user" + str(a),
                                     "test_user_last" + str(a), "123456000" + str(a),
                                     "test_user" + str(a) + "@email.com", a, 3)
                print("date: ", ap.date_scheduled, "email: ", ap.client_email)
                empl.appointments.append(ap)

    db.session.add(new_shop)
db.session.commit()
