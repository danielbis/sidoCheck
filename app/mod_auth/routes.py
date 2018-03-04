#flask dependencies
from flask import Flask, render_template, redirect, url_for, Blueprint, request, session
from flask_wtf import FlaskForm 
from app.mod_auth.forms import RegisterForm, LoginForm, AppraisalForm
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError
 
#import database object from app module 
from app import db, login_manager

from app import app
#Import module models containing User
from app.mod_auth.models import User

#Define the blueprint: 'auth', sets its url prefix: app.url/auth
mod = Blueprint('mod_auth', __name__, url_prefix = "/auth")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#set route and accepted methods
@mod.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('mod_auth.dashboardcustomer'))
        return '<h1>Invalid username or password</h1>'
    return render_template('auth/login.html', form=form)

@mod.route('/loginguest', methods=['POST'])
def loginguest():
    if request.method == 'POST' and request.form["guest"] == "guest":
        user = User.query.filter_by(email="guest@email.com").first()
        if user:
            if check_password_hash(user.password, "guestPass123"):
                login_user(user)
                return redirect(url_for('mod_auth.dashboardcustomer'))
        return '<h1>Invalid username or password</h1>'
    return render_template('auth/login.html', form=form) 


@mod.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        try:
            new_user = User(email=form.email.data, password=hashed_password)
            #check if email is taken
            #user = User.query.filter_by(email=form.email.data).first()
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return '<h1>This email address is already taken.</h1>'
        return '<h1>New user has been created!</h1>'

    return render_template('auth/signup.html', form=form)
"""
@mod.route('/dashboard')
@login_required
def dashboard():
    return render_template('auth/dashboard.html', name=current_user.first_name)
"""
@mod.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@mod.route('/dashboardcustomer', methods=['GET', 'POST'])
@login_required
def dashboardcustomer():
    form = AppraisalForm()
    
    if form.is_submitted():
        print ("submitted")
        print(form.errors)

    if form.validate_on_submit():
        print("validated")
        params_object = {
            "year": form.year.data,
            "value": form.value.data,
            "area": form.area.data,
            "window_protection": form.window_protection.data,
            "surroundings": form.surroundings.data,
            "last_roof_renew": form.last_roof_renew.data,
            "roof_wall_connection": form.roof_wall_connection.data,
            "type_of_roof_cover": form.type_of_roof_cover.data,
            "type_of_construction": form.type_of_construction.data,
            "type_of_windows": form.type_of_windows.data
        }
        session['params_object'] = params_object
        return redirect(url_for('mod_auth.estimation'))

    return render_template('customer/dashboard_customer.html', name=current_user.email, form=form)

@mod.route('/estimation', methods=['GET', 'POST'])
@login_required
def estimation():
    return render_template('customer/estimation.html', params=current_user.email)





