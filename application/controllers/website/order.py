# -*- coding: utf-8 -*-
import json
import time
from flask import request, jsonify, g, Blueprint
from flask_login import current_user, login_required
from flask_babel import gettext as _

from application.services.price import cal_order_price, FakeCart
import application.services.jobs as Jobs
import application.services.json_tmpl as Json
from application.services.bingtrans import MSTranslate
from application.services.logistic import logistic_provider_dispatcher
from application.services.inventory import import_entries

import application.models as Models
from configs.enum import ORDER_SOURCES, ORDER_TYPE, DictEnum, LOG_STATS

from application.services.cart import entry_info_from_ids, remove_from_cart

order = Blueprint('orders', __name__, url_prefix='/api/orders')

def unpaid_orders(user_id):
    orders = Models.Order.payment_pending(customer_id=user_id)
    return [Json.simple_order_json(o) for o in orders]


def logistic_orders(user_id):
    orders = Models.Order.processing(customer_id=user_id)
    return [Json.simple_order_json(o) for o in orders]


@order.route('/<order_type>', methods=['GET'])
@login_required
def get_orders(order_type):
    if order_type == 'COMMODITIES':
        orders = Models.Order.commodities(customer_id=current_user.id)
    elif order_type == 'TRANSFER':
        orders = Models.Order.transfer(customer_id=current_user.id)
    else:
        return jsonify(message='Failed')
    return jsonify(message='OK',
        orders=[Json.simple_order_json(o) for o in orders])


@order.route('/cal_entries_price', methods=['POST'])
@login_required
def cal_entries_price():
    '''calculate their prices.'''
    data = request.json
    entries = data.get('entries')
    if not entries:
        return jsonify(message='Failed', error=_(u'Please select the item.'))

    address_id = data.get('address_id')
    if address_id:
        address = Models.Address.objects(id=address_id).first_or_404()
    else:
        return jsonify(message='Failed', error=_(u'Please select the address'))

    entries_info = entry_info_from_ids(entries)

    cart = FakeCart(entries_info=entries_info,
                    user=current_user._get_current_object(),
                    address=address)

    cart.logistic_provider = data.get('logistic_provider')
    cart.cash = user.coin_wallet.cash if data.get('cash') else 0
    cart.coupon_codes = data.get('coupon_codes', [])

    o = cal_order_price(cart)
    res = Json.order_price_json(o)
    return jsonify(message='OK', order=res)


@order.route('/get/<order_id>', methods=['GET'])
@login_required
def get_order(order_id):
    order = Models.Order.get_order_or_404(order_id)
    return jsonify(message='OK', order=Json.order_json(order))


@order.route('/<order_id>/delete', methods=['GET'])
@login_required
def delete_order(order_id):
    order = Models.Order.get_order_or_404(order_id)
    if order.customer_id != current_user.id or order.is_paid:
        return jsonify(message='Failed', error=_('Order not found'))

    order.cancel_order('user delete', 'ORDER_DELETED')
    return jsonify(message='OK')


@order.route('/secret/verify_and_move/<int:code>', methods = ['GET'])
@login_required
def move_order_to_self(code):
    order_code = Models.TransferOrderCode.objects(code=code).first()
    if not order_code:
        return jsonify(message='Failed')

    order = Models.Order.get_order_or_404(order_code.order_id)
    order.customer_id = current_user.id
    order.save()

    #Jobs.stat.update_user_stats(str(order.customer_id))
    order_code.delete()

    return jsonify(message='OK', order=Json.order_json(order))



@order.route('/logistics/<logistic_id>', methods=['GET'])
@login_required
def get_logistic(logistic_id):
    mo = Models.Logistic.objects(id=logistic_id).first_or_404()
    express = mo.express_tracking

    mo_logistic = {'id': str(mo.id)}
    mo_logistic['entries'] = [Json.entry_json(e) for e in mo.entries]
    mo_logistic['status'] = mo.detail.status
    mo_logistic['data'] = mo.to_json()
    mo_logistic['history'] = mo.shipping_history
    mo_logistic['tracking'] = express.history if express else ''
    mo_logistic['address'] = mo.order.address.to_json()
    mo_logistic['payment_status'] = mo.order.goods_payment.status
    return jsonify(message='OK', logistic=mo_logistic)


