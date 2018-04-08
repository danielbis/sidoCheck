from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from sqlalchemy.orm import relationship
from datetime import datetime
from app.mod_auth.models import User, Shop
from app.mod_provider.models import Appointment, Schedule, Service
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
import random
import cloudinary as Cloud
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url

"""
	Create sample users to populate db
	__init__(self, firstname, lastname, email, password, role, manager = 0, phone_number = "")
"""
random.seed(1)

<<<<<<< HEAD
for i in range(1, 10):
=======
for i in range(1, 21):
>>>>>>> f07714b56e5ab504016c891d3a4921564f1ba839
    name = "test_user" + str(i)
    lastname = "test_user_last" + str(i)
    email = "test_user" + str(i) + "@email.com"
    password = generate_password_hash("password", method='sha256')
    role = "customer"
    manager = 0
    phone_number = "123456000" + str(i)
    user = User(name, lastname, email, password, role, manager, phone_number)
    db.session.add(user)

"""
	Create Shops
"""
shop_names = ['placeholder', 'Living in the Cut', 'Sport Clips', 'Bobs Barber Shop', 'Cut it', 'Scissors', 'Looks',
              'Be like Bond']

for i in range(1, 7):
    name = shop_names[i]
    lastname = "test_shop_last" + str(i)
    email = "test_shop" + str(i) + "@email.com"
    password = generate_password_hash("password", method='sha256')
    role = "shop"
    manager = 1
    phone_number = "123456000" + str(i)
    new_user = User(first_name=name, last_name=lastname, phone_number=phone_number, email=email, password=password,
                    role="shop")
    if i % 2 == 0:
        uploaded = upload('./app/static/img/barber_whiskey.jpg')
        print(uploaded['public_id'])
        new_shop = Shop(shop_name=name, location="location", img=uploaded['public_id'])
    else:
        uploaded = upload('./app/static/img/barber.jpg')
        print(uploaded['public_id'])
        new_shop = Shop(shop_name=name, location="location", img=uploaded['public_id'])

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
    e_names = ['placeholder', 'Mason', 'Jacob', 'William', 'Ethan', 'James', 'Alexander']
    e_last = ['placeholder','Johnson', 'Brown', 'Dicksen', 'Curie', 'Ruble', 'Flinstone', ]
    for e in range(1, 6):
        empl_name = e_names[e]
        empl_lastname = e_last[e]
        empl_email = "test_empl" + str(i) + str(e) + "@email.com"
        empl_password = generate_password_hash("password", method='sha256')
        empl_role = "employee"
        empl_manager = 0
        empl_phone_number = "123456000" + str(i) + str(e)
        uploaded = upload('./app/static/img/default_profile.jpg')
        print(uploaded['public_id'])
        empl = User(first_name=empl_name, last_name=empl_lastname, email=empl_email, phone_number=empl_phone_number,
                    password=empl_password, role=empl_role, manager=empl_manager, img=uploaded['public_id'])

        #    Append some services
        s1.providers.append(empl)
        s2.providers.append(empl)
        s3.providers.append(empl)

        #    Append to a shop
        new_shop.users.append(empl)

<<<<<<< HEAD

        #   April
        for d in range(1, 31):
            schedule = Schedule(start_time=datetime(2018, 4, d, 11, 0, 0), end_time=datetime(2018, 4, d, 23, 0, 0))
=======
        #    add schedules (MARCH)
        for d in range(10, 32):
            schedule = Schedule(start_time=datetime(2018, 3, d, 8, 0, 0), end_time=datetime(2018, 3, d, 0, 0, 0))
            empl.schedules.append(schedule)

            # add appointments __init__(self, datescheduled, username, user_last_name userphone, useremail, user_id):
            for a in range(1, 6):
                ap = None
                random_user_id = random.randrange(1, 20)
                if a < 3:
                    ap = Appointment(datetime(2018, 3, d, 11, a * 20, 0), "test_user" + str(random_user_id),
                                     "test_user_last" + str(random_user_id), "123456000" + str(random_user_id),
                                     "test_user" + str(random_user_id) + "@email.com", random_user_id, 1)
                elif a < 5:
                    ap = Appointment(datetime(2018, 3, d, 12, (a - 2) * 20, 0), "test_user" + str(random_user_id),
                                     "test_user_last" + str(random_user_id), "123456000" + str(random_user_id),
                                     "test_user" + str(random_user_id) + "@email.com", random_user_id, 2)
                else:
                    ap = Appointment(datetime(2018, 3, d, 2, (a - 4) * 20, 0), "test_user" + str(random_user_id),
                                     "test_user_last" + str(random_user_id), "123456000" + str(random_user_id),
                                     "test_user" + str(random_user_id) + "@email.com", random_user_id, 3)
                print("date: ", ap.date_scheduled, "email: ", ap.client_email)
                empl.appointments.append(ap)

        #   April
        for d in range(1, 31):
            schedule = Schedule(start_time=datetime(2018, 4, d, 11, 0, 0), end_time=datetime(2018, 4, d, 18, 0, 0))
>>>>>>> f07714b56e5ab504016c891d3a4921564f1ba839
            empl.schedules.append(schedule)

            # add appointments __init__(self, datescheduled, username, user_last_name userphone, useremail, user_id):
            for a in range(1, 6):
                ap = None
                random_user_id = random.randrange(1, 20)
                if a < 3:
                    ap = Appointment(datetime(2018, 3, d, 11, a * 20, 0), "test_user" + str(random_user_id),
                                     "test_user_last" + str(random_user_id), "123456000" + str(random_user_id),
                                     "test_user" + str(random_user_id) + "@email.com", random_user_id, 1)
                elif a < 5:
                    ap = Appointment(datetime(2018, 3, d, 12, (a - 2) * 20, 0), "test_user" + str(random_user_id),
                                     "test_user_last" + str(random_user_id), "123456000" + str(random_user_id),
                                     "test_user" + str(random_user_id) + "@email.com", random_user_id, 2)
                else:
                    ap = Appointment(datetime(2018, 3, d, 2, (a - 4) * 20, 0), "test_user" + str(random_user_id),
                                     "test_user_last" + str(random_user_id), "123456000" + str(random_user_id),
                                     "test_user" + str(random_user_id) + "@email.com", random_user_id, 3)
                print("date: ", ap.date_scheduled, "email: ", ap.client_email)
                empl.appointments.append(ap)

    db.session.add(new_shop)
db.session.commit()
