# -*- coding: utf-8 -*-
from .inventory import item_json_in_list, spec_json


def entry_json(entry):
    item = entry.item_snapshot
    spec = entry.item_spec_snapshot
    item_dict = item_json_in_list(item)
    spec_dict = spec_json(spec)
    return dict(
        id=str(entry.id),
        item=item_dict,
        spec=spec_dict,
        unit_price=entry.unit_price,
        amount=entry.amount,
        amount_usd=entry.amount_usd,
        discount=entry.discount,
        quantity=entry.quantity,
        weight=item.weight,
    )


def transfer_entry_json(entry):
    item = entry.item_snapshot
    spec = entry.item_spec_snapshot
    item_dict = item_json_in_list(item)
    spec_dict = spec_json(spec)
    return dict(
        id=str(entry.id),
        item=item_dict,
        spec=spec_dict,
        title=item.title,
        amount=item.china_price,
        amount_usd=entry.amount_usd,
        quantity=entry.quantity,
        main_category=item.main_category,
        weight=item.weight,
        remark=entry.remark,
        shipping_info=entry.shipping_info,
    )


def cart_entry_json(entry):
    item = entry.item_snapshot
    spec = entry.item_spec_snapshot
    item_dict = item_json_in_list(item)
    spec_dict = spec_json(spec)
    return dict(
        id=str(entry.id),
        item=item_dict,
        spec=spec_dict,
        unit_price=entry.unit_price,
        amount=entry.amount,
        amount_usd=entry.amount_usd,
        discount=entry.discount,
        quantity=entry.quantity,
        weight=item.weight,
    )
