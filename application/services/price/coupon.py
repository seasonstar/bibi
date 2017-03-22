# -*- coding: utf-8 -*-
from configs.enum import COUPON_TYPES as CT


class CouponConflict(Exception):
    pass


class CouponList(object):
    ''' implement some ugly validations for coupon usage'''

    CONFLICT_PAIRS = (
        (CT.FREE_SHIPPING, CT.SHIPPING_DEDUCTION),
    )

    def __init__(self):
        self.coupons = []
        self.types = []
        self.codes = set()
        self.conflicts = set()

    def add(self, coupon):
        if coupon.code in self.codes:
            raise CouponConflict('already in coupon list')

        coupon_type = coupon.coupon_type
        if coupon_type in self.conflicts:
            raise CouponConflict()

        if coupon_type == CT.PERCENT_DEDUCTION and \
                CT.AMOUNT_DEDUCTION in self.types:
            i = self.types.index(CT.AMOUNT_DEDUCTION)
            self.coupons.insert(i, coupon)
            self.types.insert(i, coupon_type)
        else:
            self.coupons.append(coupon)
            self.types.append(coupon_type)

        self.codes.add(coupon.code)
        for pair in self.CONFLICT_PAIRS:
            if coupon_type in pair:
                self.conflicts |= set(pair)

    def __iter__(self):
        return self.coupons.__iter__()

    def __len__(self):
        return len(self.coupons)

    def __getitem__(self, i):
        return self.coupons[i]

    def __delitem__(self, i):
        del self.coupons[i]

    def __add__(self, other):
        return self.coupons + other.coupons
