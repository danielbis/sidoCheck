from flask import Flask, render_template, redirect, url_for, Blueprint, jsonify, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from flask_login import login_user, login_required, logout_user, current_user
from app.mod_customer.forms import DateForm, DateForm_v2, EditProfile, UpdatePassword, ServiceForm

# import database object and login manager from app module
from app import app, db, login_manager, login_required

# Import module models containing User
from app.mod_auth.models import User, Shop
from app.mod_provider.models import Schedule, Appointment, Service
from app.mod_provider.api import check_availability_by_employee_id, is_slot_open, filter_history, get_next_available
from datetime import *

customer_mod = Blueprint("mod_customer", __name__)

"""
    Implementation: Daniel Bis
    
    Permissions: customer
    
    Renders the main page for the customer.
    Presents the list of registered service providers (shops).
    
    : returns render_template('dashboard_customer.html')
    
"""


@customer_mod.route('/dashboardcustomer')
@login_required('customer')
def dashboardcustomer():
    shops = Shop.query.all()

    return render_template('customer/dashboard_customer.html', name=current_user.first_name, shops=shops)


"""
    Implementation: Daniel Bis

    Permissions: customer


    Renders the page for the given shop, querying by the shop name.
    Presents the list of the shops employees.
    ServiceForm is a form that enables customers to choose a service that they
    can potentially book the next available appointment for. 
    If the form validates:
        :returns redirect('book_next_available')
    else:
        :returns render_template('employee_list')

"""


@customer_mod.route('/<shop_name>/employee_list')
@login_required('customer')
def employee_list(shop_name):
    shop = Shop.query.filter_by(shop_name=shop_name).first()
    employees = shop.users[1:]  # delete shop user from employees

    form = ServiceForm()
    shops_services = Service.query.filter(Service.providers.any(id=shop.users[0].id)).all()
    form.service.choices = [(s.service_id, s.service_name) for s in shops_services]

    if form.validate_on_submit():
        session["service_id"] = form.service.data
        session["shop_id"] = shop_id
        return redirect(url_for("mod_customer.book_next_available"))

    return render_template('customer/employee_list.html', employees=employees, shop_name=shop_name, shop_id=shop.shop_id, form=form)


@customer_mod.route('/next_available/<shop_id>', methods=["GET", "POST"])
@login_required('customer')
def next_available(shop_id):

    form = ServiceForm()
    shop = Shop.query.filter_by(shop_id=shop_id).first()
    shops_services = Service.query.filter(Service.providers.any(id=shop.users[0].id)).all()
    form.service.choices = [(s.service_id, s.service_name) for s in shops_services]

    if form.validate_on_submit():
        session["service_id"] = form.service.data
        session["shop_id"] = shop_id
        return redirect(url_for("mod_customer.book_next_available"))

    return render_template('customer/next_available.html', form=form, shop_id=shop_id)


"""
    Implementation: Daniel Bis

    Permissions: customer


    Renders the list of next available appointment for chosen service, grouped by employee's names.
    User can book the appointment in that view making an ajax request to the bookslot endpoint.
    
    :returns render_template('book_next_available.html')

"""

@customer_mod.route('/book_next_available', methods=["GET", "POST"])
@login_required('customer')
def book_next_available():

    service_id = session.pop('service_id', None)
    shop_id = session.pop('shop_id', None)
    service = Service.query.filter_by(service_id=service_id).first()

    d = date.today()
    slots_shop = get_next_available(shop_id, d, service.service_length)

    for s in slots_shop:
        print(s)
        s["availability"] = [x.strftime("%H:%M") for x in s["availability"]]

    return render_template('customer/book_next_available.html', slots_shop=slots_shop, service_id=service_id,
                           date_today=str(d.strftime("%m/%d/%Y")))


"""
    Implementation: Daniel Bis

    Permissions: customer


    Renders a template with a calendar widget.
    When user selects a date in the calendar an ajax request is made to 
    the 'timeslots' endpoint, which returns a list of slots available 
    for the specified service, employee and date.
    After the slot is chosen, 'Book it' button appears which takes user to a page
    where he/she can confirm his/her choice.

    :returns render_template('availability.html')

"""

