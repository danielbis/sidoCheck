from app import db
from app.mod_auth.models import User, Shop
from app.mod_provider.models import Schedule, Appointment
from app.mod_provider.api import check_availability_by_employee_id, check_availability_by_shop, get_employees_appointments_by_date
from datetime import *

d = date.today()
#employee availability test
es= check_availability_by_employee_id(23, d)
#print(es)

ap = get_employees_appointments_by_date(23, d)
print(ap)
"""
#shop availability test
sa = check_availability_by_shop(38, d)
print(sa)
"""