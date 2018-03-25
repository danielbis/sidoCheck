# Author: DANIEL BIS
from flask import Flask, render_template, redirect, url_for, Blueprint, session, request, jsonify
from flask_sqlalchemy  import SQLAlchemy
from flask_wtf import FlaskForm 
from flask_login import login_user, login_required, logout_user, current_user
import logging
from app.mod_provider.forms import DateForm, ServiceForm, AddServiceForm, BookDateForm, BookTimeForm

#import database object and login manager from app module
from app import db, login_manager
#import the app object itself
from app import app

#Import module models containing User
from app.mod_auth.models import User, Shop
from app.mod_auth.routes import load_user

from app.mod_provider.models import Schedule, Appointment, Service
from app.mod_provider.api import check_availability_by_emplId, is_slot_open, get_employees_appointments_by_date, check_availability_by_shop, get_next_available
from datetime import *
provider_mod = Blueprint("mod_provider", __name__, url_prefix = "/provider")

@provider_mod.route('/dashboardprovider', methods = ['GET', 'POST'])
@login_required
def dashboardprovider():
	employees = User.query.filter_by(shopId = current_user.shopId).all()
	empl_app = []
	for e in employees:
		if e.id == current_user.id:
			del(e)
		else:
			d = date.today()
			a = get_employees_appointments_by_date(e, d)
			empl_app.append((e, a))
	
	form = ServiceForm()
	shops_services = Service.query.filter(Service.providers.any(id=current_user.id)).all()	
	form.service.choices = [(s.service_id, s.service_name) for s in shops_services]
	shop = Shop.query.filter_by(shopId = current_user.shopId).first()
	if form.validate_on_submit():
		session["walkin_service_id"] = form.service.data
		return redirect(url_for("mod_provider.walkin"))
	
	return render_template('dashboardprovider.html', name=shop.shopname, employees = employees, empl_app=empl_app, form=form)


@provider_mod.route('/addschedule', methods = ['GET', 'POST'])
@login_required
def add_schedule():

	form = DateForm()
	sb = Schedule.query.count()
	counter = 0
	if form.validate_on_submit():
		employee = User.query.filter_by(email = form.email.data).first()
		print("email: ", form.email.data)
		print(employee.shopId, current_user.shopId)
		if employee.shopId == current_user.shopId:
			day = timedelta(days=1)
			start_date = form.start_date.data
			end_date = form.end_date.data
			start_time = form.start_time.data
			end_time = form.end_time.data
			print(start_date, end_date, start_time, end_time)
			print(datetime.combine(start_date, start_time))
			while start_date <= end_date:
				new_schedule = Schedule(starttime = datetime.combine(start_date, start_time), endtime = datetime.combine(end_date, end_time))
				employee.schedules.append(new_schedule)
				start_date += day 
				counter += 1
			db.session.add(new_schedule)
			db.session.commit()
			sa = Schedule.query.count()
			if sa - sb == counter:
				session["scheduled"] = True
			else:
				session["scheduled"] = False
			return redirect(url_for('mod_provider.scheduled'))
	print("form not validated")
	return render_template('provider/add_schedule.html', form = form)


@provider_mod.route('/scheduled', methods = ['GET', 'POST'])
@login_required
def scheduled():
	success = session.pop("scheduled", None)
	
	if success:
		return render_template('provider/scheduled.html', message = "Schedule added successfully.")
	else: 
		return render_template('provider/scheduled.html', message = "Adding the schedule failed.")




@provider_mod.route('/walkin', methods=['GET', 'POST'])
@login_required
def walkin():

	shop = Shop.query.filter_by(shopId = current_user.shopId).first()
	print("shop is ", shop)
	service_id = session.pop("walkin_service_id", None)
	print("s_id ", service_id)
	service = Service.query.filter_by(service_id = service_id).first()
	print("service ", service)
	slots_required = int(int(service.service_length)/ 20)
	d = date.today()
	slots_shop = get_next_available(current_user.shopId, d, slots_required)
	for s in slots_shop:
		s["availability"] = [x.strftime("%H:%M") for x in s["availability"]] 

	print("date_today is ", d.strftime("%m/%d/%Y"))

	return render_template('provider/walkin.html', slots_shop = slots_shop, service_id=service_id, date_today = str(d.strftime("%m/%d/%Y")))

