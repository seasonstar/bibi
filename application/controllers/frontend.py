# -*- coding: utf-8 -*-
from uuid import uuid4
import os
from flask import (Blueprint, current_app, request, flash, jsonify, Response,
        url_for, redirect, session, abort, render_template, make_response)
from mongoengine.queryset import Q
from flask_admin.base import MenuLink
from flask_mail import Message
from flask_babel import gettext as _
from flask_login import login_user, current_user, logout_user, \
        confirm_login, login_fresh, fresh_login_required, login_required
import application.models as Models
from application.extensions import mail, login_manager, admin
from application.services.forms.frontend import *
import application.services.jobs as Jobs
from application.utils import redirect_url
from application.controllers.admin import AuthenticatedMenuLink,\
        NotAuthenticatedMenuLink
from configs.config import TEMPLATE_DIR


frontend = Blueprint('frontend', __name__, url_prefix='')


def redirect_next():
    return redirect(url_for('admin.index'))

#@frontend.route('/', methods=['GET'])
def index():
    return make_response(open(os.path.join(
        TEMPLATE_DIR, 'index.html')).read())

@frontend.route('/api/v1/apps/<appid>/updates/check/', methods=['POST'])
@frontend.route('/api/v1/apps/<appid>/updates/check/<uuid>', methods=['POST'])
def app_update(appid, uuid=None):
    uuid = '1.1.0'
    device_app_version = request.json.get('device_app_version')
    update_available = True
    if float(device_app_version.replace('.','')) >= float(uuid.replace('.','')):
        update_available = False

    res = {'compatible_binary': True,
           'update_available': update_available,
           'update':{'uuid': uuid,
                     'url': 'http://192.168.31.134:5000/api/update/get/www_%s.zip'%uuid
                    }
          }
    return jsonify(res)

@frontend.route('/api/update/get/<filename>', methods=['GET'])
def getZip(filename):
    return make_response(open(os.path.join(
        TEMPLATE_DIR, filename)).read())

@frontend.route('/account/oauth/<sitename>', methods=['GET'])
def oauth(sitename):
    code = request.args.get('code')
    return redirect('http://m.maybi.cn/#/account/oauth/%s?code=%s' % (sitename, code))


@frontend.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.user_agent.platform in ['ipad', 'iphone', 'android']:
        return jsonify(error=u"请先登录")
    if current_user.is_authenticated:
        return redirect_next()
    if request.method == 'POST':
        email = request.form.get('email', None)
        password = request.form.get('password', None)
        if email and password:
            user, authenticated = Models.User.authenticate(email=email, password=password)
        else:
            flash(_("Please Enter the correct email and password"))
            return redirect_next()

        if user and authenticated:
            #remember = request.form.get('remember') == 'y'
            remember = True
            login_user(user, remember)
        else:
            flash(u'账号或密码不正确')

        return redirect_next()

    return render_template('admin/user/login.html')


@frontend.route('/admin/reauth', methods=['GET', 'POST'])
def reauth():
    form = ReauthForm(next=request.args.get('next'))

    if request.method == 'POST':
        user, authenticated = Models.User.authenticate(
            email=current_user.name, password=form.password.data)
        if user and authenticated:
            confirm_login()     # make the session fresh
            current_app.logger.debug('reauth: %s' % session['_fresh'])
            flash(_('Reauthenticated.'), 'success')
            return redirect('frontend.change_password')

        flash(_('Password is wrong.'), 'error')
    return render_template('admin/user/reauth.html', form=form)


@frontend.route('/admin/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('frontend.login'))


@frontend.route('/admin/signup', methods=['GET', 'POST'])
def signup():
    return redirect(url_for('frontend.signup'))


@frontend.route('/admin/confirm_reset_password', methods=['GET', 'POST'])
@frontend.route('/account/confirm_reset_password', methods=['GET', 'POST'])
def confirm_reset_password():
    if request.method == 'GET':
        if current_user.is_authenticated:
            if not login_fresh():       #force reauth user
                return login_manager.needs_refresh()
            user = current_user
        elif 'activation_key' in request.args and 'email' in request.args:
            activation_key = request.args.get('activation_key')
            email = request.args.get('email')
            user = Models.User.objects( Q(account__activation_key=activation_key) &
                             Q(account__email=email)).first()
        else:
            return Response("邮件已失效")
        form = ConfirmResetPasswordForm(activation_key=user.account.activation_key,
                email=user.account.email)
        return render_template("admin/user/confirm_reset_password.html", form=form)
    if request.method == 'POST':
        form = ConfirmResetPasswordForm()
        activation_key = form.activation_key.data
        email = form.email.data
        user = Models.User.objects( Q(account__activation_key=activation_key) &
                         Q(account__email=email)).first()
        if form.validate_on_submit():
            user.account.password = form.password.data
            user.account.activation_key = None
            user.save()
            flash(_("Your password has been changed, please log in again"),
                  "success")
            return render_template("admin/user/success_reset_password.html")

        flash(_("Fail, please confirm your password"),
              "success")
        return render_template("admin/user/confirm_reset_password.html", form=form)


@frontend.route('/admin/change_password', methods=['GET', 'POST'])
def change_password():
    user = current_user
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user.account.password = form.password.data
        user.save()

        logout_user()
        flash(_("Your password has been changed, please log in again"),
              "success")
        return redirect(url_for("frontend.login"))

    return render_template("admin/user/change_password.html", form=form)


@frontend.route('/admin/reset_password', methods=['GET', 'POST'])
def reset_password():
    form = RecoverPasswordForm()

    if form.validate_on_submit():
        user = Models.User.objects(account__email=form.email.data).first()

        if user:
            flash(_('Please see your email for instructions on '
                  'how to access your account'), 'success')

            user.account.activation_key = str(uuid4())
            user.save()

            # send recover password html
            # TODO: change project name
            url = "http://bigbang.maybi.cn/admin/confirm_reset_password?activation_key=%s&email=%s" % \
                    (user.account.activation_key, user.account.email)
            html = render_template('admin/user/_reset_password.html',
                project=current_app.config['PROJECT'], username=user.name, url=url)
            Jobs.noti.send_mail.delay([user.account.email],
                    _('Reset your password in ')+ 'Maybi',
                    html)

            return render_template('/admin/user/reset_password.html', form=form)
        else:
            flash(_('Sorry, no user found for that email address'), 'error')

    return render_template('admin/user/reset_password.html', form=form)

@frontend.route("/admin/secret")
@fresh_login_required
def secret():
    if current_user.is_authenticated:
        print (current_user)
    return jsonify(success='OK')


admin.add_link(MenuLink(name='Home', url="/admin"))
admin.add_link(NotAuthenticatedMenuLink(name="Login", endpoint="frontend.login"))
admin.add_link(AuthenticatedMenuLink(name="Logout", endpoint="frontend.logout"))
admin.add_link(AuthenticatedMenuLink(name="Change Password", endpoint="frontend.change_password"))
