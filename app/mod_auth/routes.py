from flask import Flask, render_template, redirect, url_for, Blueprint, flash
from flask_wtf import FlaskForm 
from app.mod_auth.forms import RegisterForm, RegisterFormShop, RegisterFormEmployee, LoginForm, ResetPasswordRequestForm, ResetPasswordForm
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from flask_login import login_user, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from app import db, login_manager, login_required
from app import app
# Import module models containing User
from app.mod_auth.models import User, Shop
from app.mod_customer.routes import dashboardcustomer
from app.email import send_password_reset_email
import cloudinary as Cloud
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url

# Define the blueprint: 'auth', sets its url prefix: app.url/auth
mod = Blueprint('mod_auth', __name__, url_prefix="/auth")

Cloud.config.update = ({
    'cloud_name': 'sidoproject',
    'api_key': '848925646618136',
    'api_secret': 'HelekvosM3FQEAPsY6gAlJhiedk'
})
"""
    
    load_user function enables us to use a current_user object globally. 
    Because of that we can access user that is currently authenticated.
    
"""


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


"""
    Implementation: Daniel Bis, Abraham D'mitri Joseph
    
    Authenticates the user given his/her credentials. 
    If credentials are correct, renders appropriate template depending if user is a customer 
    or shop (provider).
    
    :returns render_template()
    
"""


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
        flash("Invalid username or password")

    return render_template('auth/login.html', form=form)


"""
    Implementation: Daniel Bis, Christian Pileggi

    Registers the user of type customer. 
    If registration is successful:
        :returns render_template()
    else:
        :Flashes an error message

"""


@mod.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        try:
            hashed_password = generate_password_hash(form.password.data, method='sha256')
            new_user = User(first_name=form.firstname.data, last_name=form.lastname.data, email=form.email.data,
                            password=hashed_password, role="customer")
            # check if email is taken
            # user = User.query.filter_by(email=form.email.data).first()
            db.session.add(new_user)
            db.session.commit()

        except IntegrityError:
            db.session.rollback()
            flash("Email taken")
        return redirect(url_for("mod_auth.login"))
    return render_template('auth/signup.html', form=form)

"""
    Implementation: Daniel Bis, Christian Pileggi, Abraham D'mitri Joseph

    Registers the user of type shop. 
    If registration is successful:
        :returns render_template()
    else:
        :Flashes a message notifying user about the problem.

"""


@mod.route('/signupshop', methods=['GET', 'POST'])
def signup_shop():
    form = RegisterFormShop()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        try:
            f = form.image.data
            if f is not None:
                filename = secure_filename(f.filename)
                #path = os.path.join(app.config['UPLOADED_IMAGES_DEST'], filename)
                uploaded = upload(f)
                print(uploaded['public_id'])
            else:
                uploaded = upload('../static/img/city.jpg')
                print('else ', uploaded['public_id'])

            new_user = User(first_name=form.shop_name.data, last_name=form.shop_name.data,
                            phone_number=form.phone_number.data, email=form.email.data, password=hashed_password,
                            role="shop")
            new_shop = Shop(shop_name=form.shop_name.data, location=form.address.data,
                            img=uploaded['public_id'])  # storing only the filename since all of the images are in the same directory
            # db.session.add(new_shop)
            db.session.add(new_shop)
            new_shop.users.append(new_user)

            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Email taken")
        return render_template('auth/login.html', form=LoginForm())

    return render_template('auth/signup_shop.html', form=form)


"""
    Implementation: Daniel Bis, Christian Pileggi, Abraham D'mitri Joseph

    Registers the user of type employee. 
    If registration is successful:
        :returns render_template()
    else:
        :Flashes a message notifying user about the problem.

"""


@login_required('shop')
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
                #path = os.path.join(app.config['UPLOADED_IMAGES_DEST'], filename)
                uploaded = upload(f)
                print(uploaded['public_id'])
            else:
                uploaded = {}
                uploaded['public_id'] = ""
                print('else ', uploaded['public_id'])

            new_user = User(first_name=form.firstname.data, last_name=form.lastname.data, email=form.email.data,
                            phone_number=form.phone_number.data, password=hashed_password, role="employee",
                            manager=managerCheck, img=uploaded['public_id'])

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
            flash("Email taken")
        return redirect(url_for("mod_provider.dashboardprovider"))
    return render_template('auth/signup_employee.html', form=form)


"""
    Implementation:  Abraham D'mitri Joseph

    Allows user to request a password request email
    If successful:
        :An email is sent to the user to commence the reset process and redirects to login page
    else:
        :If user is already authenticated redirects to their landing page, Does not inform user if the email
        they're entering is valid or not for security purposes

"""


@mod.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        user = current_user
        if user.role == "customer":  # check if customer or provider
            return redirect(url_for('mod_customer.dashboardcustomer'))
        else:
            return redirect(url_for('mod_provider.dashboardprovider'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('mod_auth.login'))
    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)


"""
    Implementation:  Abraham D'mitri Joseph

    Uses JWT token to authenticate user from email and allows user to submit a new password
    If successful:
        :Password is changed and user is redirected to login page
    else:
        :If user is already authenticated redirects to their landing page
        If token does not match the user is redirected to login page.

"""


@mod.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):

    if current_user.is_authenticated:
        user = current_user
        if user.role == "customer":  # check if customer or provider
            return redirect(url_for('mod_customer.dashboardcustomer'))
        else:
            return redirect(url_for('mod_provider.dashboardprovider'))

    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('mod_auth.login'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('mod_auth.login'))
    return render_template('auth/reset_password.html', user=user, form=form)

"""
    Implementation: Daniel Bis, Christian Pileggi, Abraham D'mitri Joseph

    Logs out a user of any type.
    Removes credentials from the session. 
    If successful:
        :returns redirect('index')
    else:
        :returns an html with a message notifying user about the problem. 

"""


@mod.route('/logout')
@login_required('ANY')
def logout():
    logout_user()
    return redirect(url_for('index'))
