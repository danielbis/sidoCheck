from flask import Flask, render_template, redirect, url_for, Blueprint, jsonify, request, session
from flask_sqlalchemy  import SQLAlchemy
from flask_wtf import FlaskForm 
from flask_login import login_user, login_required, logout_user, current_user
import logging
from app.mod_customer.forms import DateForm, DateForm_v2

#import database object and login manager from app module
from app import app, db, login_manager


#Import module models containing User
from app.mod_auth.models import User, Shop
from app.mod_provider.models import Schedule, Appointment, Service
from app.mod_provider.api import check_availability_by_emplId, is_slot_open
from datetime import *

customer_mod = Blueprint("mod_customer", __name__)

@customer_mod.route('/dashboardcustomer')
@login_required
def dashboardcustomer():
	shops = Shop.query.all()
	return render_template('customer/dashboard_customer.html', name=current_user.first_name, shops = shops)


@customer_mod.route('/<shopname>/employee_list')
@login_required
def employee_list(shopname):
	shop = Shop.query.filter_by(shopname=shopname).first()
	employees = shop.users

	return render_template('customer/employee_list.html', employees=employees, shopname=shopname)

@customer_mod.route('/<shopname>/availability/<empl_id>', methods=["GET", "POST"])
@login_required
def availability(shopname, empl_id):
	form = DateForm()
	services = Service.query.filter(Service.providers.any(id=empl_id)).all()
	employee = User.query.filter_by(id=empl_id).first()
	if form.validate_on_submit():
		print(form.dt.data.strftime('%x'))
		return render_template('<h1> Booked </h1>')
	return render_template('customer/availability.html', shopname=shopname, form = form, empl_id = empl_id, employee = employee, services=services)

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
	slots = [x.strftime("%H:%M") for x in check_availability_by_emplId(empl_id, d, int(int(service.service_length)/20)) ] 

	return jsonify(slots)

@customer_mod.route('/bookslot', methods=["GET", "POST"])
@login_required
def bookslot():
	

	#retrieve data from ajax request
	request_json = request.get_json()
	date_string = str(request_json['date_string'])
	service_id = request_json['service_id']
	time_slot = request_json['time_slot']
	empl_id = request_json['empl_id']

	#process the data
	print("date string: ", date_string)
	date_string = date_string[:-4] + date_string[-2:]
	d = datetime.strptime(date_string, '%m/%d/%y').date()
	print("date is: ", d)

	date_string += " " + time_slot
	print("date and time: ", date_string)
	datetime_object = datetime.strptime(date_string, '%m/%d/%y %H:%M')
	print("datetime is: ", datetime_object)

	service = Service.query.filter_by(service_id=service_id).first()
	slots_required = int(int(service.service_length)/20)
	print("empl_id is ", empl_id, " service id is: ", service_id, " slots required ", slots_required, " d is ", d, " datetime_object is ", datetime_object )
	if (is_slot_open(empl_id, d, datetime_object, slots_required)):
		#datescheduled, username, user_last_name, userphone, useremail, userId, service_id)
		employee = User.query.filter_by(id=empl_id).first()
		interval = timedelta(minutes=20)
		for i in range(0,slots_required):
			a = Appointment(datetime_object + (i*interval), current_user.first_name, current_user.last_name, current_user.phonenumber, current_user.email, current_user.id, service_id)
			employee.appointments.append(a)

		
		db.session.commit()
		session["confirmation"] = { 
			"service_name": service.service_name, 
			"price": service.service_price, 
			"service_length": service.service_length,
			"date_scheduled": datetime_object,
			"employee_name": employee.first_name + " "+employee.last_name,
			"customer_name": current_user.first_name + " " + current_user.last_name,
			"customer_id": current_user.id, 
			"customer_email": current_user.email, 
			"empl_id": empl_id
		}

		return jsonify("/confirmation")		
	return jsonify("slot_taken")

@customer_mod.route('/confirmation', methods=["GET", "POST"])
@login_required
def confirmation():
	confirmation = session.pop("confirmation", None)
	a = Appointment.query.filter_by(date_scheduled = confirmation["date_scheduled"], employeeId = confirmation["empl_id"], userId = confirmation["customer_id"]).first()

	

	if (a == None):
		print("a is none")
		confirmation["message"] = "Booking failed due to technical problems"
	elif (int(a.userId) != int(current_user.id) or int(confirmation["empl_id"]) != int(a.employeeId)):
		print("a.userId ", a.userId, " current_user.id ", current_user.id, " confirmation[empl_id] ", confirmation["empl_id"], " a.employeeId ", a.employeeId )
		confirmation["message"] = "Booking failed due to technical problems"
	else:
		confirmation["message"] = "Congratulation! Your appointment was booked!"
	return render_template("customer/confirmation.html", confirmation = confirmation)


@customer_mod.route('/history', methods=["GET", "POST"])
@login_required
def history():
	my_appointments = Appointment.query.filter_by(userId = current_user.id).all()

	today = datetime.now()
	# mark upcoming appointemnts
	for a in my_appointments:
		employee = User.query.filter_by(id = a.employeeId).first()
		shop = Shop.query.filter_by(shopId = employee.shopId).first()
		if a.date_scheduled > today:
			a.upcoming = True
		else:
			a.upcoming = False

		a.shop = shop.shopname
		a.employee = employee.first_name + employee.last_name
	my_appointments.sort(key=lambda r: r.date_scheduled, reverse=True)
	
	return render_template("customer/history.html", my_appointments = my_appointments)

