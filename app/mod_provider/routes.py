# Author: DANIEL BIS
from flask import Flask, render_template, redirect, url_for, Blueprint, session, request, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from flask_wtf import FlaskForm
from flask_login import login_user, logout_user, current_user
import logging
from app.mod_provider.forms import DateForm, ServiceForm, AddServiceForm, BookDateForm, BookTimeForm, EditShopProfile, \
    UpdateShopPassword, EditEmployeeProfile

# import database object and login manager from app module
from app import db, login_manager, login_required
# import the app object itself
from app import app
import logging
import sys, traceback

# Import module models containing User
from app.mod_auth.models import User, Shop
from app.mod_auth.routes import load_user

from app.mod_provider.models import Schedule, Appointment, Service
from app.mod_provider.api import check_availability_by_employee_id, is_slot_open, get_employees_appointments_by_date, \
    check_availability_by_shop, get_next_available, get_schedules
from datetime import *

provider_mod = Blueprint("mod_provider", __name__, url_prefix="/provider")

"""
    Implementation: Daniel Bis

    Permissions: shop

    Renders the main page for the shop.
    Queries for all of the appointments for the day (today).
    ServiceForm is a form that enables the shop to choose a service that they
    can potentially book the next available appointment for. 
    If the form validates:
        :returns redirect('walkin.html')
        
    :returns render_template('dashboard_customer.html')

"""


@provider_mod.route('/dashboardprovider', methods=['GET', 'POST'])
@login_required('shop')
def dashboardprovider():

    employees = User.query.filter_by(shop_id=current_user.shop_id).all()
    empl_app = []
    date_string = request.args.get('date', 0, type=str)
    if date_string is not 0:
        print("rs: ", date_string)
        date_string = date_string[:-4] + date_string[-2:]
        print("rs: ", date_string)
        d = datetime.strptime(date_string, '%m/%d/%y').date()
    else:
        d = date.today()

    print("d is", d)
    for e in employees:
        if e.id == current_user.id:
            del (e)
        else:
            a = get_employees_appointments_by_date(e, d)
            empl_app += a

    print("appoint before sort: ", empl_app)
    empl_app.sort(key=lambda r: r["time"], reverse=False)
    print("appoint after sort: ", empl_app)

    if date_string is not 0:
        return jsonify(empl_app)

    form = ServiceForm()
    shops_services = Service.query.filter(Service.providers.any(id=current_user.id)).all()
    form.service.choices = [(s.service_id, s.service_name) for s in shops_services]
    shop = Shop.query.filter_by(shop_id=current_user.shop_id).first()

    app.logger.info('dashboard, shop: %s', shop.shop_name)

    if form.validate_on_submit():
        session["walkin_service_id"] = form.service.data
        return redirect(url_for("mod_provider.walkin"))

    return render_template('dashboardprovider.html', name=shop.shop_name, employees=employees, empl_app=empl_app,
                           form=form)


"""
    Implementation: Daniel Bis
    
    DateForm is responsible for gathering information about the schedule.
    On POST save the schedule or schedules to the database
        :returns redirect('scheduled')
    on GET
        :returns render_template('add_schedule')

"""


@provider_mod.route('/addschedule', methods=['GET', 'POST'])
@login_required('shop')
def add_schedule():
    form = DateForm()
    sb = Schedule.query.count()
    counter = 0
    if form.validate_on_submit():
        employee = User.query.filter_by(email=form.email.data).first()
        print("email: ", form.email.data)
        print(employee.shop_id, current_user.shop_id)
        if employee.shop_id == current_user.shop_id:
            day = timedelta(days=1)
            start_date = form.start_date.data
            end_date = form.end_date.data
            start_time = form.start_time.data
            end_time = form.end_time.data
            print(start_date, end_date, start_time, end_time)
            print(datetime.combine(start_date, start_time))
            while start_date <= end_date:
                sanity_check = db.session.query(Schedule).filter(
                    Schedule.employee_id == employee.id).filter(
                    Schedule.start_time.between(
                        datetime.combine(start_date, datetime.min.time()),
                        datetime.combine(start_date, datetime.max.time()))).first()
                if sanity_check is not None:
                    print('deleting ', sanity_check)
                    db.session.delete(sanity_check)
                    db.session.commit()
                    counter -= 1

                new_schedule = Schedule(start_time=datetime.combine(start_date, start_time),
                                        end_time=datetime.combine(start_date, end_time))
                employee.schedules.append(new_schedule)
                start_date += day
                counter += 1

            db.session.commit()
            sa = Schedule.query.count()
            print(sa, sb)
            if sa - sb == counter:
                session["scheduled"] = True
            else:
                session["scheduled"] = False
            return redirect(url_for('mod_provider.scheduled'))
    print("form not validated")
    return render_template('provider/add_schedule.html', form=form)


