#0 -*- coding: utf-8 -*-
import json
import re
from uuid import uuid4

from datetime import datetime
from collections import defaultdict
from mongoengine.queryset import Q

from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required
from flask_babel import gettext as _
from application.services.cart import entry_info_from_ids
from application.services.price import cal_order_price, FakeCart
import application.services.jobs as Jobs
import application.services.json_tmpl as Json
from configs.price import PRICE_FN
import application.models as Models
from application.utils import paginate


user = Blueprint('user', __name__, url_prefix='/api/users')


@user.route('/session_key', methods=['GET'])
def session_key():
    return jsonify(message='OK', session_key=get_session_key())

@user.route('/permissions', methods=['GET'])
def permissions():
    if not current_user.is_authenticated:
        return jsonify(message="Failed")

    roles = current_user.roles
    return jsonify(message="OK", roles=roles)

@user.route('/coupons/by_entries', methods=['POST'])
@login_required
def coupon_by_entries():
    data = request.json
    entry_ids = data.get('entries')
    if not entry_ids:
        return jsonify(message='Failed', error=_(u'Please choose the item'))

    entries_info = entry_info_from_ids(entry_ids)

    order = FakeCart(entries_info,
            user=current_user._get_current_object())

    o = cal_order_price(order)
    c_jsons = []
    for c in current_user.wallet.consumable_coupons:
        if c.is_expired:
            continue
        c_json = c.to_json()
        c_json['can_apply'] = (c.coupon.is_effective() and
                               c.coupon.can_apply(o))

        c_json['saving'] = PRICE_FN.ORDER_COUPON[c.coupon.coupon_type](
            o, c.coupon)[1]


        c_jsons.append(c_json)

    return jsonify(message='OK',
                   consumable_coupons=c_jsons)

@user.route('/coupons/by_order', methods=['POST'])
@login_required
def coupon_by_order():
    data = request.json
    order_id = data.get('order_id')
    if not order_id:
        return jsonify(message='Failed', error=_(u'Please choose order'))

    order = Models.Order.objects(id=order_id).first()
    o = cal_order_price(order)
    c_jsons = []
    for c in current_user.wallet.consumable_coupons:
        if c.is_expired:
            continue
        c_json = c.to_json()
        c_json['can_apply'] = (c.coupon.is_effective() and
                               c.coupon.can_apply(o))

        c_json['saving'] = PRICE_FN.ORDER_COUPON[c.coupon.coupon_type](
            o, c.coupon)[1]


        c_jsons.append(c_json)

    return jsonify(message='OK',
                   consumable_coupons=c_jsons)


@user.route('/account/change_password', methods=['POST'])
@login_required
def change_password():
    user = current_user
    password = request.json.get('password', '')
    password_confirm = request.json.get('password_confirm','')
    if not password.isalnum():
        # 密码包含非法字符
        return jsonify(message='Failed',
                       error=_(u'Password contains illegal characters'))
    if len(password) < 6:
        # 密码长度不足
        return jsonify(message='Failed', error=_(u'Password is too short'))
    if password != password_confirm:
        return jsonify(message='Failed', error=_(u'Password is inconsistent'))

    user.account.password = password
    user.save()

    return jsonify(message='OK')

@user.route('/account/reset_password', methods=['POST'])
def reset_password():
    email = request.json.email
    user = Models.User.objects(account__email=email).first()

    if user:
        user.account.activation_key = str(uuid4())
        user.save()

        url = "http://m.maybi.cn/account/confirm_reset_password?activation_key=%s&email=%s" % \
                (user.account.activation_key, user.account.email)
        html = render_template('admin/user/_reset_password.html',
            project=current_app.config['PROJECT'], username=user.name, url=url)
        message = Message(subject=_('Reset your password in ')+ 'Maybi',
            html=html, recipients=[user.account.email])
        message.sender = 'notify@maybi.cn'
        mail.send(message)

        return jsonify(message="OK",desc=_('Please see your email for instructions on '
              'how to access your account'))
    else:
        return jsonify(message="Failed", desc=_('Sorry, no user found for that email address'))

@user.route('/update_avatar', methods=['POST'])
@login_required
def update_avatar():
    path = request.json.get('avatar_url')
    if path:
        url = "http://assets.maybi.cn/%s" % path
        Jobs.image.make_thumbnails('maybi-img', path, url)

        user = current_user._get_current_object()
        user.avatar_url = url
        user.save()
    return jsonify(message='OK', user=Json.get_user_info(user))

@user.route('/update_username', methods=['POST'])
@login_required
def update_username():
    username = request.json.get('username')
    if username:
        if len(username) >16:
            return jsonify(message="Failed", error=_('Username is too long'))
        user = current_user._get_current_object()
        user.name = username
        user.save()
        return jsonify(message='OK', user=Json.get_user_info(user))
    return jsonify(message='Failed', error=u"参数不对")

@user.route('/user_info/<user_id>', methods=['GET'])
def user_info(user_id):
    user = Models.User.objects(id=user_id).first_or_404()
    return jsonify(message='OK', user=Json.user_json(user))

@user.route('/follow/<follow_id>', methods=['GET'])
@login_required
def follow(follow_id):
    follow_user = Models.User.objects(id=follow_id).first_or_404()
    if follow_user.id == current_user.id:
        return jsonify(message='Failed', error="Can not follow yourself")
    current_user.follow(follow_user)

    return jsonify(message='OK')

@user.route('/unfollow/<follow_id>', methods=['GET'])
@login_required
def unfollow(follow_id):
    follow_user = Models.User.objects(id=follow_id).first_or_404()
    current_user.unfollow(follow_user)

    return jsonify(message='OK')

@user.route('/followers', methods=['GET'])
def user_followers():
    args = request.args
    user_id = args.get('user_id')
    page = int(args.get('page', 0))
    per_page = int(args.get('per_page', 20))

    user = Models.User.objects(id=user_id).first_or_404()
    followers = user.followers
    users = paginate(followers, page, per_page)

    return jsonify(message='OK', users=[Json.user_json(u) for u in users])


@user.route('/followings', methods=['GET'])
def user_followings():
    args = request.args
    user_id = args.get('user_id')
    page = int(args.get('page', 0))
    per_page = int(args.get('per_page', 20))

    user = Models.User.objects(id=user_id).first_or_404()
    followings = user.followings
    users = paginate(followings, page, per_page)

    return jsonify(message='OK', users=[Json.user_json(u) for u in users])
