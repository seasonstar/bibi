# encoding: utf-8
import time
from flask import current_app
from application.cel import celery

@celery.task
def send_mail(recipients, title, message, sender='notify@maybi.cn', cc=None):
    from flask_mail import Message
    from application.extensions import mail

    msg = Message(title, recipients=recipients)
    if sender:
        msg.sender = sender
    if cc:
        msg.cc=cc
    msg.html = message
    mail.send(msg)
    return True
