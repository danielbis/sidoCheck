from flask_sqlalchemy  import SQLAlchemy
from app import app, db
#Import models
from app.mod_auth.models import User, Shop

from app.mod_provider.models import Schedule, Appointment, Service

from datetime import *

"""
	Finds employees schedule (daily_hours) for a day (@date) 
	Finds employees appointments (appointments) for a day (@date)
	Returns a list of time slots (python datetime.datetime format) that are available.
"""

def check_availability_by_emplId(emplId, date, slots_required = 1):
	
	# get work hours for that day and appointments scheduled between them for employee with id emplId
	daily_hours = db.session.query(Schedule).filter(Schedule.emplId == emplId, Schedule.start_time.between(datetime.combine(date, datetime.min.time()), datetime.combine(date, datetime.max.time()) )).first()
	appointments = db.session.query(Appointment).filter(Appointment.employeeId == emplId, Appointment.date_scheduled.between(datetime.combine(date, datetime.min.time()), datetime.combine(date, datetime.max.time()) )).all()
	
	booked = [a.date_scheduled for a in appointments]
	start_time = daily_hours.start_time
	end_time = daily_hours.end_time
	interval = timedelta(minutes=20)
	
	"""
		Debuggin prints 

	print("daily_hours.start_time ", daily_hours.start_time, " type is datetime: ", type(daily_hours.start_time) is datetime  )
	print("start time is ", start_time, " type is datetime: ", type(start_time) is datetime)
	print("end time is ", end_time, " type is datetime: ", type(end_time) is datetime)
	print("booked[0] is ",booked[0], "t ype is datetime ", type(booked[0]) is datetime)
	"""
	
	time_slots = []

	while(start_time < end_time):
		if start_time not in booked: 
			time_slots.append(start_time)
		start_time += interval
	
	if len(time_slots) < slots_required:
		return []
	print("slots required is ", slots_required, "number of slots: ", len(time_slots))


	bound = len(time_slots) - (slots_required)
	print("bound is: ", bound)
	short = []
	for i in range(0, bound):
		for j in range(0, slots_required):
			if time_slots[i+j] != time_slots[i] + (j*interval):
				short.append(i)
				break

	for i in short:
		del(time_slots[i])

	return time_slots

def is_slot_open(empl_id, date, datetime_object, slots_required=1):
	print("is_open? : ", datetime_object )
	slots = check_availability_by_emplId(empl_id, date, slots_required)
	for i in range(0,len(slots)):
		print(slots[i])
		if slots[i] == datetime_object:
			print("FOUND")
			return True
	
	return False


"""
	Find all available time slots for shop - @shop_id, for a date - @date
	Calls check_availability_by_emplId for every employee and appends to 
	a global list
"""
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


"""
	Finds Employees Appointments for a day (@date)
	and returns a list of dictionaries in format:

	{
		time: datetime.datetime
		clients_first: str 
		clients_last: str
		clients_phone: str
		clients_email: str
		service_type: str
		service_price: int
		employee_id: int
		empl_first: str
		empl_last: str
		empl_phone: string
		empl_email: str
	}

"""
def get_employees_appointments_by_date(emplId, date):

	appointments = db.session.query(Appointment).filter(Appointment.employeeId == emplId, Appointment.date_scheduled.between(datetime.combine(date, datetime.min.time()), datetime.combine(date, datetime.max.time()) )).all()
	empl = User.query.filter_by(id = emplId).first()
	# list to be returned
	a_list = []
	for a in appointments:
		s = Service.query.filter_by(service_id=a.service_id).first()
		o = {
			"time": a.date_scheduled,
			"client_first": a.client_first,
			"client_last": a.client_last, 
			"client_phone": a.client_phone, 
			"service_type": s.service_name, 
			"service_price": s.service_price, 
			"empl_id": a.employeeId, 
			"empl_first": empl.first_name,
			"empl_last": empl.last_name,
			"empl_phone": empl.phonenumber, 
			"empl_email": empl.email
		}
		a_list.append(o)

	return a_list




