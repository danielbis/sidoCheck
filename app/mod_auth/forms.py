from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length, EqualTo
from flask_wtf.file import FileField, FileAllowed, FileRequired

# Define the login form (WTForms)


class LoginForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    firstname = StringField('first name', validators=[InputRequired(), Length(min=2, max=32)])
    lastname = StringField('last name', validators=[InputRequired(), Length(min=2, max=32)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


class RegisterFormShop(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    shopname = StringField('shopname', validators=[InputRequired(), Length(min=2, max=64)])
    address = StringField('address', validators=[InputRequired(), Length(min=8, max=128)])
    phonenumber = StringField('phonenumber', validators=[InputRequired(), Length(min=10, max=12)])
    image = FileField(validators=[FileAllowed(['jpg', 'png'], 'Images only!')]) #validators=[FileRequired()]
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


class RegisterFormEmployee(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    firstname = StringField('firstname', validators=[InputRequired(), Length(min=2, max=32)])
    lastname = StringField('lastname', validators=[InputRequired(), Length(min=2, max=32)])
    phonenumber = StringField('phonenumber', validators=[InputRequired(), Length(min=10, max=12)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    manager = BooleanField('manager')
    image = FileField(validators=[FileAllowed(['jpg', 'png'], 'Images only!')]) #validators=[FileRequired()]


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    password2 = PasswordField( 'Repeat Password', validators=[InputRequired(), EqualTo('password')])