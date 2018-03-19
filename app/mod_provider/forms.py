# Author: DANIEL BIS

from datetime import datetime, date
from flask_wtf import FlaskForm 
from wtforms import StringField, SelectField
from wtforms.fields.html5 import  DateTimeField
from wtforms.validators import InputRequired, Length, Email

class DateForm(FlaskForm):
	email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
	start_time = DateTimeField('start_time')
	end_time = DateTimeField('end_time')


class ServiceForm(FlaskForm):
    service = SelectField(
        'Service', coerce=int
        
    )