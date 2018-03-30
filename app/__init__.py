#Author: DANIEL BIS

# Import flask and template operators
from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
# Import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
#import login manager 
from flask_login import LoginManager, current_user, login_required
from flask.ext.uploads import UploadSet, configure_uploads, IMAGES
# Define the WSGI application object
app = Flask(__name__)
Bootstrap(app)
# Configurations
app.config.from_object('config')
app.config['UPLOADED_IMAGES_DEST'] = 'app/static/img'

images = UploadSet('images', IMAGES)
configure_uploads(app, images)


# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)


# Define the database object which is imported
# by modules and controllers


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import a module / component using its blueprint handler variable (mod_auth)
from app.mod_auth.routes import mod
from app.mod_provider.routes import provider_mod
from app.mod_customer.routes import customer_mod

# Register blueprint(s)
app.register_blueprint(mod_auth.routes.mod)
app.register_blueprint(mod_provider.routes.provider_mod)
app.register_blueprint(mod_customer.routes.customer_mod)
# app.register_blueprint(xyz_module)
# ..


from flask_dance.contrib.google import make_google_blueprint, google
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
import os
import sys
from sqlalchemy.orm.exc import NoResultFound


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app.secret_key = "supersekrit"


blueprint = make_google_blueprint(
    client_id="91401939367-hau5et1aki5vdnf243cbug7fv28ub4l4.apps.googleusercontent.com",
    client_secret="spVfLRtr9dR7n3Y5NGcEMJ0B",
    scope=["profile", "email"]
)
app.register_blueprint(blueprint, url_prefix="/login")


from flask_dance.consumer.backend.sqla import OAuthConsumerMixin, SQLAlchemyBackend
from app.mod_auth.models import OAuth, User
from flask_dance.consumer import oauth_authorized, oauth_error

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

blueprint.backend = SQLAlchemyBackend(OAuth, db.session, user=current_user)

@oauth_authorized.connect_via(blueprint)
def google_logged_in(blueprint, token):
    if not token:
        flash("Failed to log in with Google.", category="error")
        return False

    resp = blueprint.session.get("/oauth2/v2/userinfo")
    if not resp.ok:
        msg = "Failed to fetch user info from Google."
        flash(msg, category="error")
        return False

    print(resp, file=sys.stdout)

    google_info = resp.json()
    google_user_id = str(google_info["id"])

    # Find this OAuth token in the database, or create it
    query = OAuth.query.filter_by(
        provider=blueprint.name,
        provider_user_id=google_user_id,
    )
    try:
        oauth = query.one()
    except NoResultFound:
        oauth = OAuth(
            provider=blueprint.name,
            provider_user_id=google_user_id,
            token=token,
        )

    if oauth.user:
        login_user(oauth.user)
        flash("Successfully signed in with Google.")
        if oauth.user.role == "customer":  # check if customer or provider
            return redirect(url_for('mod_customer.dashboardcustomer'))
        else:
            return redirect(url_for('mod_provider.dashboardprovider'))


    else:
        print("in else ", file=sys.stdout)
        print(resp.json, file=sys.stdout)

        # Create a new local user account for this user
        user = User(
            # Remember that `email` can be None, if the user declines
            # to publish their email address on GitHub!
            email=google_info["email"],
            firstname=google_info["given_name"],
            lastname=google_info["family_name"],
            password="0",
            role="customer"
        )
        # Associate the new local user account with the OAuth token
        oauth.user = user
        # Save and commit our database models
        db.session.add_all([user, oauth])
        db.session.commit()
        # Log in the new local user account
        login_user(user)
        flash("Successfully signed in with GitHub.")
        return redirect(url_for('mod_customer.dashboardcustomer'))
    # Disable Flask-Dance's default behavior for saving the OAuth token
    print("end", file=sys.stdout)
    return False


# notify on OAuth provider error
@oauth_error.connect_via(blueprint)
def google_error(blueprint, error, error_description=None, error_uri=None):
    msg = (
        "OAuth error from {name}! "
        "error={error} description={description} uri={uri}"
    ).format(
        name=blueprint.name,
        error=error,
        description=error_description,
        uri=error_uri,
    )
    flash(msg, category="error")


#Home page
@app.route('/')
def index():
    return redirect(url_for("mod_auth.login"))





# Sample HTTP error handling
"""@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404"""

# Build the database:
# This will create the database file using SQLAlchemy
#db.drop_all()


db.create_all()