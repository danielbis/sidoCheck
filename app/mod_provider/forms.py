# Author: DANIEL BIS

from datetime import datetime, date
from flask_wtf import Form
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, widgets, DateField, SubmitField
from wtforms.fields.html5 import DateTimeField, IntegerField
from wtforms.validators import InputRequired, Length, Email
from wtforms_components import TimeField
from flask_wtf.file import FileField, FileAllowed, FileRequired



class DateForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    start_date = DateField('start_date', format="%m/%d/%Y")
    end_date = DateField('end_date', format="%m/%d/%Y")
    start_time = TimeField('start_time', format="%H:%M")
    end_time = TimeField('end_time', format="%H:%M")


class BookDateForm(FlaskForm):
    start_date = DateField('start_date', format="%m/%d/%Y")
    service = SelectField(
        'Service', coerce=int

    )
    guest_name = StringField("Customer's Name", validators=[InputRequired(), Length(min=3, max=64)])


class BookTimeForm(FlaskForm):
    time = DateTimeField("time")


class ServiceForm(FlaskForm):
    service = SelectField(
        'Service', coerce=int

    )


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.TableWidget()
    option_widget = widgets.CheckboxInput()


class AddServiceForm(FlaskForm):
    def pre_validate(self, form):
        # Prevent "not a valid choice" error
        pass

    service_length = IntegerField('Service Length', validators=[InputRequired()])
    service_price = IntegerField('Service Price', validators=[InputRequired()])
    service_name = StringField('Service Name', validators=[InputRequired()])
    employees = MultiCheckboxField(coerce=int)
    """employees = SelectField(
	        'Please choose providers', coerce=int

	)"""


class EditShopProfile(FlaskForm):
    shop_name = StringField('shop_name', validators=[InputRequired(), Length(min=2, max=64)])
    location = StringField('Address', validators=[InputRequired(), Length(min=8, max=128)])
    phone_number = StringField('phone_number', validators=[InputRequired(), Length(min=10, max=12)])
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    lastname = StringField('Last name', validators=[InputRequired(), Length(min=2, max=32)])
    firstname = StringField('First name', validators=[InputRequired(), Length(min=2, max=32)])
    image = FileField(validators=[FileAllowed(['jpg', 'png'], 'Images only!')]) #validators=[FileRequired()]

    submit = SubmitField('Update')


class UpdateShopPassword(FlaskForm):
    old_password = StringField('Current Password', validators=[InputRequired(), Length(min=8, max=80)])
    new_password = StringField('New Password', validators=[InputRequired(), Length(min=8, max=80)])
    val_password = StringField('Retype Password', validators=[InputRequired(), Length(min=8, max=80)])
    submit = SubmitField('Update')

class EditEmployeeProfile(FlaskForm):
    email= StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    phone_number= StringField('Phone Number', validators=[InputRequired(), Length(min=10, max=12)])
    image = FileField(validators=[FileAllowed(['jpg', 'png'], 'Images only!')]) #validators=[FileRequired()]
    submit= SubmitField('Update')