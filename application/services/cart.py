# -*- coding: utf-8 -*-
from collections import Counter
from datetime import datetime, timedelta
from application.models import Cart, CartEntry, EntrySpec
from application.services.json_tmpl.cart import cart_json
from application.services.inventory import get_specs_info


def _get_cart(user_id, session_key):
    if user_id:
        cart = Cart.objects(user_id=user_id).modify(
            upsert=True, new=True, set__user_id=user_id)
    elif session_key:
        cart = Cart.objects(session_key=session_key).modify(
            upsert=True, new=True, set__session_key=session_key)
    return cart


def _cart_specs_info(cart):
    return get_specs_info([e.sku for e in cart.entries])


def _new_entry(sku, quantity, cart):
    now = datetime.utcnow()
    return CartEntry(sku=sku, quantity=quantity,
                     created_at=now)


def _remove_cart_from_spec(sku, cart_id):
    cart = Cart.objects(id=cart_id).first()
    if sku in (e.sku for e in cart.entries):
        return
    EntrySpec.objects(sku=sku).update_one(pull__carts=cart)

    sp = EntrySpec.objects(sku=sku).first()
    if sp and not sp.carts:
        sp.update(set__last_empty_date=datetime.utcnow())


def remove_cart_from_specs(skus, cart_id):
    for sku in skus:
        _remove_cart_from_spec(sku, cart_id)


def get_cart_entries_num(user_id=None, session_key=None):
    cart = _get_cart(user_id, session_key)
    return len(cart.entries)


def update_cart_entry(sku, quantity=1, incr_quantity=True,
                      user_id=None, session_key=None):
    cart = _get_cart(user_id, session_key)

    for e in cart.entries:
        if e.sku == sku:
            if incr_quantity:
                e.quantity += quantity
            else:
                e.quantity = quantity
            cart.save()
            break
    else:
        if sku:  # ignore where sku is None.
            e = _new_entry(sku=sku, quantity=quantity, cart=cart)
            cart.entries.append(e)
            cart.save()

    return cart_json(cart)


def remove_from_cart(skus, user_id=None, session_key=None):
    cart = _get_cart(user_id, session_key)
    cart.entries = [e for e in cart.entries if e.sku not in skus]
    cart.save()
    remove_cart_from_specs(skus, str(cart.id))
    return cart_json(cart)


def empty_cart(user_id=None, session_key=None):
    cart = _get_cart(user_id, session_key)
    del_skus = [e.sku for e in cart.entries]
    cart.entries = []
    cart.save()
    remove_cart_from_specs(del_skus, str(cart.id))
    return cart_json(cart)


def update_cart(entries_info, user_id=None, session_key=None):
    cart = _get_cart(user_id, session_key)

    quantities = {e.get('sku'): e.get('quantity') for e in entries_info}
    orig_skus = set(e.sku for e in cart.entries)
    current_skus = set(e.get('sku') for e in entries_info)

    new_skus = current_skus - orig_skus
    del_skus = []

    entries = []
    for e in cart.entries:
        if e.sku not in current_skus:
            del_skus.append(e.sku)
            continue
        if not e.sku:  # ignore where sku is None.
            continue
        e.quantity = quantities.get(e.sku, 1)
        entries.append(e)

    for sku in new_skus:
        if not sku:  # ignore where sku is None.
            continue
        entries.append(_new_entry(sku=sku, quantity=quantities.get(sku, 1),
                                  cart=cart))

    cart.entries = entries
    cart.save()

    remove_cart_from_specs(del_skus, str(cart.id))

    return cart_json(cart)


def get_cart(user_id=None, session_key=None):
    cart = _get_cart(user_id, session_key)
    return cart_json(cart)


def merge_carts(user_id_from=None, session_key_from=None,
                user_id_to=None, session_key_to=None):
    from_cart = _get_cart(user_id_from, session_key_from)
    to_cart = _get_cart(user_id_to, session_key_to)
    info = Counter({e.sku: e.quantity for e in from_cart.entries})
    info.update({e.sku: e.quantity for e in to_cart.entries})
    res = update_cart([{'sku': k, 'quantity': v} for k, v in info.items()],
                      user_id_to, session_key_to)
    empty_cart(user_id_from, session_key_from)
    return res


def entry_info_from_ids(entries):
    entries_info = []
    for entry in entries:
        e = {}
        e['item_id'] = entry['item_id']
        e['sku'] = entry['sku']
        e['quantity'] = entry['quantity']
        entries_info.append(e)

    return entries_info
