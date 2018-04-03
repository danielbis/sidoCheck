# Author: DANIEL BIS

from datetime import datetime, date
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, SelectField
from wtforms.fields.html5 import DateTimeField
from wtforms.validators import InputRequired, Length, Email


class DateForm(FlaskForm):
    # email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    dt = DateField('start_time')
# end_time = DateTimeField('end_time')


class DateForm_v2(FlaskForm):
    """docstring for DateForm_v2"""
    dt = DateField('DatePicker', format='%Y-%m-%d')


class EditProfile(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    phone_number = StringField('Phone Number', validators=[InputRequired(), Length(min=10, max=12)])
    submit = SubmitField('Update')


class UpdatePassword(FlaskForm):
    old_password = StringField('Current Password', validators=[InputRequired(), Length(min=8, max=80)])
    new_password = StringField('New Password', validators=[InputRequired(), Length(min=8, max=80)])
    val_password = StringField('Retype Password', validators=[InputRequired(), Length(min=8, max=80)])
    submit = SubmitField('Update')


class ServiceForm(FlaskForm):
    service = SelectField(
        'Service', coerce=int

    )