@provider_mod.route('/addservice', methods=['GET', 'POST'])
@login_required
def addservice():

	shop = Shop.query.filter_by(shopId = current_user.shopId).first()
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
		db.session.add(s)
		db.session.commit()
		return redirect(url_for("mod_provider.dashboardprovider"))


	return render_template('provider/addservice.html', form = form)

@provider_mod.route('/book_appointment_date', methods=['GET', 'POST'])
@login_required
def book_appointment_date():

	form = BookDateForm()
	shops_services = Service.query.filter(Service.providers.any(id=current_user.id)).all()	
	form.service.choices = [(s.service_id, s.service_name) for s in shops_services]
	if form.validate_on_submit():
		session["booking_date"] = str(form.start_date.data)
		print("str fd ",  str(form.start_date.data))
		session["service_id"] = form.service.data
		session["guest_name"] = form.guest_name.data
		print("guest_name: ", form.guest_name.data)
		return redirect(url_for('mod_provider.book_appointment'))
	return render_template('provider/book_appointment_date.html', form=form)

@provider_mod.route('/book_appointment', methods=['GET', 'POST'])
@login_required
def book_appointment():

	form = BookTimeForm()

	date_string = session.pop("booking_date", None)
	print("ds: ", date_string)

	d = datetime.strptime(date_string, '%Y-%m-%d').date()
	date_string = date_string[5:] + "-" + date_string[:4]
	print("date string after date(): ", date_string)
	shop = Shop.query.filter_by(shopId = current_user.shopId).first()
	service_id = session.pop("service_id", None)
	service = Service.query.filter_by(service_id=service_id).first()
	slots_required = int(service.service_length/20)
	slots = []
	for u in shop.users:
		u_slots = [x.strftime("%H:%M") for x in check_availability_by_emplId(u.id, d, slots_required) ] 
		if (len(u_slots) > 0):
			slots.append((u, u_slots))
	

	return render_template('provider/book_appointment.html', slots = slots, form = form, date_string = date_string, service_id=service_id)

