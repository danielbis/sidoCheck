# Author: DANIEL BIS

# flask dependencies
import os
from flask import Flask, render_template, redirect, url_for, Blueprint
from flask_wtf import FlaskForm
from app.mod_auth.forms import RegisterForm, RegisterFormShop, RegisterFormEmployee, LoginForm
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from app import db, login_manager
from app import app
# Import module models containing User
from app.mod_auth.models import User, Shop

# Define the blueprint: 'auth', sets its url prefix: app.url/auth
mod = Blueprint('mod_auth', __name__, url_prefix="/auth")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@mod.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                if user.role == "customer":  # check if customer or provider
                    return redirect(url_for('mod_customer.dashboardcustomer'))
                else:
                    return redirect(url_for('mod_provider.dashboardprovider'))

        return '<h1>Invalid username or password</h1>'

    return render_template('auth/login.html', form=form)


# Daniel Bis and Christian Pileggi
@mod.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        try:
            new_user = User(firstname=form.firstname.data, lastname=form.lastname.data, email=form.email.data,
                            password=hashed_password, role="customer")
            # check if email is taken
            # user = User.query.filter_by(email=form.email.data).first()
            db.session.add(new_user)
            db.session.commit()

        except IntegrityError:
            db.session.rollback()
            return '<h1>This email address is already taken.</h1>'
        return redirect(url_for("mod_auth.login"))
    return render_template('auth/signup.html', form=form)


# Daniel Bis and Christian Pileggi
# Register a service provider aka shop
@mod.route('/signupshop', methods=['GET', 'POST'])
def signup_shop():
    form = RegisterFormShop()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        try:
            f = form.image.data
            if f is not None:
                filename = secure_filename(f.filename)
                path = os.path.join(app.config['UPLOADED_IMAGES_DEST'], filename)
                f.save(path)
            else:
                filename = 'city.jpg'

            new_user = User(firstname=form.shop_name.data, lastname=form.shop_name.data,
                            phone_number=form.phone_number.data, email=form.email.data, password=hashed_password,
                            role="shop")
            new_shop = Shop(shop_name=form.shop_name.data, location=form.address.data,
                            img=filename)  # storing only the filename since all of the images are in the same directory
            # db.session.add(new_shop)
            db.session.add(new_shop)
            new_shop.users.append(new_user)

            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return '<h1>This email address is already taken.</h1>'
        return render_template('auth/login.html', form = LoginForm())

    return render_template('auth/signup_shop.html', form=form)

#write a function that not only ensures that login is required
#but also checks if employee and if manager
#@login_required
@mod.route('/signupemployee', methods=['GET', 'POST'])
def signup_employee():
    form = RegisterFormEmployee()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')

        try:
            managerCheck = 0
            if form.manager.data:
                managerCheck = 1
            f = form.image.data
            if f is not None:
                filename = secure_filename(f.filename)
                path = os.path.join(app.config['UPLOADED_IMAGES_DEST'], filename)
                f.save(path)
            else:
                filename = 'city.jpg'

            new_user = User(firstname=form.firstname.data, lastname=form.lastname.data, email=form.email.data,
                            phone_number=form.phone_number.data, password=hashed_password, role="employee",
                            manager=managerCheck, img=filename)

            # quering for shop where the current user is a manager
            temp_user = User.query.filter_by(id=current_user.id).first()
            employer_id = temp_user.shop_id
            employer = Shop.query.filter_by(shop_id=employer_id).first()
            db.session.add(new_user)
            # making user an employee
            # append a shop for future references
            employer.users.append(new_user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return '<h1> This email is already taken </h1>'
        return redirect(url_for("mod_provider.dashboardprovider"))
        # return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('auth/signup_employee.html', form=form)


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
