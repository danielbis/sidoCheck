from flask import Flask, render_template, redirect, url_for, Blueprint, jsonify, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from flask_login import login_user, login_required, logout_user, current_user
from app.mod_customer.forms import DateForm, DateForm_v2, EditProfile, UpdatePassword

# import database object and login manager from app module
from app import app, db, login_manager

# Import module models containing User
from app.mod_auth.models import User, Shop
from app.mod_provider.models import Schedule, Appointment, Service
from app.mod_provider.api import check_availability_by_employee_id, is_slot_open, filter_history
from datetime import *

customer_mod = Blueprint("mod_customer", __name__)


@customer_mod.route('/dashboardcustomer')
@login_required
def dashboardcustomer():
    shops = Shop.query.all()
    return render_template('customer/dashboard_customer.html', name=current_user.first_name, shops=shops)


@customer_mod.route('/<shop_name>/employee_list')
@login_required
def employee_list(shop_name):
    shop = Shop.query.filter_by(shop_name=shop_name).first()
    employees = shop.users[1:]  # delete shop user from employees

    return render_template('customer/employee_list.html', employees=employees, shop_name=shop_name)


@customer_mod.route('/<shop_name>/availability/<empl_id>', methods=["GET", "POST"])
@login_required
def availability(shop_name, empl_id):
    form = DateForm()
    services = Service.query.filter(Service.providers.any(id=empl_id)).all()
    employee = User.query.filter_by(id=empl_id).first()
    if form.validate_on_submit():
        print(form.dt.data.strftime('%x'))
        return render_template('<h1> Booked </h1>')
    return render_template('customer/availability.html', shop_name=shop_name, form=form, empl_id=empl_id,
                           employee=employee, services=services)


@customer_mod.route('/timeslots', methods=["GET", "POST"])
@login_required
def timeslots():
    date_string = request.args.get('date', 0, type=str)
    date_string = date_string[:-4] + date_string[-2:]
    empl_id = request.args.get('empl_id', 0, type=int)
    service_id = request.args.get('service_id', 0, type=int)
    d = datetime.strptime(date_string, '%m/%d/%y').date()
    service = Service.query.filter_by(service_id=service_id).first()
    print("date is: ", date_string)
    print("date object is: ", d)
    print("empl_id is: ", empl_id)
    print("service_id is: ", service_id)
    slots = [x.strftime("%H:%M") for x in
             check_availability_by_employee_id(empl_id, d, service.service_length)]

    print("slots: ", slots)

    return jsonify(slots)


@customer_mod.route('/bookslot', methods=["GET", "POST"])
@login_required
def bookslot():
    # retrieve data from ajax request
    request_json = request.get_json()
    date_string = str(request_json['date_string'])

    # process the data
    date_string = date_string[:-4] + date_string[-2:]
    date_time_string = date_string + " " + request_json['time_slot']

    app.logger.info("Attempting to book slot: %s, shop_id: %s", date_time_string, current_user.shop_id)
    parameters = {
        "service_id": request_json['service_id'],
        "time_slot": request_json['time_slot'],
        "empl_id": request_json['empl_id'],
        "date_string": date_string,
        "date_time_string": date_time_string
    }

    # save to session to access in next screen
    session["parameters"] = parameters

    return jsonify("/confirm")