@provider_mod.route('/confirm_shop', methods=["GET", "POST"])
@login_required
def confirm_shop():

		parameters = session.pop("parameters", None)
		guest_name = session.pop("guest_name", None)
		session["parameters"] = parameters
		session["guest_name"] = guest_name

		#session["parameters"] = parameters
		d = datetime.strptime(parameters['date_string'].replace("-", "/"), '%m/%d/%y').date()
		datetime_object = datetime.strptime(parameters['date_time_string'].replace("-", "/"), '%m/%d/%y %H:%M')

		service = Service.query.filter_by(service_id=parameters['service_id']).first()
		slots_required = int(int(service.service_length)/20)
		

		print("empl_id is ", parameters['empl_id'], " service id is: ", parameters['service_id'], " slots required ", slots_required, " d is ", d, " datetime_object is ", datetime_object )
		employee = User.query.filter_by(id=parameters['empl_id']).first()
		shop = Shop.query.filter_by(shopId = employee.shopId).first()
		confirmation = {
			"service_name": service.service_name, 
			"price": service.service_price, 
			"service_length": service.service_length,
			"date_scheduled": datetime_object,
			"employee_name": employee.first_name + " "+employee.last_name,
			"shop_name": shop.shopname
		}
		if request.method == 'POST':
			parameters = session.pop("parameters", None)
			guest_name = session.pop("guest_name", None)

			d = datetime.strptime(parameters['date_string'].replace("-","/"), '%m/%d/%y').date()
			datetime_object = datetime.strptime(parameters['date_time_string'].replace("-","/"), '%m/%d/%y %H:%M')
			service = Service.query.filter_by(service_id=parameters['service_id']).first()
			slots_required = int(int(service.service_length)/20)
			
			print("empl_id is ", parameters['empl_id'], " service id is: ", parameters['service_id'], " slots required ", slots_required, " d is ", d, " datetime_object is ", datetime_object )
			employee = User.query.filter_by(id=parameters['empl_id']).first()
			if (current_user.shopId != employee.shopId):
				return '<h1> Access not authorized </h1>'

			shop = Shop.query.filter_by(shopId = employee.shopId).first()
			
			if (is_slot_open(parameters['empl_id'], d, datetime_object, slots_required)):
				#datescheduled, username, user_last_name, userphone, useremail, userId, service_id)
				interval = timedelta(minutes=20)
				for i in range(0,slots_required):
					a = Appointment(datetime_object + (i*interval), guest_name, "guest", current_user.phonenumber, current_user.email, current_user.id, parameters['service_id'])
					employee.appointments.append(a)

				
				db.session.commit()
				session["confirmation"] = { 
					"open": "True",
					"service_name": service.service_name, 
					"price": service.service_price, 
					"service_length": service.service_length,
					"date_scheduled": datetime_object,
					"employee_name": employee.first_name + " "+employee.last_name,
					"customer_name":guest_name,
					"customer_id": current_user.id, 
					"customer_email": current_user.email, 
					"empl_id": parameters['empl_id'], 
					"shopname": shop.shopname
				}
			else:
				session["confirmation"] = { 
					"open": "False", 
					"service_name": service.service_name, 
					"price": service.service_price, 
					"service_length": service.service_length,
					"date_scheduled": datetime_object,
					"employee_name": employee.first_name + " "+employee.last_name,
					"customer_name": guest_name,
					"customer_id": current_user.id, 
					"customer_email": current_user.email, 
					"empl_id": parameters['empl_id'],
					"shopname": shop.shopname
				}
				
			return redirect(url_for("mod_provider.confirmation_shop"))
	

		return render_template("provider/confirm_shop.html", confirmation= confirmation)


@provider_mod.route('/confirmation_shop', methods=["GET", "POST"])
@login_required
def confirmation_shop():
	confirmation = session.pop("confirmation", None)
	if confirmation["open"] == "False":
		print("Slots taken")
		confirmation["message"] = "Sorry, this time is already booked."
	else:
		a = Appointment.query.filter_by(date_scheduled = confirmation["date_scheduled"], employeeId = confirmation["empl_id"], userId = confirmation["customer_id"]).first()

		if (a == None):
			print("appointment didnt propagate to the db")
			confirmation["open"] = "False"
			confirmation["message"] = "Booking failed due to technical problems"
		elif (int(a.userId) != int(current_user.id) or int(confirmation["empl_id"]) != int(a.employeeId)):
			print("a.userId ", a.userId, " current_user.id ", current_user.id, " confirmation[empl_id] ", confirmation["empl_id"], " a.employeeId ", a.employeeId )
			confirmation["open"] = "False"
			confirmation["message"] = "Booking failed due to technical problems"
		else:
			confirmation["message"] = "Congratulation! Your appointment was booked!"
	
	return render_template("provider/confirmation_shop.html", confirmation = confirmation)


@provider_mod.route('/cancel_appointment', methods=["GET", "POST"])
@login_required
def cancel_appointment():

	request_json = request.get_json()
	print("aid ", request_json["appointment_id"])
	appointment_id = int(request_json["appointment_id"])
	try: 
		a = Appointment.query.filter_by(appointmentId = appointment_id).first()
		db.session.delete(a)
		db.session.commit()
		return jsonify("success")
	except IntegrityError:
		db.session.rollback()

	return jsonify("failed")
	

