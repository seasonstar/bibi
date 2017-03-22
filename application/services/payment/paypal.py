# -*- coding: utf-8 -*-

import datetime
import paypalrestsdk
from flask import url_for, abort, current_app
from .config import PAYPAL_SANDBOX, PAYPAL_LIVE
from configs.enum import PAYMENT_TRADERS

def init_paypal():
    paypalrestsdk.configure(**PAYPAL_LIVE)
    return paypalrestsdk

def create_webprofile():
    paypalapi = init_paypal()
    web_profile = paypalapi.WebProfile({
        "name": "maybi",
        "presentation": {
            "brand_name": "Maybi Shop",
            "logo_image": "http://assets.maybi.cn/logo/maybi.jpg",
            "locale_code": "zh_CN"
        },
        "input_fields": {
            "allow_note": False,
            "no_shipping": 1,
            "address_override": 1
        },
    })
    if web_profile.create():
        print("Web Profile[%s] created successfully" % (web_profile.id))
        return web_profile.id
    else:
        print(web_profile.error)
        return None

def paypal_checkout(order, ptype):
    subject = u'Maybi Order %s' % str(order.short_id)

    paypalapi = init_paypal()
    payment = paypalapi.Payment({
        "intent": "sale",
        "experience_profile_id": "XP-ZC4W-JUZD-6JPP-J36R",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": url_for('payment.paypal_success', _external=True),
            "cancel_url": url_for('payment.paypal_cancel', _external=True)
        },

        "transactions": [{
            "amount": {
                "total": "%.2f" % order.final,
                "currency": "USD"
            },
            "description": subject,
        }]
    })
    if payment.create():
        print("Payment[%s] created successfully" % (payment.id))
        obj = create_payment(order, ptype, payment)
    else:
        print("Error while creating payment:")
        print(payment.error)
        current_app.logger.error(payment.error)
    return payment, obj


def create_payment(order, ptype, payment):
    # Redirect the user to given approval url
    for link in payment.links:
        if link.method == "REDIRECT":
            redirect_url = str(link.href)
            print("Redirect for approval: %s" % (redirect_url))

    obj = order.create_payment(ptype, PAYMENT_TRADERS.PAYPAL)
    obj.redirect_url = redirect_url
    obj.ref_number = payment.id
    obj.save()
    return obj

def paypal_update_payment(pending_payment, payer_id):
    try:
        paypalapi = init_paypal()
        payment = paypalapi.Payment.find(pending_payment.ref_number)
    except paypalrestsdk.exceptions.ResourceNotFound:
        abort(404)

    if payment.execute({"payer_id": payer_id}):
        if payment.state == 'approved' and pending_payment.ref_number == payment.id:
            pay_dt = datetime.datetime.utcnow(),
            data = dict(
                paid_amount = float(payment.transactions[0].amount.total),
                currency = payment.transactions[0].amount.currency,
                buyer_id =  payment.payer.payer_info.email,
                trade_status = payment.state.upper(),
                modified = pay_dt,
            )
            pending_payment.mark_paid(data)
            return True
        else:
            return False

    else:
        current_app.logger.error(payment.error)
        return False

def paypal_sdk_update_payment(pending_payment):
    try:
        paypalapi = init_paypal()
        payment = paypalapi.Payment.find(pending_payment.ref_number)
    except paypalrestsdk.exceptions.ResourceNotFound:
        abort(404)

    if payment.state == 'approved' and pending_payment.ref_number == payment.id:
        pay_dt = datetime.datetime.utcnow(),
        data = dict(
            paid_amount = float(payment.transactions[0].amount.total),
            currency = payment.transactions[0].amount.currency,
            buyer_id =  payment.payer.payer_info.email,
            trade_status = payment.state.upper(),
            modified = pay_dt,
        )
        pending_payment.mark_paid(data)
        return True
    else:
        current_app.logger.error(payment.error)
        return False
