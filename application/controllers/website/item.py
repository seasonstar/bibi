# -*- coding: utf-8 -*-
import datetime
import json

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from flask_babel import gettext as _

from application.utils import get_session_key, paginate
from application.services.cache import cached
from application.services.log import log_item_visit
import application.models as Models
import application.services.jobs as Jobs
import application.services.json_tmpl as Json


item = Blueprint('item', __name__, url_prefix='/api/items')

def refactor_query(data):
    query = {}
    for k,v in data.items():
        if v in [None, u"None", "", "null"]:
            continue
        elif k == 'title':
            query.update({'title__icontains': v})
        elif 'page' in k:
            query.update({k: int(v)})
        else:
            query.update({k: v})
    return query

@item.route('', methods=['GET'])
@cached(3600)
def items():
    query = refactor_query(request.args)
    page = query.pop('page', 0)
    per_page = query.pop('per_page', 20)

    objects = Models.Item.available_items(**query)
    items = paginate(objects, page, per_page)
    data=[Json.item_json_in_list(i) for i in items]
    return jsonify(message='OK', items=data, total=objects.count())


@item.route('/<int:item_id>', methods=['GET'])
def item_detail(item_id):
    item = Models.Item.objects(item_id=item_id).first_or_404()

    item_dict = Json.item_json(item)

    if current_user.is_authenticated:
        user = current_user._get_current_object()
    else:
        user = Models.GuestRecord.by_key(get_session_key())

    item_dict.update({'is_favored': item_id in user.favor_items})
    log_item_visit(user_id=user.id, item_id=item_id)
    return jsonify(message='OK', item=item_dict)


@item.route('/favors', methods=['GET'])
def favor_items():
    if current_user.is_authenticated:
        user = current_user._get_current_object()
    else:
        # guest user
        user = Models.GuestRecord.by_key(get_session_key())

    items = Models.Item.objects(item_id__in=user.favor_items)

    return jsonify(message='OK',
                   items=[Json.item_json_in_list(i) for i in items])


@item.route('/favor/<int:item_id>', methods=['GET'])
def item_favor(item_id):
    item = Models.Item.objects(item_id=item_id).first_or_404()

    if current_user.is_authenticated:
        current_user.mark_favored(item)
    else:
        guest = Models.GuestRecord.by_key(get_session_key())
        guest.mark_favored(item)

    return jsonify(message='OK')


@item.route('/unfavor/<int:item_id>', methods=['GET'])
def item_unfavor(item_id):
    item = Models.Item.objects(item_id=item_id).first_or_404()

    if current_user.is_authenticated:
        current_user.unmark_favored(item)
    else:
        guest = Models.GuestRecord.by_key(get_session_key())
        guest.unmark_favored(item)

    return jsonify(message='OK')
