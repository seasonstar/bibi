# -*- coding: utf-8 -*-
import json

from flask import Blueprint, session
from flask import request, jsonify
from flask_login import current_user, user_logged_in
from application.utils import get_session_key
import application.models as Models

from application.services.cart import remove_from_cart, \
    update_cart_entry, get_cart, empty_cart, merge_carts

cart = Blueprint('cart', __name__, url_prefix='/api/cart')


@user_logged_in.connect
def combine_cart(sender, user):
    merge_carts(session_key_from=session.sid, user_id_to=str(user.id))


@user_logged_in.connect
def combine_favor_items(sender, user):
    guest_record = Models.GuestRecord.by_key(key=get_session_key())
    current_user.favor_items = list(set(current_user.favor_items +
                                        guest_record.favor_items))
    current_user.num_favors = len(current_user.favor_items)
    current_user.save()


def get_user_id_for_cart():
    if current_user.is_authenticated:
        user_id = str(current_user.id)
        session_key = None
    else:
        user_id = None
        session_key = session.sid
    return user_id, session_key


@cart.route('', methods=['GET'])
def check_cart():
    user_id, session_key = get_user_id_for_cart()
    cart = get_cart(user_id, session_key)
    return jsonify(message='OK', cart=cart)


@cart.route('/add/<int:spec_id>', methods=['POST'])
def add_to_cart(spec_id):
    user_id, session_key = get_user_id_for_cart()
    quantity = int(request.json.get('quantity', 1))
    res = update_cart_entry(spec_id, quantity, incr_quantity=False,
                            user_id=user_id, session_key=session_key)

    return jsonify(message='OK', cart=res)


@cart.route('/entry/delete', methods=['POST'])
def remove_entries_from_cart():
    user_id, session_key = get_user_id_for_cart()
    skus = request.json.get('skus', '[]')
    res = remove_from_cart(skus, user_id, session_key)
    return jsonify(message='OK', cart=res)


@cart.route('/entry/<int:entry_id>/update', methods=['POST'])
def update_entry(entry_id):

    quantity = int(request.json.get('quantity', 1))
    user_id, session_key = get_user_id_for_cart()
    res = update_cart_entry(entry_id, quantity, incr_quantity=False,
                            user_id=user_id, session_key=session_key)

    return jsonify(message='OK', cart=res)


@cart.route('/empty', methods=['GET'])
def cart_empty():
    user_id, session_key = get_user_id_for_cart()
    res = empty_cart(user_id, session_key)
    return jsonify(message='OK', cart=res)