@order.route('/create_order', methods=['POST'])
@login_required
def create_order():
    data = request.json
    entries = data.get('entries')
    entries_info = entry_info_from_ids(entries)

    user = current_user._get_current_object()

    address_id = data.get('address_id')
    if address_id:
        address = Models.Address.objects(
            id=address_id).first_or_404()
    elif user.addresses:
        address = user.addresses[0]
    else:
        return jsonify(message='Failed', error=_('no address'))

    logistic_provider = data.get('logistic_provider')
    if not logistic_provider:
        return jsonify(message='Failed', error=_('no logistic provider'))

    coin = 0
    cash = 0
    coupon_codes = data.get('coupon_codes', [])

    order = Models.Order.create_from_skus(
        user.id, entries_info, logistic_provider,
        coupon_codes=coupon_codes, coin=coin, cash=cash,
        address=address, source=ORDER_SOURCES.WECHAT)

    if not isinstance(order, Models.Order):
        return jsonify(message='Failed',
                       error=u'编号为“{}”的商品已售光，请重新提交'.format(
                           order['item_id']))

    if order.final == 0:
        order.set_paid()

    remove_from_cart([entry.item_spec_snapshot.sku for entry in order.entries],
                     user_id=str(current_user.id))

    return jsonify(message='OK', order_id=str(order.id),
                   order=order.to_grouped_json())

@order.route('/create_transfer_order', methods=['POST'])
@login_required
def create_transfer_order():
    data = request.json
    entries = data.get('entries')

    user = current_user._get_current_object()

    address_id = data.get('address_id')
    if address_id:
        address = Models.Address.objects(
            id=address_id).first_or_404()
    elif user.addresses:
        address = user.addresses[0]
    else:
        return jsonify(message='Failed', error=_('no address'))

    coin = 0
    cash = user.coin_wallet.cash if data.get('cash') else 0
    coupon_codes = data.get('coupon_codes', [])

    entries = import_entries(entries)
    order = Models.Order.create_transfer(customer_id=str(user.id),
                         final=0,
                         entries=entries,
                         address=address,
                         source=ORDER_SOURCES.WECHAT,
                         status=LOG_STATS.PENDING_REVIEW,
                         order_type=ORDER_TYPE.TRANSFER,
                         logistic_provider=data.get('logistic_provider'),
                         coupon_codes=coupon_codes,
                         coin=coin,
                         cash=cash)

    logistic_provider_dispatcher(order)

    return jsonify(message='OK', order_id=str(order.id),
                   order=order.to_grouped_json())

@order.route('/update_transfer_order', methods=['POST'])
@login_required
def update_transfer_order():
    '''calculate order prices.'''
    data = request.json
    order_id = data.get('order_id')
    order = Models.Order.objects(id=order_id).first_or_404()
    if order.status != 'WAREHOUSE_IN':
        return jsonify(message='Failed', error=_('only when order status WAREHOUSE_IN can be updated'))

    address_id = data.get('address_id')
    if address_id:
        address = Models.Address.objects(
            id=address_id).first_or_404()
    elif user.addresses:
        address = user.addresses[0]
    else:
        return jsonify(message='Failed', error=_('no address'))

    order.logistic_provider = data.get('logistic_provider')
    order.coupon_codes = data.get('coupon_codes', [])
    order.address = address

    order.update_amount()
    order.reload()
    res = Json.transfer_order_price_json(order)
    return jsonify(message='OK', order=res)

@order.route('/cal_order_price', methods=['POST'])
@login_required
def cal_price_by_order():
    '''calculate order prices.'''
    data = request.json
    order_id = data.get('order_id')
    address_id = data.get('address_id')
    if address_id:
        address = Models.Address.objects(
            id=address_id).first_or_404()
    elif user.addresses:
        address = user.addresses[0]
    else:
        return jsonify(message='Failed', error=_('no address'))

    order = Models.Order.objects(id=order_id).first_or_404()
    order.logistic_provider = data.get('logistic_provider')
    order.coupon_codes = data.get('coupon_codes', [])

    order.address = address

    o = cal_order_price(order)
    res = Json.transfer_order_price_json(o)
    return jsonify(message='OK', order=res)


@order.route('/fill_shipping_info', methods=['POST'])
@login_required
def fill_shipping_info():
    data = request.json
    entry_id = data.get('entry_id')
    shipping_info = data.get('shipping_info')
    entry = Models.OrderEntry.objects(id=entry_id).first()
    entry.shipping_info = {
            'number': shipping_info.get('number'),
            'is_written': True
        }
    entry.save()
    return jsonify(message='OK')