"""
    Implementation: Daniel Bis
    
    renders a confirmation page after adding the schedule by the shop.
    Checks if the operation  was successful.
    
"""


@provider_mod.route('/scheduled', methods=['GET', 'POST'])
@login_required('shop')
def scheduled():
    success = session.pop("scheduled", None)

    if success:
        return render_template('provider/scheduled.html', message="Schedule added successfully.")
    else:
        return render_template('provider/scheduled.html', message="Adding the schedule failed.")


"""
    Implementation: Daniel Bis
    
    Renders a list of the next available time slots for each employee, 
    given the date and service id
    
    :returns render_template('walkin.html)
     
"""


@provider_mod.route('/walkin', methods=['GET', 'POST'])
@login_required('shop')
def walkin():
    # shop = Shop.query.filter_by(shop_id=current_user.shop_id).first()
    service_id = session.pop("walkin_service_id", None)
    service = Service.query.filter_by(service_id=service_id).first()
    d = date.today()
    slots_shop = get_next_available(current_user.shop_id, d, service.service_length)

    for s in slots_shop:
        print(s)
        s["availability"] = [x.strftime("%H:%M") for x in s["availability"]]

    return render_template('provider/walkin.html', slots_shop=slots_shop, service_id=service_id,
                           date_today=str(d.strftime("%m/%d/%Y")))


"""
    Implementation: Daniel Bis

    Permissions: shop
    
    Enables shop to add services and assign them to employees. 
    
    Query for the shop and its employees and append new service object to them.
    
    :returns render_template('addservice.html')
"""


@provider_mod.route('/addservice', methods=['GET', 'POST'])
@login_required('shop')
def addservice():
    shop = Shop.query.filter_by(shop_id=current_user.shop_id).first()
    employees = shop.users[1:]

    form = AddServiceForm()
    form.employees.choices = [(e.id, e.first_name + " " + e.last_name) for e in employees]
    print(form.employees.choices)
    if form.validate_on_submit():
        print("choices: ", form.employees.data)
        s = Service(form.service_name.data, form.service_length.data, form.service_price.data)
        s.providers.append(current_user)
        for u in shop.users:
            if u.id in form.employees.data:
                s.providers.append(u)
        try:
            db.session.add(s)
        except Exception as e:
            app.logger.error(traceback.format_exc())
        db.session.commit()
        return redirect(url_for("mod_provider.dashboardprovider"))

    return render_template('provider/addservice.html', form=form)


"""
    Implementation: Daniel Bis

    Permissions: shop

    Renders list of schedules of employees for a given date (today) for the shop that is logged in.
    Calls get_schedules function from /api.py

    :returns render_template('schedules.html', schedules=[(User, Schedule)])
    
"""


@provider_mod.route('/schedules', methods=['GET', 'POST'])
@login_required('shop')
def schedules():
    schedules_list = get_schedules(current_user.shop_id, date.today())

    return render_template('provider/schedules.html', schedules=schedules_list)


"""
    Implementation: Daniel Bis

    Permissions: shop

    AJAX endpoint used to reload the schedules of employees 
    of a given shop for a different date.
    
    Calls get_schedules function from /api.py
    
    :returns [(User, Schedule)] list of schedules (JSON)
"""


@provider_mod.route('/reload_schedules', methods=['GET', 'POST'])
@login_required('shop')
def reload_schedules():
    date_string = request.args.get('date', 0, type=str)
    print("rs: ", date_string)
    date_string = date_string[:-4] + date_string[-2:]
    d = datetime.strptime(date_string, '%m/%d/%y').date()

    schedules_list = get_schedules(current_user.shop_id, d)

    return jsonify(schedules_list)


"""
    Implementation: Daniel Bis

    Permissions: shop
    
    Enables shops to choose a date and service for 
    in store appointment reservation. 
    
    on POST: 
     :returns redirect('book_appointment')
    on GET:
     :returns render_template('book_appointment_date.html')

"""


@provider_mod.route('/book_appointment_date', methods=['GET', 'POST'])
@login_required('shop')
def book_appointment_date():
    form = BookDateForm()
    shops_services = Service.query.filter(Service.providers.any(id=current_user.id)).all()
    form.service.choices = [(s.service_id, s.service_name) for s in shops_services]
    if form.validate_on_submit():
        session["booking_date"] = str(form.start_date.data)
        print("str fd ", str(form.start_date.data))
        session["service_id"] = form.service.data
        session["guest_name"] = form.guest_name.data
        print("guest_name: ", form.guest_name.data)
        return redirect(url_for('mod_provider.book_appointment'))
    return render_template('provider/book_appointment_date.html', form=form)


