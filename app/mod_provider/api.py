from flask_sqlalchemy import SQLAlchemy
from app import app, db
# Import models
from app.mod_auth.models import User, Shop

from app.mod_provider.models import Schedule, Appointment, Service

from datetime import *
from itertools import cycle

"""
    Finds employees schedule (daily_hours) for a day (@date) 
    Finds employees appointments (appointments) for a day (@date)
    Returns a list of time slots (python datetime.datetime format) that are available.
"""


def check_availability_by_employee_id(employee_id, date, slots_required=1):
    #    get work hours for that day and appointments scheduled between them for employee with id employee_id
    daily_hours = db.session.query(Schedule).filter(Schedule.employee_id == employee_id, Schedule.start_time.between(
        datetime.combine(date, datetime.min.time()), datetime.combine(date, datetime.max.time()))).first()
    appointments = db.session.query(Appointment).filter(Appointment.employee_id == employee_id,
                                                        Appointment.date_scheduled.between(
                                                            datetime.combine(date, datetime.min.time()),
                                                            datetime.combine(date, datetime.max.time()))).all()
    print("daily hours", daily_hours)
    if (daily_hours):
        booked = [a.date_scheduled for a in appointments]
        start_time = daily_hours.start_time
        end_time = daily_hours.end_time
        interval = timedelta(minutes=20)

        time_slots = []

        while (start_time < end_time):
            if start_time not in booked:
                time_slots.append(start_time)
            start_time += interval

        if len(time_slots) < slots_required:
            return []

        bound = len(time_slots) - (slots_required)
        short = []
        for i in range(0, bound):
            for j in range(0, slots_required):
                if time_slots[i + j] != time_slots[i] + (j * interval):
                    short.append(i)
                    break

        for i in short:
            del (time_slots[i])

        return time_slots
    else:
        return []


def is_slot_open(empl_id, date, datetime_object, slots_required=1):
    slots = check_availability_by_employee_id(empl_id, date, slots_required)
    print("date_time object in API ", datetime_object)
    for i in range(0, len(slots)):
        print(slots[i], " ?= ", datetime_object)
        if slots[i] == datetime_object:
            print("FOUND")
            return True
    return False


"""
	Find all available time slots for shop - @shop_id, for a date - @date
	Calls check_availability_by_employee_id for every employee and appends to 
	a global list
"""


def check_availability_by_shop(shop_id, date, slots_required=1):
    shop = Shop.query.filter_by(shop_id=shop_id).first()
    employees = [u for u in shop.users]
    del (employees[0])  # this is an id representing the shop, doesnt have schedules --> remove it
    shop_slots = []
    for empl in employees:
        empl_slots = check_availability_by_employee_id(empl.id, date, slots_required)
        e = {'id': empl.id, 'name': empl.first_name + empl.last_name, 'availability': empl_slots}
        shop_slots.append(e)

    return shop_slots


def get_next_available(shop_id, date, slots_required=1):
    slots = check_availability_by_shop(shop_id, date, slots_required)
    print('slots before filter ', slots)
    for s in slots:
        s["availability"] = list(filter(lambda x: x > datetime.now(), s["availability"]))

    print('slots after filter ', slots)

    slots = list(filter(lambda x: len(x["availability"]) > 0, slots))

    return slots


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


def get_employees_appointments_by_date(empl, date):
    appointments = db.session.query(Appointment).filter(Appointment.employee_id == empl.id,
                                                        Appointment.date_scheduled.between(
                                                            datetime.combine(date, datetime.min.time()),
                                                            datetime.combine(date, datetime.max.time()))).all()
    # empl = User.query.filter_by(id = employee_id).first()
    # list to be returned
    a_list = []
    for a in appointments:
        s = Service.query.filter_by(service_id=a.service_id).first()
        o = {
            "time": a.date_scheduled,
            "appointment_id": a.appointment_id,
            "client_first": a.client_first,
            "client_last": a.client_last,
            "client_phone": a.client_phone,
            "service_type": s.service_name,
            "service_price": s.service_price,
            "empl_id": a.employee_id,
            "empl_first": empl.first_name,
            "empl_last": empl.last_name,
            "empl_phone": empl.phone_number,
            "empl_email": empl.email
        }
        a_list.append(o)

    return a_list


def filter_history(appointments):
    time_diff = timedelta(minutes=20)
    idx = 0
    for app in appointments:
        if (idx < len(appointments) - 1):
            print("diff is ",
                  type(appointments[idx + 1].date_scheduled - appointments[idx].date_scheduled) is timedelta)
            print("time_diff ", time_diff)
            if (appointments[idx].date_scheduled - appointments[idx + 1].date_scheduled == time_diff) and (
                        appointments[idx].employee_id == appointments[idx + 1].employee_id):
                del (appointments[idx])
            idx += 1
    return appointments
