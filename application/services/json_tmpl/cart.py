# -*- coding: utf-8 -*-
from datetime import datetime
from operator import itemgetter
from itertools import groupby

from application.services.inventory import get_specs_info
from application.models import EntrySpec


def cart_json(cart):
    info = get_specs_info([e.sku for e in cart.entries])
    specs = []
    for e, spec in zip(cart.entries, info):
        if not spec.get('found'):
            entry_spec = EntrySpec.objects(sku=e.sku).first()
            if not entry_spec:
                continue
            spec = entry_spec.to_mongo()
            spec['available'] = False
        spec['quantity'] = e.quantity
        specs.append(spec)

    entries = []
    for spec in specs:
        entries.append({
            'id': '{}-{}-{}'.format(spec['item_id'], spec['sku'], spec['quantity']),
            'item': {
                'item_id': spec['item_id'],
                'title': spec['title'],
                'primary_image': spec['primary_image'],
                'available': spec['item_available'],
            },
            'spec': {
                'item_id': spec['item_id'],
                'sku': spec['sku'],
                'images': spec['images'],
                'price': spec['price'],
                'available': spec['available'],
                'attributes': spec['attributes'],
            },
            'unit_price': spec['price'],
            'amount': spec['price'] * e.quantity,
            'quantity': spec['quantity'],
        })
    return entries
