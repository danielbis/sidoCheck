from flask_sqlalchemy import SQLAlchemy
from app import app, db
# Import models
from app.mod_auth.models import User, Shop

from app.mod_provider.models import Schedule, Appointment, Service

from datetime import *
from itertools import cycle

"""
    Parameters: 
     @employee_id (integer)
     @date (datetime.date object)
     @service_length (integer)
     
    Finds employees schedule (daily_hours) for a day (@date) 
    Finds employees appointments (appointments) for a day (@date)
    Returns a list of time slots (python datetime.datetime format) that are available.
    
    :returns a list of datetime objects representing employees available time slots for that given service_length
"""


def check_availability_by_employee_id(employee_id, date, service_length):
    #    get work hours for that day and appointments scheduled between them for employee with id employee_id
    daily_hours = db.session.query(Schedule).filter(Schedule.employee_id == employee_id, Schedule.start_time.between(
        datetime.combine(date, datetime.min.time()), datetime.combine(date, datetime.max.time()))).first()
    appointments = db.session.query(Appointment).filter(Appointment.employee_id == employee_id,
                                                        Appointment.date_scheduled.between(
                                                            datetime.combine(date, datetime.min.time()),
                                                            datetime.combine(date, datetime.max.time()))).all()

    print("daily hours", daily_hours)
    if (daily_hours):
        slots_required = int(service_length / daily_hours.interval_length)
        booked = [a.date_scheduled for a in appointments]
        start_time = daily_hours.start_time
        end_time = daily_hours.end_time
        interval = timedelta(minutes=20)
        print('interval is, ', interval)
        time_slots = []
        print('start time is,  ', type(start_time) is datetime)
        while start_time <= end_time - slots_required * interval:
            if start_time not in booked:
                switch = True
                for i in range(1, slots_required):
                    if start_time + i * interval in booked:
                        switch = False
                if switch:
                    time_slots.append(start_time)
                    start_time += slots_required * interval
                else:
                    start_time += interval
            else:
                start_time += interval

        return time_slots
    else:
        return []


"""
    Parameters: 
    @empl_id (integer)
    @date (datetime.date object)
    @datetime_object (datetime.datetime object)
    @service_length (integer)
    
    Calls the check_availability_by_employee_id().
    If given datetime_object in the returned list:
        :returns True
    else 
        :returns False

"""


def is_slot_open(empl_id, date, datetime_object, service_length):
    slots = check_availability_by_employee_id(empl_id, date, service_length)
    print("date_time object in API ", datetime_object)
    for i in range(0, len(slots)):
        print(slots[i], " ?= ", datetime_object)
        if slots[i] == datetime_object:
            print("FOUND")
            return True
    return False


"""
    Parameters:
    @shop_id (integer)
    @date (datetime.date object)
    @service_length (integer)
   
    Find all available time slots for shop - @shop_id, for a date - @date
    Calls check_availability_by_employee_id for every employee and appends to 
    a global list
    
    :returnsa list of datetime objects representing shops available time slots for that given service_length
"""


def check_availability_by_shop(shop_id, date, service_length):
    shop = Shop.query.filter_by(shop_id=shop_id).first()
    employees = [u for u in shop.users]
    del (employees[0])  # this is an id representing the shop, doesnt have schedules --> remove it
    shop_slots = []
    for empl in employees:
        empl_slots = check_availability_by_employee_id(empl.id, date, service_length)
        e = {'id': empl.id, 'name': empl.first_name + " " + empl.last_name, 'availability': empl_slots}
        shop_slots.append(e)

    return shop_slots


"""
    Parameters:
    @shop_id (integer)
    @date (datetime.date object)
    @service_length (integer)

    Finds the first available time slot for shop - @shop_id, for a date - @date
    Calls check_availability_by_employee_id for every employee and appends to 
    a global list

    :returns list of datetime objects representing shops available time slots for that given service_length
"""


def get_next_available(shop_id, date, service_length):
    slots = check_availability_by_shop(shop_id, date, service_length)
    print('slots before filter ', slots)
    for s in slots:
        s["availability"] = list(filter(lambda x: x > datetime.now(), s["availability"]))

    print('slots after filter ', slots)

    slots = list(filter(lambda x: len(x["availability"]) > 0, slots))

    return slots


"""
    :parameter:
    @empl (object of user class)
    @date (datetime.date object)

    Finds Employees Appointments for a day (@date)
    and returns a list of dictionaries in format:

    {
        time: datetime.datetime,
        clients_first: str,
        clients_last: str,
        clients_phone: str,
        clients_email: str,
        service_type: str,
        service_price: int,
        employee_id: int,
        empl_first: str,
        empl_last: str,
        empl_phone: string,
        empl_email: str
    }
    
    :returns list of employee's appointments for the given date

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


"""
        :parameter:
        @appointments (list of appointments)
        
        Functions filter the appointments making sure that slots in the table that correspond to one 
        appointment but take more then one entry in the table are represented as a single object in the list.
        
        :returns list of appointments 
"""


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


"""
    :parameter:
    @shop_id (integer)
    @d (datetime.date object)
    
    Query Database for a list of schedules for all employees for a given shop.
    :returns  [(User, Schedule)]
"""


def get_schedules(shop_id, d):
    schedules_list = db.session.query(Schedule.start_time, Schedule.end_time, User.first_name, User.last_name,
                                      User.email).filter(User.id == Schedule.employee_id).filter(
        User.shop_id == shop_id).filter(
        Schedule.start_time.between(
            datetime.combine(d, datetime.min.time()),
            datetime.combine(d, datetime.max.time()))).all()
    sl = []
    for row in schedules_list:
        row_as_list = list(row)
        row_as_list[0] = row_as_list[0].time().strftime('%I:%M%p')
        row_as_list[1] = row_as_list[1].time().strftime('%I:%M%p')
        sl.append(row_as_list)

    return sl