"""
    Implementation: Daniel Bis

    Permissions: shop

    Enables shops to browse available time slots for the given service and date.
    On selection an ajax request to the bookslot endpoint is made. 

   
     :returns render_template('book_appointment.html')

"""


@provider_mod.route('/book_appointment', methods=['GET', 'POST'])
@login_required('shop')
def book_appointment():
    form = BookTimeForm()

    date_string = session.pop("booking_date", None)
    if date_string is None:
        return redirect(url_for("mod_provider.book_appointment_date"))

    print("ds: ", date_string)

    d = datetime.strptime(date_string, '%Y-%m-%d').date()
    date_string = date_string[5:] + "-" + date_string[:4]
    print("date string after date(): ", date_string)
    shop = Shop.query.filter_by(shop_id=current_user.shop_id).first()
    service_id = session.pop("service_id", None)
    service = Service.query.filter_by(service_id=service_id).first()
    slots = []
    for u in shop.users:
        u_slots = [x.strftime("%H:%M") for x in check_availability_by_employee_id(u.id, d, service.service_length)]
        if (len(u_slots) > 0):
            slots.append((u, u_slots))

    return render_template('provider/book_appointment.html', slots=slots, form=form, date_string=date_string,
                           service_id=service_id)


"""
    Implementation: Daniel Bis

    Permissions: shop

    Parameters are restored from the session, and immediately stored back for backup in case of a refresh event.
    Parameters are used to show the details of appointment to the user.

    On POST request an appointment is created and saved to the database.
    Appointment is booked for a guest user. 
    Appointments are created in form of intervals. For example a service that takes an hour, with a shop whose 
    service intervals are 20 minutes long will need three appointment entries to the database. 
    This is resolved in a loop over the slots_required. 

    is_slot_open function from mod_provider/api.py ensures that the slots are still available. 

    confirmation object stores the information about the booked appointment. It is saved in the session. 
    It is restored in next view for the booking summary. 

    if GET:
        :returns render_template('confirm_shop.html')
    if POST:
        returns render_template('confirmation.html')

"""


@provider_mod.route('/confirm_shop', methods=["GET", "POST"])
@login_required('shop')
def confirm_shop():
    parameters = session.pop("parameters", None)
    guest_name = session.pop("guest_name", None)
    session["parameters"] = parameters
    session["guest_name"] = guest_name

    # session["parameters"] = parameters
    d = datetime.strptime(parameters['date_string'].replace("-", "/"), '%m/%d/%y').date()
    datetime_object = datetime.strptime(parameters['date_time_string'].replace("-", "/"), '%m/%d/%y %H:%M')

    service = Service.query.filter_by(service_id=parameters['service_id']).first()

    print("empl_id is ", parameters['empl_id'], " service id is: ", parameters['service_id'],
          " d is ", d, " datetime_object is ", datetime_object)

    employee = User.query.filter_by(id=parameters['empl_id']).first()
    shop = Shop.query.filter_by(shop_id=employee.shop_id).first()
    confirmation = {
        "service_name": service.service_name,
        "price": service.service_price,
        "service_length": service.service_length,
        "date_scheduled": datetime_object,
        "employee_name": employee.first_name + " " + employee.last_name,
        "shop_name": shop.shop_name
    }

    if request.method == 'POST':
        parameters = session.pop("parameters", None)
        guest_name = session.pop("guest_name", None)

        session["parameters"] = parameters
        session["guest_name"] = guest_name

        d = datetime.strptime(parameters['date_string'].replace("-", "/"), '%m/%d/%y').date()
        datetime_object = datetime.strptime(parameters['date_time_string'].replace("-", "/"), '%m/%d/%y %H:%M')
        service = Service.query.filter_by(service_id=parameters['service_id']).first()
        slots_required = int(service.service_length / 20)

        print("empl_id is ", parameters['empl_id'], " service id is: ", parameters['service_id'], " slots required ",
              slots_required, " d is ", d, " datetime_object is ", datetime_object)
        employee = User.query.filter_by(id=parameters['empl_id']).first()
        if (current_user.shop_id != employee.shop_id):
            return '<h1> Access not authorized </h1>'

        shop = Shop.query.filter_by(shop_id=employee.shop_id).first()

        confirmation_obj = {
            "open": None,
            "service_name": service.service_name,
            "price": service.service_price,
            "service_length": service.service_length,
            "date_scheduled": datetime_object,
            "employee_name": employee.first_name + " " + employee.last_name,
            "customer_name": guest_name,
            "customer_id": current_user.id,
            "customer_email": current_user.email,
            "empl_id": parameters['empl_id'],
            "shop_name": shop.shop_name
        }
        if (is_slot_open(parameters['empl_id'], d, datetime_object, service.service_length)):
            try:
                # datescheduled, username, user_last_name, userphone, useremail, user_id, service_id)
                interval = timedelta(minutes=20)
                for i in range(0, slots_required):
                    a = Appointment(datetime_object + (i * interval), guest_name, "guest", current_user.phone_number,
                                    current_user.email, current_user.id, parameters['service_id'])
                    employee.appointments.append(a)
                    app.logger.info('Appointment slot %s scheduled for employee: %s', i, employee.id)

                db.session.commit()
                confirmation_obj["open"] = 'True'
                session["confirmation"] = confirmation_obj
            except IntegrityError as IE:
                db.session.rollback()
                app.logger.error("cancel appointment, IntegrityError: %s", IE)

        else:
            confirmation_obj["open"] = 'False'
            session["confirmation"] = confirmation_obj

        return redirect(url_for("mod_provider.confirmation_shop"))

    return render_template("provider/confirm_shop.html", confirmation=confirmation)


