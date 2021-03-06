#Author: DANIEL BIS, ABRAHAM D'MITRI JOSEPH
# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

# Define the database - we are working with
# SQLite for this example
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = 'postgres://iozdirrc:YJg3fp0JDOpNk5-I_atnkPxFol6vVBEU@baasu.db.elephantsql.com:5432/iozdirrc'

#os.environ["SIDOCHECK_DB"]
# DANIEL YOUR PATH IS 'postgresql://localhost/cutcheck' SET ENV VARS ASAP
DATABASE_CONNECT_OPTIONS = {}
PREFERRED_URL_SCHEME = 'https'

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = False

# Use a secure, unique and absolutely secret key for
# signing the data. 
CSRF_SESSION_KEY = "SECRET"
#os.environ.get("SECRET")

# Secret key for signing cookies

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = 1
MAIL_USERNAME = 'sidocheckdev@gmail.com'
MAIL_PASSWORD = 's1dos1do'
ADMINS = ['sidocheckdev@gmail.com']

SECRET_KEY = "SECRET"


#os.environ["SECRET"]


