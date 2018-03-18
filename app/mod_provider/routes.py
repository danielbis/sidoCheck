# Author: DANIEL BIS


from flask import Flask, render_template, redirect, url_for, Blueprint
from flask_sqlalchemy  import SQLAlchemy
from flask_wtf import FlaskForm 
from flask_login import login_user, login_required, logout_user, current_user
import logging
from app.mod_provider.forms import DateForm

#import database object and login manager from app module
from app import db, login_manager
#import the app object itself
from app import app

#Import module models containing User
from app.mod_auth.models import User, Shop
from app.mod_auth.routes import load_user

from app.mod_provider.models import Schedule, Appointment, Service
from app.mod_provider.api import check_availability_by_emplId, is_slot_open, get_employees_appointments_by_date 
from datetime import *
provider_mod = Blueprint("mod_provider", __name__, url_prefix = "/provider")

@provider_mod.route('/dashboardprovider')
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
			
	
	return render_template('dashboardprovider.html', name=current_user.first_name, employees = employees, empl_app=empl_app)


@provider_mod.route('/addschedule', methods = ['GET', 'POST'])
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

