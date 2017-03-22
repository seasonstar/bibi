# -*- coding: utf-8 -*-
from application.services.logistic import logistic_provider_dispatcher
import application.models as Models
import application.services.jobs as Jobs
from application.services.noti import noti_order

from configs.enum import ORDER_STATUS, COIN_TYPE, ORDER_TYPE
import configs.signals as Signals


def payment_received(order):
    if order.order_type != ORDER_TYPE.TRANSFER:
        order = logistic_provider_dispatcher(order)
    else:
        for logistic in order.logistics:
            logistic.update_logistic({'status': 'PAYMENT_RECEIVED'})
    Jobs.order_stat.update_user_stats(user_id=order.customer_id)
    noti_order(order, 'PAYMENT_RECEIVED')
    Signals.payment_received.send('received', order=order)

@Signals.payment_received.connect
def post_payment_ops(sender, order):
    coin_wallet = order.customer.coin_wallet
    wallet = order.customer.wallet
    if order.coin:
        coin_wallet.pay(order, order.coin, coin_type=COIN_TYPE.COIN)
        coin_wallet.reload()
    if order.cash:
        coin_wallet.pay(order, order.cash, coin_type=COIN_TYPE.CASH)
        coin_wallet.reload()
    for code in order.coupon_codes:
        wallet.use_consumable_coupon(code)
        wallet.reload()

    for order in Models.Order.objects(
            customer_id=str(order.customer.id),
            status=ORDER_STATUS.PAYMENT_PENDING, id__ne=order.id):
        order.update_amount()

    for entry in order.entries:
        item = entry.item
        Signals.item_bought.send('system', item_id=entry.item_snapshot.item_id)
