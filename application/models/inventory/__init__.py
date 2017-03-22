# -*- coding: utf-8 -*-

from .brand import *
from .category import *
from .item import *
from .price import *
from .tag import *
from .vendor import *
from .statistics import *

def all():
    result = []
    models = [brand, category, item, price, tag, vendor, statistics]
    for m in models:
        result += m.__all__
    return result


__all__ = all()
