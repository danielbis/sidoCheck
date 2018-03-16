from app import db
from app.mod_auth.models import User, Shop
from app.mod_provider.models import Schedule, Appointment
from app.mod_provider.api import check_availability_by_emplId, check_availability_by_shop
from datetime import *

d = date.today()
#employee availability test
es= check_availability_by_emplId(455, d)
print(es)

#shop availability test
sa = check_availability_by_shop(38, d)
print(sa)
