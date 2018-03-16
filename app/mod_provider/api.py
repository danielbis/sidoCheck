from flask_sqlalchemy  import SQLAlchemy
from app import app, db
#Import models
from app.mod_auth.models import User, Shop

from app.mod_provider.models import Schedule, Appointment

from datetime import *

# get employee's time slots for the day
# get all of the appointments that are scheduled for him
# return the time slots that are not scheduled

def check_availability_by_emplId(emplId, date, slots_required = 1):
	daily_hours = db.session.query(Schedule.start_time, Schedule.end_time).filter(Schedule.emplId == emplId, Schedule.start_time.between(datetime.combine(date, datetime.min.time()), datetime.combine(date, datetime.max.time()) )).first()
	booked = db.session.query(Appointment.date_scheduled).filter(Appointment.employeeId == emplId, Appointment.date_scheduled.between(datetime.combine(date, datetime.min.time()), datetime.combine(date, datetime.max.time()) )).all()

	interval = timedelta(minutes=20)
	print("dh ", daily_hours[0])
	print("booked ", booked)
	slot = daily_hours[0]
	print("start time: ", slot)
	time_slots = []
	while(slot < daily_hours[1]):
		if slot not in booked: #change to datetime object for comparison
			time_slots.append(slot)
		slot += interval
	
	bound = len(time_slots) - (slots_required - 1)
	for i in range(0, bound):
		for j in range(0, slots_required):
			if time_slots[i+j] != time_slots[i] + (j*interval):
				del(time_slots[i])
				break

	return time_slots

# find all available time slots for shop - @shop_id, for a date - @date

def check_availability_by_shop(shop_id, date):
	shop = Shop.query.filter_by(shopId=shop_id).first()
	employees = [u.id for u in shop.users]
	del(employees[0]) #  this is an id representing the shop, doesnt have schedules --> remove it
	print(employees)
	shop_slots = []
	for empl in employees:
		print("EMPL ID: ", empl) 
		empl_slots = check_availability_by_emplId(empl, date)
		e = {'id': id, 'availability': empl_slots}
		shop_slots.append(e)

	return shop_slots


