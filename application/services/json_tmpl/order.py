# -*- coding: utf-8 -*-
import re
import itertools
from math import ceil
import application.models as Models
from application.utils import format_date

from .entry import entry_json, transfer_entry_json

from configs.order_status import *
from configs.enum import LOG_STATS, ORDER_TYPE

def simple_order_json(order):
    if not order.is_paid:
        order.update_amount()
        order.reload()

    entries_json = []
    for e in order.entries:
        if order.order_type == ORDER_TYPE.TRANSFER:
            entries_json.append(transfer_entry_json(e))
        else:
            entries_json.append(entry_json(e))

    refund_entries_json = []
    for e in order.refund_entries:
        refund_entries_json.append(e.to_json())

    result = dict(
        id=str(order.id),
        short_id=str(order.sid),
        current_status=ORDER_STATUS_DESC.get(order.status, ''),
        status=order.status,
        customer_id=str(order.customer_id),
        amount=order.amount,
        amount_usd=order.amount_usd,
        cn_shipping=order.cn_shipping,
        coin=order.coin,
        hongbao=order.hongbao,
        discount=order.discount,
        final=order.final,
        payment_status='PAID' if order.is_paid else 'UNPAID',
        payment_ref_number=[p.ref_number for p in
                            Models.Payment.objects(order=order)],
        created_at=format_date(order.created_at),
        entries=entries_json,
        refund_entries=refund_entries_json,
        refund_amount=order.refund_amount,
    )

    return result


def order_json(order):
    if not order.is_paid:
        order.update_amount()
        order.reload()

    entries_json = []
    for e in order.entries:
        if order.order_type == ORDER_TYPE.TRANSFER:
            entries_json.append(transfer_entry_json(e))
        else:
            entries_json.append(entry_json(e))

    refund_entries_json = []
    for e in order.refund_entries:
        refund_entries_json.append(e.to_json())

    provider_json = Models.LogisticProvider.objects.get(
            name=order.logistic_provider,
            country=order.address.country).to_json()

    result = dict(
        id=str(order.id),
        short_id=str(order.sid),
        status=order.status,
        customer_id=str(order.customer_id),
        amount=order.amount,
        amount_usd=order.amount_usd,
        cn_shipping=order.cn_shipping,
        coin=order.coin,
        hongbao=order.hongbao,
        discount=order.discount,
        final=order.final,
        estimated_tax=order.estimated_tax,
        payment_status='PAID' if order.is_paid else 'UNPAID',
        payment_ref_number=[p.ref_number for p in
                            Models.Payment.objects(order=order)],
        created_at=format_date(order.created_at),
        entries=entries_json,
        refund_entries=refund_entries_json,
        refund_amount=order.refund_amount,
        real_tax=order.real_tax,
        provider=provider_json,
        address='')

    if order.address:
        result.update(dict(address=order.address.to_json()))

    if order.logistics:
        result.update(
            dict(logistics=[logistic_json(l, order.order_type)
                            for l in order.logistics]))

    return result


def logistic_json(logistic, order_type):

    if order_type == ORDER_TYPE.TRANSFER:
        entries = [transfer_entry_json(entry) for entry in logistic.entries]
    else:
        entries = [entry_json(entry) for entry in logistic.entries]
    all_status = [
        {'status': st, 'desc': ORDER_STATUS_DESC.get(st, '')}
        for st in ROUTES.get(logistic.detail.route, 'DEFAULT')
    ]
    current_status = logistic.detail.status

    # Combined history
    history = []
    for st in LOG_STATS:

        dt_field = logistic.detail.attr_by_log_stat[st]
        val = getattr(logistic.detail, dt_field)
        if not val:
            continue
        history.append(dict(
            desc=SHIPPING_HISTORY[st],
            time=(format_date(val) if val else ''),
        ))
        if st == 'TRANSFER_APPROVED':
            history.append(dict(
                desc=u'美比仓库地址：广东省深圳市 南山区 粤海路四达大厦B座19B \t邮编：518000',
                time=u'收货人：唐耀星 \t手机号码：13822327121',
            ))
        if st == 'WAREHOUSE_IN' and logistic.detail.real_weight > 0:
            history.append(dict(
                desc=u'称得包裹总重量：%skg' % str(logistic.detail.real_weight/1000),
                time='',
            ))

        # tracking information
        tracking = None
        if st == LOG_STATS.SHIPPING and logistic.detail.cn_logistic_name:
            history.append(dict(
                desc=u'国际快递公司: %s' % logistic.detail.cn_logistic_name.upper(),
                time=u'国际快递单号: %s' % logistic.detail.cn_tracking_no,
            ))
            tracking = Models.ExpressTracking.find(
                company=logistic.detail.cn_logistic_name,
                number=logistic.detail.cn_tracking_no)
        for d in (reversed(tracking.data) if tracking else []):
            desc = re.sub(r'\s{2,}', ' ', d.get('context', ''))
            history.append(dict(
                desc=desc,
                time=d.get('time', ''),
            ))

        if st == current_status:
            break

    if current_status in ['PENDING_RETURN', 'RETURNING', 'RETURNED']:
        current_status = 'PAYMENT_RECEIVED'

    return {
        'id': str(logistic.id),
        'entries': entries,
        'all_status': all_status,
        'current_status': current_status,
        'history': history,
        'partner_tracking_no': logistic.detail.partner_tracking_no,
    }

def order_price_json(order):

    return dict(
        coin=getattr(order, 'coin', None) or 0,
        hongbao=getattr(order, 'hongbao', None) or 0,
        coupon_codes=order.coupon_codes,
        amount_usd = round(order.amount_usd, ndigits=2),
        cn_shipping=order.cn_shipping,
        discount=order.discount + list(itertools.chain.from_iterable(
            e.discount for e in order.entries)),
        final=round(order.final, ndigits=2),
    )

def transfer_order_price_json(order):

    entries_json = []
    for e in order.entries:
        entries_json.append(transfer_entry_json(e))

    provider_json = Models.LogisticProvider.objects.get(
            name=order.logistic_provider,
            country=order.address.country).to_json()

    result = dict(
        id=str(order.id),
        short_id=str(order.sid),
        status=order.status,
        customer_id=str(order.customer_id),
        amount=order.amount,
        amount_usd=order.amount_usd,
        cn_shipping=order.cn_shipping,
        coin=order.coin,
        hongbao=order.hongbao,
        discount=order.discount,
        final=order.final,
        estimated_tax=order.estimated_tax,
        payment_status='PAID' if order.is_paid else 'UNPAID',
        created_at=format_date(order.created_at),
        entries=entries_json,
        refund_amount=order.refund_amount,
        real_tax=order.real_tax,
        provider=provider_json,
        address='')

    if order.address:
        result.update(dict(address=order.address.to_json()))

    if order.logistics:
        result.update(
            dict(logistics=[logistic_json(l, order.order_type)
                            for l in order.logistics]))

    return result
