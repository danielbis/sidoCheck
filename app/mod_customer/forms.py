# Author: DANIEL BIS

from datetime import datetime, date
from flask_wtf import FlaskForm 
from wtforms import StringField
from wtforms.fields.html5 import  DateTimeField
from wtforms.validators import InputRequired, Length, Email
from wtforms import DateField

class DateForm(FlaskForm):
	#email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
	dt = DateField('start_time')
	#end_time = DateTimeField('end_time')

class DateForm_v2(FlaskForm):
	"""docstring for DateForm_v2"""
	dt = DateField('DatePicker', format='%Y-%m-%d')

		