@customer_mod.route('/confirm', methods=["GET", "POST"])
@login_required
def confirm():

    if request.method == 'POST':
        parameters = session.pop("parameters", None)

        # store parameters back for later
        session["parameters"] = parameters

        d = datetime.strptime(parameters['date_string'], '%m/%d/%y').date()
        datetime_object = datetime.strptime(parameters['date_time_string'], '%m/%d/%y %H:%M')
        service = Service.query.filter_by(service_id=parameters['service_id']).first()
        slots_required = int(int(service.service_length) / 20)

        print("empl_id is ", parameters['empl_id'], " service id is: ", parameters['service_id'], " slots required ",
              slots_required, " d is ", d, " datetime_object is ", datetime_object)
        employee = User.query.filter_by(id=parameters['empl_id']).first()
        shop = Shop.query.filter_by(shop_id=employee.shop_id).first()

        #confirmation object that will be needed in the next screen
        confirmation_obj = {
                "open": None,
                "service_name": service.service_name,
                "price": service.service_price,
                "service_length": service.service_length,
                "date_scheduled": datetime_object,
                "employee_name": employee.first_name + " " + employee.last_name,
                "customer_name": current_user.first_name + " " + current_user.last_name,
                "customer_id": current_user.id,
                "customer_email": current_user.email,
                "empl_id": parameters['empl_id'],
                "shop_name": shop.shop_name,
                "shop_id": shop.shop_id
            }
        if (is_slot_open(parameters['empl_id'], d, datetime_object, service.service_length)):
            # datescheduled, username, user_last_name, userphone, useremail, user_id, service_id)
            interval = timedelta(minutes=20)
            for i in range(0, slots_required):
                a = Appointment(datetime_object + (i * interval), current_user.first_name, current_user.last_name,
                                current_user.phone_number, current_user.email, current_user.id, parameters['service_id'])
                employee.appointments.append(a)

            db.session.commit()
            confirmation_obj["open"] = "True"
            session["confirmation"] = confirmation_obj
        else:
            confirmation_obj["open"] = "False"
            session["confirmation"] = confirmation_obj

        return redirect(url_for("mod_customer.confirmation"))

    parameters = session.pop("parameters", None)

    #store parameters back for later
    session["parameters"] = parameters

    # format dates
    d = datetime.strptime(parameters['date_string'].replace("-", "/"), '%m/%d/%y').date()
    datetime_object = datetime.strptime(parameters['date_time_string'], '%m/%d/%y %H:%M')

    service = Service.query.filter_by(service_id=parameters['service_id']).first()
    slots_required = int(int(service.service_length) / 20)

    print("empl_id is ", parameters['empl_id'], " service id is: ", parameters['service_id'], " slots required ",
          slots_required, " d is ", d, " datetime_object is ", datetime_object)
    employee = User.query.filter_by(id=parameters['empl_id']).first()
    shop = Shop.query.filter_by(shop_id=employee.shop_id).first()
    confirmation = {
        "service_name": service.service_name,
        "price": service.service_price,
        "service_length": service.service_length,
        "date_scheduled": datetime_object,
        "employee_name": employee.first_name + " " + employee.last_name,
        "shop_name": shop.shop_name,
        "shop_id": shop.shop_id
    }

    return render_template("customer/confirm.html", confirmation=confirmation, user=current_user)


@customer_mod.route('/confirmation', methods=["GET", "POST"])
@login_required
def confirmation():
    confirmation = session.pop("confirmation", None)

    # store confirmation back for later (refresh etc)
    session["confirmation"] = confirmation

    if confirmation["open"] == "False":
        print("Slots taken")
        confirmation["message"] = "Sorry, this time is already booked."
    else:
        a = Appointment.query.filter_by(date_scheduled=confirmation["date_scheduled"],
                                        employee_id=confirmation["empl_id"], user_id=confirmation["customer_id"]).first()

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

    return render_template("customer/confirmation.html", confirmation=confirmation, user=current_user)


@customer_mod.route('/history', methods=["GET", "POST"])
@login_required
def history():
    my_appointments = Appointment.query.filter_by(user_id=current_user.id).all()
    today = datetime.now()
    # mark upcoming appointemnts
    for a in my_appointments:
        employee = User.query.filter_by(id=a.employee_id).first()
        if employee:
            shop = Shop.query.filter_by(shop_id=employee.shop_id).first()
            a.shop_name = shop.shop_name
            a.employee = employee.first_name + employee.last_name
        else:
            a.shop_name = "Unavailable"
            a.employee = "Unavailable"

        if a.date_scheduled > today:
            a.upcoming = True
        else:
            a.upcoming = False


    my_appointments.sort(key=lambda r: r.date_scheduled, reverse=True)
    my_appointments = filter_history(my_appointments)

    return render_template("customer/history.html", my_appointments=my_appointments)


@customer_mod.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    my_profile = User.query.filter_by(id=current_user.id).first()

    return render_template('customer/profile.html', my_profile=my_profile)


@customer_mod.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfile()
    form_action = url_for('mod_customer.edit_profile')

    profile = User.query.filter_by(id=current_user.id).first()

    if request.method == 'GET':
        form.email.data = profile.email
        form.phone_number.data = profile.phone_number

    if form.validate_on_submit():
        profile.email = form.email.data
        profile.phone_number = form.phone_number.data
        db.session.commit()
        flash('Profile Updated')
        return redirect(url_for("mod_customer.profile"))

    return render_template('customer/edit_profile.html', form=form, form_action=form_action, profile=profile,
                           title="Update Profile")


@customer_mod.route('/update_password', methods=['GET', 'POST'])
@login_required
def update_password():
    form = UpdatePassword()
    form_action = url_for('mod_customer.update_password')

    profile = User.query.filter_by(id=current_user.id).first()

    if form.validate_on_submit():
        if check_password_hash(profile.password, form.old_password.data):
            if form.new_password.data == form.val_password.data:
                profile.password = generate_password_hash(form.new_password.data, method='sha256')
                db.session.commit()
                flash('Password Updated')

                return redirect(url_for("mod_customer.profile"))
            else:
                return '<h1>Passwords do not match</h1>'

        else:
            return '<h1>Incorrect Password</h1>'

    return render_template('customer/update_password.html', form=form, form_action=form_action, profile=profile,
                           title="Update Password")
