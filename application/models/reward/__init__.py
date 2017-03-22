# -*- coding: utf-8 -*-
from .coin import *

def all():
    result = []
    models = [coin]
    for m in models:
        result += m.__all__
    return result


__all__ = all()