"""
    Implementation: Daniel Bis

    Permissions: customer, shop

    Renders a confirmation for the appointment booked in the confirm view.

    :returns render_template('confirmation.html')

"""


@provider_mod.route('/confirmation_shop', methods=["GET", "POST"])
@login_required('shop')
def confirmation_shop():
    confirmation = session.pop("confirmation", None)
    session['confirmation'] = confirmation
    if confirmation["open"] == "False":
        print("Slots taken")
        confirmation["message"] = "Sorry, this time is already booked."
    else:
        a = Appointment.query.filter_by(date_scheduled=confirmation["date_scheduled"],
                                        employee_id=confirmation["empl_id"],
                                        user_id=confirmation["customer_id"]).first()

        if (a == None):
            print("appointment didnt propagate to the db")
            confirmation["open"] = "False"
            confirmation["message"] = "Booking failed due to technical problems"
        elif (int(a.user_id) != int(current_user.id) or int(confirmation["empl_id"]) != int(a.employee_id)):
            print("a.user_id ", a.user_id, " current_user.id ", current_user.id, " confirmation[empl_id] ",
                  confirmation["empl_id"], " a.employee_id ", a.employee_id)
            confirmation["open"] = "False"
            confirmation["message"] = "Booking failed due to technical problems"
        else:
            confirmation["message"] = "Congratulation! Your appointment was booked!"

    return render_template("provider/confirmation_shop.html", confirmation=confirmation)


"""
    Implementation: Daniel Bis

    Permissions: shop

    Ajax endpoint for canceling appointments from the dashboard view.

    :returns "success"/"failed" (JSON)

"""


@provider_mod.route('/cancel_appointment', methods=["GET", "POST"])
@login_required('shop')
def cancel_appointment():
    request_json = request.get_json()
    print("aid ", request_json["appointment_id"])
    appointment_id = int(request_json["appointment_id"])
    try:
        a = Appointment.query.filter_by(appointment_id=appointment_id).first()
        db.session.delete(a)
        db.session.commit()
        app.logger.info('Appointment canceled: %s', a.appointment_id)
        return jsonify("success")
    except IntegrityError as IE:
        db.session.rollback()
        app.logger.error("cancel appointment, IntegrityError: %s", IE)

    return jsonify("failed")


"""
    Implementation: Oluwatobi Ajayi

    Permissions: shop

    Renders shops profile details and a list of shops employees.

    :returns render_template('profile.html')

"""


@provider_mod.route('/profile', methods=['GET', 'POST'])
@login_required('shop')
def profile():
    my_profile = Shop.query.filter_by(shop_id=current_user.shop_id).first()
    User_profile = User.query.filter_by(id=current_user.id).first()
    employees = db.session.query(User).filter(User.shop_id == current_user.shop_id).all()
    employees.remove(employees[0])
    print(employees[0].first_name)
    return render_template('provider/profile.html', my_profile=my_profile, User_profile=User_profile,
                           employees=employees)


"""
    Implementation: Oluwatobi Ajayi, Daniel Bis

    Permissions: shop

    Renders a an edit profile form for the shop.
    EditShopProfile form from /form.py is passed to the template.
    
    :returns render_template('edit_profile.html')

"""


