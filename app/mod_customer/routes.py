from flask import Flask, render_template, redirect, url_for, Blueprint, jsonify, request
from flask_sqlalchemy  import SQLAlchemy
from flask_wtf import FlaskForm 
from flask_login import login_user, login_required, logout_user, current_user
import logging
from app.mod_customer.forms import DateForm, DateForm_v2

#import database object and login manager from app module
from app import app, db, login_manager


#Import module models containing User
from app.mod_auth.models import User, Shop
from app.mod_provider.models import Schedule, Appointment
from app.mod_provider.api import check_availability_by_emplId
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
	if form.validate_on_submit():
		print(form.dt.data.strftime('%x'))
		return render_template('<h1> Booked </h1>')
	return render_template('customer/availability.html', shopname=shopname, form = form, empl_id = empl_id)

@customer_mod.route('/timeslots', methods=["GET", "POST"])
def timeslots():

	date_string = request.args.get('date', 0, type=str)
	date_string = date_string[:-4] + date_string[-2:]
	empl_id = request.args.get('empl_id', 0, type=int)
	d = datetime.strptime(date_string, '%m/%d/%y').date()
	print("date is: ", date_string)
	print("date object is: ", d)
	print("empl_id is: ", empl_id)
	slots = [x.strftime("%I:%M") for x in check_availability_by_emplId(empl_id, d)] 

	return jsonify(slots)




