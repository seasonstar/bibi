# -*- coding: utf-8 -*-
import datetime
import application.models as Models
from configs.enum import COUPON_SCOPE, COUPON_APPLY
from application.extensions import db
from .coupon import CouponList, CouponConflict


class DocProxy(object):
    def __init__(self, obj):
        self._obj = obj

    def __getattr__(self, attr):
        return getattr(self._obj, attr)

    def apply(self):
        for attr, value in vars(self).items():
            if attr.startswith('_'):
                continue
            setattr(self._obj, attr, value)


class PriceEval(DocProxy):
    def __init__(self, obj):
        super(PriceEval, self).__init__(obj)
        self.entries = [EntryProxy(entry) for entry in obj.entries]
        self.order_coupons = CouponList()
        self.entry_coupons = CouponList()
        self.coupon_errors = []
        if getattr(obj, 'is_paid', False):
            for coupon in Models.Coupon.objects(code__in=self.coupon_codes):
                self.add_coupon(coupon)
        else:
            for coupon in Models.Coupon.objects(
                    (db.Q(code__in=self.coupon_codes) |
                     db.Q(apply=COUPON_APPLY.AUTO)) &
                    db.Q(effective_date__lt=datetime.datetime.utcnow(),
                         expire_date__gt=datetime.datetime.utcnow())):
                if self.can_add_coupon(coupon):
                    self.add_coupon(coupon)
                    break
        self.discount = []

    def can_add_coupon(self, coupon):
        return (coupon.apply in (COUPON_APPLY.AUTO, COUPON_APPLY.BY_CODE) or
                self._obj.customer.wallet.has_coupon(coupon))

    def add_coupon(self, coupon):
        if coupon.scope == COUPON_SCOPE.ORDER:
            container = self.order_coupons
        else:
            container = self.entry_coupons

        try:
            container.add(coupon)
        except CouponConflict:
            if coupon.code in self.coupon_codes:
                self.coupon_errors.append(coupon.code)

    def apply(self):
        for entry in self.entries:
            entry.apply()
        del self.entries
        del self.order_coupons
        del self.entry_coupons
        super(PriceEval, self).apply()

    def apply_base_price(self):
        for attr in ('amount_usd', 'amount',
                     'cn_shipping', 'final',
                     'forex', 'logistic_provider'):
            setattr(self._obj, attr, getattr(self, attr, None))

    def apply_discount(self):
        for attr in ('discount', 'coin', 'cash', 'final', 'is_test'):
            setattr(self._obj, attr, getattr(self, attr, None))


class EntryProxy(DocProxy):
    pass


def get_price_eval(order):
    if isinstance(order, PriceEval):
        return order
    return PriceEval(order)
