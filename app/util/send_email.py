from app import mail
from flask_mail import Message
from flask import render_template


def send_email(subject, recipients, template, html_data):
    # send the message
    msg = Message(subject, recipients)
    msg.html = render_template(template, html_data)
    mail.send(msg)
