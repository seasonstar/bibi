# -*- coding: utf-8 -*-

from itertools import chain
import application.models as Models
from application.cel import celery


@celery.task
def update_user_stats(user_id):
    stat, created = Models.OrderStat.objects.get_or_create(user_id=user_id)

    all_orders = Models.Order.objects(customer_id=user_id)
    stat.num_orders = all_orders.count()
    stat.total = all_orders.sum('final')

    received_orders = Models.Order.received(customer_id=user_id)
    stat.received = received_orders.sum('final')

    stat.num_unpaid = Models.Order.payment_pending(customer_id=user_id).count()

    processing = Models.Order.processing(customer_id=user_id)
    stat.num_waiting = processing.count()
    stat.save()
