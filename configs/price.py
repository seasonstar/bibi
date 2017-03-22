# -*- coding: utf-8 -*-
import math
from application.utils import ceil
from .enum import DictEnum, COUPON_TYPES as CT


def _with_fx_rate(x, forex=None):
    from application.models import ForexRate
    if forex is None:
        forex = ForexRate.get()
    return ceil(x * forex)

PRICE_FN = DictEnum({
    'ORDER_COUPON': {
        CT.AMOUNT_DEDUCTION:
            lambda o, c: ('final', min(o.final, int(c.value))),
        CT.PERCENT_DEDUCTION:
            lambda o, c: ('amount_usd', int(o.amount_usd * float(c.value))),
        CT.FINAL_PERCENT_DEDUCTION:
            lambda o, c: ('final', int(o.final * float(c.value))),
        CT.SHIPPING_DEDUCTION:
            lambda o, c: ('cn_shipping', min(int(c.value), o.cn_shipping)),
    },
    'ENTRY_COUPON': {
        CT.AMOUNT_DEDUCTION: lambda e, c: ('amount_usd', min(e.amount, float(c.value))),
        CT.PERCENT_DEDUCTION: lambda e, c: ('amount_usd', e.amount * float(c.value)),
    },
    'FINAL': {
        'DEFAULT': lambda us_sale, cn_shipping: us_sale + cn_shipping,
        'WECHAT': lambda us_sale, shipping: us_sale + shipping,
        'IOS': lambda us_sale, shipping: us_sale + shipping
    },
    'LOGISTIC': {
        # first pound $9.99, next pound $4.99
        'DEFAULT': lambda weight: 4.99 * float(weight)/500 + 9.99 if weight else 0
    },
    'WITH_FX_RATE': _with_fx_rate
})


LOGISTIC_RATE = 0.085
MARGIN = 1.12
FOREX_RATE = 6.3

COST_PRICE = lambda china_price, weight: china_price + LOGISTIC_RATE * weight
CURR_PRICE = lambda cost_price: float((str(cost_price/FOREX_RATE * MARGIN).split(".")[0] + '.99'))
ORIG_PRICE = lambda price: float(str(price * 1.2).split(".")[0]+'.99')
