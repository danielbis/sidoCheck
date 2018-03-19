# Author: DANIEL BIS
from flask import Flask, render_template, redirect, url_for, Blueprint, session
from flask_sqlalchemy  import SQLAlchemy
from flask_wtf import FlaskForm 
from flask_login import login_user, login_required, logout_user, current_user
import logging
from app.mod_provider.forms import DateForm, ServiceForm

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

	if form.validate_on_submit():
		session["walkin_service_id"] = form.service.data
		return redirect(url_for("mod_provider.walkin"))
	
	return render_template('dashboardprovider.html', name=current_user.first_name, employees = employees, empl_app=empl_app, form=form)


@provider_mod.route('/addschedule', methods = ['GET', 'POST'])
@login_required
def add_schedule():

	form = DateForm()

	if form.validate_on_submit():
		employee = User.query.filter_by(email = form.email.data).first()
		new_schedule = Schedule(starttime = form.start_time.data, endtime = form.end_time.data)

		employee.schedules.append(new_schedule)
		db.session.add(new_schedule)
		db.session.commit()
		return '<h1>New schedule added! </h1>'
	print("form not validated")
	return render_template('provider/add_schedule.html', form = form)


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



