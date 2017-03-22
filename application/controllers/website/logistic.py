# -*- coding: utf-8 -*-
import json
from flask import jsonify, request, Blueprint
from flask_login import login_required
from flask_babel import gettext as _
from application.services.cache import cached

import application.services.json_tmpl as Json

import application.models as Models

logistic = Blueprint('logistics', __name__, url_prefix='/api/logistic')

@logistic.route('/channel_prices', methods=['POST'])
@login_required
def get_channel_providers():
    entry_ids = request.json.get('entries')
    country = request.json.get('country')
    if not entry_ids or not country:
        return jsonify(message='Failed', error=_(u'Please select the item and address.'))
    items = map(lambda i: (Models.Item.objects(item_id=int(i.get('item_id'))).first(),
            i.get('quantity')), entry_ids)
    res = Json.channel_prices(items, country)
    return jsonify(message='OK', logistics=res)


@logistic.route('/transfer_provider_prices', methods=['POST'])
@login_required
def get_transfer_providers():
    order_id = request.json.get('order_id')
    country = request.json.get('country')
    if not order_id or not country:
        return jsonify(message='Failed', error=_(u'no order_id and country.'))
    order = Models.Order.objects(id=order_id).first()
    items = [(entry.item_snapshot, entry.quantity) for entry in order.entries]
    total_weight = sum(logistic.detail.real_weight for logistic in order.logistics)
    res = Json.logistic_provider_prices(items, country, total_weight)
    return jsonify(message='OK', logistics=res)

@logistic.route('/cal_provider_prices', methods=['GET'])
@cached(21600)
def cal_provider_prices():
    weight = float(request.args.get('weight'))
    country = request.args.get('country')
    if not weight or not country:
        return jsonify(message='Failed', error=_(u'no weight or country.'))
    res = Json.get_display_provider_info(country, weight)
    return jsonify(message='OK', logistics=res)
