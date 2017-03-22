# -*- coding: utf-8 -*-

import math
from application.extensions import db
from datetime import datetime, date, timedelta
from configs.enum import CURRENCY

__all__ = ['PriceHistory', 'ForexRate']


class Price(db.EmbeddedDocument):
    price = db.FloatField(required=True, min_value=0)
    record_date = db.DateTimeField(default=datetime.utcnow(), required=True)


class PriceHistory(db.Document):
    meta = {
        'db_alias': 'inventory_db',
    }

    item_id = db.IntField(required=True)
    history = db.EmbeddedDocumentListField('Price', required=True)

    @classmethod
    def upsert_price_history(cls, item_id, cur):
        if not cls.objects(item_id=item_id):
            price = Price(price=cur)
            cls(item_id=item_id, history=[price]).save()
        else:
            if cls.objects(item_id=item_id).first().history[-1].price != cur:
                price = Price(price=cur)
                cls.objects(item_id=item_id).update_one(push__history=price)


DEFAULT_RX_RATE = {
    'USD': 6.25,
    'TWD': 0.210,
}
RATE_INCR = {
    'USD': 0.03,
    'TWD': 0.005,
}


def _ceil(v, n):
    return math.ceil(v * 10**n) / (1.0 * 10**n)


class ForexRate(db.Document):
    currency = db.StringField(default=CURRENCY.USD, choices=CURRENCY)
    rate = db.FloatField()
    modified = db.DateTimeField()

    @classmethod
    def get(cls, currency=CURRENCY.USD):
        currency = currency.upper()
        if currency == 'US':
            currency = 'USD'
        if currency == 'CNY':
            return 1

        # rounding datetime, so we can use cache of mongoengine
        start = (datetime.utcnow() - timedelta(days=3)).replace(
            minute=0, second=0, microsecond=0)
        rate_objs = cls.objects(currency=currency, modified__gt=start)
        rates = [r.rate for r in rate_objs]
        try:
            rate = sum(rates) / float(len(rates))
        except ZeroDivisionError:
            rate = 0

        if not rate:
            rate = cls.get_latest_rate(currency)
        return _ceil(rate + RATE_INCR.get(currency, 0), 3)

    @classmethod
    def get_latest_rate(cls, currency=CURRENCY.USD):
        forex = cls.objects(currency=currency).order_by('-modified').first()
        rate = forex.rate if forex else DEFAULT_RX_RATE[currency]
        return rate

    @classmethod
    def put(cls, rate, d=None, currency=CURRENCY.USD):
        if d is None:
            d = datetime.utcnow()
        cls.objects(currency=currency, modified=d).update_one(
            set__rate=rate, upsert=True)
