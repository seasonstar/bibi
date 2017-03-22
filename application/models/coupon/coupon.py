# -*- coding: utf-8 -*-
from application.extensions import db
from application.utils import format_date
from datetime import datetime, timedelta
from configs.enum import COUPON_TYPES, COUPON_SCOPE, COUPON_APPLY, \
    COUPON_TYPES as CT
from application.utils import to_utc


__all__ = ['Coupon']


class Coupon(db.Document):
    meta = {
        'strict': False,
        'db_alias': 'order_db',
        'indexes': ['code', 'apply', 'expire_date', 'description']
    }

    scope = db.StringField(required=True, choices=COUPON_SCOPE,
                           default=COUPON_SCOPE.ORDER)
    coupon_type = db.StringField(default=COUPON_TYPES.NORMAL, required=True,
                                 choices=COUPON_TYPES)
    value = db.FloatField()
    description = db.StringField()
    effective_date = db.DateTimeField(default=datetime.utcnow)
    expire_date = db.DateTimeField(default=datetime(2019, 12, 31))
    code = db.StringField(unique=True)

    # by which means this coupon can be applied: by coupon code, by display_id
    apply = db.StringField(required=True, default=COUPON_APPLY.BY_DISPLAY_ID,
                           choices=COUPON_APPLY)

    required_amount = db.FloatField(default=0)
    required_final = db.FloatField(default=0)
    require_new_order = db.BooleanField(default=False)
    once_per_user = db.BooleanField(default=False)

    # note for internal usage
    note = db.StringField()
    coupon_category = db.StringField(choices=['PROMOTION', 'STAFF',
                                              'NEW_USER'], default='PROMOTION')

    @property
    def is_expired(self):
        if not self.expire_date:
            return False
        return (datetime.utcnow() >= self.expire_date)

    def to_json(self):
        return dict(
            coupon_type=self.coupon_type,
            value=self.value,
            code=self.code,
            effective_date=format_date(self.effective_date, '%Y-%m-%d'),
            expire_date=format_date(self.expire_date, '%Y-%m-%d'),
            is_expired=self.is_expired,
            description=self.description)

    def is_effective(self):
        return self.effective_date <= datetime.utcnow() < self.expire_date

    def can_apply(self, order):
        res = bool(
            (self.required_final <= order.final) and
            (self.required_amount <= order.amount) and
            not (self.require_new_order and order.customer.orders) and
            not (self.once_per_user and order.customer.used_coupon(self.code))
        )
        return res