@customer_mod.route('/<shop_name>/availability/<empl_id>', methods=["GET", "POST"])
@login_required('customer')
def availability(shop_name, empl_id):
    form = DateForm()
    services = Service.query.filter(Service.providers.any(id=empl_id)).all()
    employee = User.query.filter_by(id=empl_id).first()
    if form.validate_on_submit():
        print(form.dt.data.strftime('%x'))
        return render_template('<h1> Booked </h1>')
    return render_template('customer/availability.html', shop_name=shop_name, form=form, empl_id=empl_id,
                           employee=employee, services=services)


"""
    Implementation: Daniel Bis
    
    Permissions: customer, shop


    AJAX endpoint that returns a list of available timeslots for a given employee, date and service.
    It calls the check_availability_by_employee_id() function from the mod_provider/api.py 

    :returns list of slots, JSON format

"""


@customer_mod.route('/timeslots', methods=["GET", "POST"])
@login_required('ANY')
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
    slots = [x.strftime("%I:%M%p") for x in
             check_availability_by_employee_id(empl_id, d, service.service_length)]

    print("slots: ", slots)

    return jsonify(slots)


"""
    Implementation: Daniel Bis

    Permissions: customer, shop

    AJAX endpoint that stores the information about the service being booked in the parameters object.
    That object is stored in the session.
    
    If '/confirm' is returned, jQuery in the template will redirect the user to the page where he/she 
    can confirm the reservation. 

    :returns '/confirm' string on success, JSON format

"""

@customer_mod.route('/bookslot', methods=["GET", "POST"])
@login_required('ANY')
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


"""
    Implementation: Daniel Bis

    Permissions: customer, shop

    Parameters are restored from the session, and immediately stored back for backup in case of a refresh event.
    Parameters are used to show the details of appointment to the user.
    
    On POST request an appointment is created and saved to the database. 
    Appointments are created in form of intervals. For example a service that takes an hour, with a shop whose 
    service intervals are 20 minutes long will need three appointment entries to the database. 
    This is resolved in a loop over the slots_required. 
    
    is_slot_open function from mod_provider/api.py ensures that the slots are still available. 
    
    confirmation object stores the information about the booked appointment. It is saved in the session. 
    It is restored in next view for the booking summary. 
    
    if GET:
        :returns render_template('confirm.html')
    if POST:
        returns render_template('confirmation.html')

"""


@customer_mod.route('/confirm', methods=["GET", "POST"])
@login_required('ANY')
def confirm():

    if request.method == 'POST':
        parameters = session.pop("parameters", None)

        # store parameters back for later
        session["parameters"] = parameters

        d = datetime.strptime(parameters['date_string'], '%m/%d/%y').date()
        datetime_object = datetime.strptime(parameters['date_time_string'], '%m/%d/%y %I:%M%p')
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
    datetime_object = datetime.strptime(parameters['date_time_string'], '%m/%d/%y %I:%M%p')

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


"""
    Implementation: Daniel Bis

    Permissions: customer, shop

    Renders a confirmation for the appointment booked in the confirm view.

    :returns render_template('confirmation.html')

"""


@customer_mod.route('/confirmation', methods=["GET", "POST"])
@login_required('ANY')
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


"""
    Implementation: Daniel Bis

    Permissions: customer, shop

    Renders a list of appointments booked by a the current_user.

    :returns render_template('history.html')

"""
@customer_mod.route('/history', methods=["GET", "POST"])
@login_required('customer')
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


"""
    Implementation: Oluwatobi Ajayi

    Permissions: customer

    Renders users profile details.

    :returns render_template('profile.html')

"""


@customer_mod.route('/profile', methods=['GET', 'POST'])
@login_required('customer')
def profile():
    my_profile = User.query.filter_by(id=current_user.id).first()

    return render_template('customer/profile.html', my_profile=my_profile)

"""
    Implementation: Oluwatobi Ajayi

    Permissions: customer

    Renders a an edit profile form for the customer.
    EditProfile form from /form.py is passed to the template.
    
    :returns render_template('edit_profile.html')

"""


@customer_mod.route('/edit_profile', methods=['GET', 'POST'])
@login_required('customer')
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


"""
    Implementation: Oluwatobi Ajayi

    Permissions: customer

    Renders a an edit password form for the customer.
    UpdatePassword form from /form.py is passed to the template.
    
    on form.validate_on_submit update the password entry in the table
    
    :returns render_template('update_password.html')

"""

@customer_mod.route('/update_password', methods=['GET', 'POST'])
@login_required('customer')
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
