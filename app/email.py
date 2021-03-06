from flask_mail import Message
from app import mail
from app import app
from threading import Thread
from flask import render_template

"""
    Implementation: Abraham D'mitri Joseph

    Implements a SMTP Email server to connect sido with it's users
    Emails are sent asynchronously using threads

"""


def send_async_email(app, msg):
    with app.app_context():
        mail.connect()
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
        msg = Message(subject, sender=sender, recipients=recipients)
        msg.body = text_body
        msg.html = html_body
        Thread(target=send_async_email, args=(app, msg)).start()

"""
    Implementation: Abraham D'mitri Joseph

    Sends an email to user with a link secured by a JWT token to form for them to reset their password

"""


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[SidoCheck] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('auth/reset_password_email.txt',
                                         user=user, token=token),
               html_body=render_template('auth/reset_password_email.html',
                                         user=user, token=token))