# Wrap commits into try/except blocks
@provider_mod.route('/edit_profile', methods=['GET', 'POST'])
@login_required('shop')
def edit_profile():
    form = EditShopProfile()
    # form_action= url_for('mod_provider.edit_profile')
    User_profile = User.query.filter_by(id=current_user.id).first()
    profile = Shop.query.filter_by(shop_id=current_user.shop_id).first()
    if form.validate_on_submit():
        print("validated")
        try:
            profile.shop_name = form.shop_name.data
            profile.location = form.location.data
            User_profile.email = form.email.data
            User_profile.last_name = form.lastname.data
            User_profile.first_name = form.firstname.data
            User_profile.phone_number = form.phone_number.data

            f = form.image.data
            if f is not None:
                filename = secure_filename(f.filename)
                print(filename)
                path = os.path.join(app.config['UPLOADED_IMAGES_DEST'], filename)
                f.save(path)
            else:
                filename = 'city.jpg'

            profile.img_path = filename
            db.session.commit()
            flash('Profile Updated')
        except IntegrityError as IE:
            db.session.rollback()
            app.logger.error('Error editing shop: %s', IE)

        return redirect(url_for("mod_provider.profile"))

    if request.method == 'GET':
        form.shop_name.data = profile.shop_name
        form.location.data = profile.location
        form.email.data = User_profile.email
        form.lastname.data = User_profile.last_name
        form.firstname.data = User_profile.first_name
        form.phone_number.data = User_profile.phone_number
        form.image.data = profile.img_path

    return render_template('provider/edit_profile.html', form=form, profile=profile, User_profile=User_profile,
                           title="Update Profile")


"""
    Implementation: Oluwatobi Ajayi

    Permissions: shop

    Renders a an edit password form for the shop.
    UpdateShopPassword form from /form.py is passed to the template.

    on form.validate_on_submit update the password entry in the table

    :returns render_template('update_password.html')

"""


@provider_mod.route('/update_password', methods=['GET', 'POST'])
@login_required('shop')
def update_password():
    form = UpdateShopPassword()
    form_action = url_for('mod_provider.update_password')
    profile = User.query.filter_by(id=current_user.id).first()

    if form.validate_on_submit():
        if check_password_hash(profile.password, form.old_password.data):
            if form.new_password.data == form.val_password.data:
                profile.password = generate_password_hash(form.new_password.data, method='sha256')
                db.session.commit()
                flash('Password Updated')

                return redirect(url_for("mod_provider.profile"))
            else:
                return '<h1>Passwords do not match</h1>'

        else:
            return '<h1>Incorrect Password</h1>'

    return render_template('provider/update_password.html', form=form, form_action=form_action, profile=profile,
                           title="Update Password")


"""
    Implementation: Daniel Bis

    Permissions: shop
    
    Ajax endpoint that enables the shop to remove an employee.
    
    :returns "success" on success 

"""


@provider_mod.route('/delete_employee', methods=['GET', 'POST'])
@login_required('shop')
def delete_employee():
    request_json = request.get_json()
    employee_id = request_json['employee_id']
    print("ID: ", employee_id)
    employee = User.query.filter_by(id=employee_id).first()

    db.session.delete(employee)
    db.session.commit()

    return jsonify('success')


"""
    Implementation: Daniel Bis

    Permissions: shop

    Renders a an edit profile form for the employee.
    EditEmployeeProfile form from /form.py is passed to the template.

    :returns render_template('edit_employee.html')

"""


@provider_mod.route('/edit_employee/<id>', methods=['GET', 'POST'])
@login_required('shop')
def edit_employee(id):
    form = EditEmployeeProfile()
    # form_action= url_for('mod_provider.edit_profile')
    profile = User.query.filter_by(id=id).first()
    if form.validate_on_submit():
        print("validated")
        try:
            profile.email = form.email.data
            profile.phone_number = form.phone_number.data
            f = form.image.data
            if f is not None:
                filename = secure_filename(f.filename)
                print(filename)
                path = os.path.join(app.config['UPLOADED_IMAGES_DEST'], filename)
                f.save(path)
            else:
                filename = 'city.jpg'

            profile.img_path = filename
            db.session.commit()
            flash('Profile Updated')
        except IntegrityError as IE:
            db.session.rollback()
            app.logger.error('Error editing employee: %s', IE)
        return redirect(url_for("mod_provider.profile"))

    if request.method == 'GET':
        form.email.data = profile.email
        form.phone_number.data = profile.phone_number

    return render_template('provider/edit_employee.html', form=form, profile=profile)
