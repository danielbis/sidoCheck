from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField, IntegerField, SelectField
from wtforms.validators import InputRequired, Email, Length, DataRequired


# Define the login form (WTForms)

class LoginForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

class AppraisalForm(FlaskForm):
	year = IntegerField('Year', validators=[InputRequired()])
	value = IntegerField('Value', validators=[InputRequired()])
	area = IntegerField('Area', validators=[InputRequired()])
	window_protection = SelectField('Window Shutters?', choices=[("True","Yes"), ("False","No")], validators=[InputRequired()])
	surroundings = SelectField('Surroundings', choices=[("On shore","On shore"),("Suburban","Suburban"), ("City", "City"), ("Field","Field"), ("Forrest", "Forrest")], validators=[InputRequired()])
	last_roof_renew = IntegerField("If you remember, provide a year of the last roof renovation.")
	roof_wall_connection = SelectField("Type of roof to wall connection", choices=[("type1","type1"), ("type2","type2"), ("type3","type3")])

	type_of_construction = SelectField('Type of Construction', choices=[ ("Wood","Wood"), ("Masonry","Masonry") ], validators=[InputRequired()])
	#advanced
	type_of_roof_cover = SelectField("Type of roof roof cover", choices=[("type1","type1"), ("type2", "type2"), ("type3","type3")])
	type_of_windows = SelectField("Window type", choices=[("type1","type1"), ("type2","type2"), ("type3","type3")])
	