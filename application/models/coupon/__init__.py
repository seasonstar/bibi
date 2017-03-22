# -*- coding: utf-8 -*-

from .coupon import *
from .wallet import *

def all():
    result = []
    models = [coupon, wallet]
    for m in models:
        result += m.__all__
    return result


__all__ = all()
