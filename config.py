#Author: DANIEL BIS, ABRAHAM D'MITRI JOSEPH
# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

# Define the database - we are working with
# SQLite for this example
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = os.environ["SIDOCHECK_DB"]
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
CSRF_SESSION_KEY = os.environ.get("SECRET")

# Secret key for signing cookies

MAIL_SERVER = os.environ.get('MAIL_SERVER')
MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
ADMINS = ['sidocheckdev@gmail.com']

SECRET_KEY = os.environ["SECRET"]

