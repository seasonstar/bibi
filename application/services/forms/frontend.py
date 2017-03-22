# -*- coding: utf-8 -*-

from flask import Markup

from flask_wtf import Form
from wtforms.fields import (HiddenField, BooleanField, TextField,
                            PasswordField, SubmitField)
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError

from application.utils import (PASSWORD_LEN_MIN, PASSWORD_LEN_MAX,
        USERNAME_LEN_MIN, USERNAME_LEN_MAX)
import application.models as Models


class LoginForm(Form):
    next = HiddenField()
    login = TextField(u'Username or email', [DataRequired()])
    password = PasswordField('Password', [DataRequired(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)])
    remember = BooleanField('Remember me')
    submit = SubmitField('Sign in')


class SignupForm(Form):
    next = HiddenField()
    email = EmailField(u'Email', [DataRequired(), Email()],
            description=u"What's your email address?")
    password = PasswordField(u'Password', [DataRequired(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)],
            description=u'%s characters or more! Be tricky.' % PASSWORD_LEN_MIN)
    name = TextField(u'Choose your username', [DataRequired(), Length(USERNAME_LEN_MIN, USERNAME_LEN_MAX)],
            description=u"Don't worry. you can change it later.")
    agree = BooleanField(u'Agree to the ' +
        Markup('<a target="blank" href="/terms">Terms of Servic</a>'), [DataRequired()])
    submit = SubmitField('Sign up')

    def validate_name(self, field):
        if Models.User.objects(name=field.data).first() is not None:
            raise ValidationError(u'This username is taken')

    def validate_email(self, field):
        if Models.User.objects(account__email=field.data).first() is not None:
            raise ValidationError(u'This email is taken')


class RecoverPasswordForm(Form):
    email = EmailField(u'Your email', [Email()])
    submit = SubmitField('Send instructions')


class ChangePasswordForm(Form):
    password = PasswordField(u'Password', [DataRequired()])
    password_again = PasswordField(u'Password again', [EqualTo('password', message="Passwords don't match")])
    submit = SubmitField('Save')

class ConfirmResetPasswordForm(Form):
    activation_key = HiddenField()
    email = HiddenField()
    password = PasswordField(u'Password', [DataRequired()])
    password_again = PasswordField(u'Password again', [EqualTo('password', message="Passwords don't match")])
    submit = SubmitField('Save')


class ReauthForm(Form):
    next = HiddenField()
    password = PasswordField(u'Password', [DataRequired(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)])
    submit = SubmitField('Reauthenticate')
