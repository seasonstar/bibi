# -*- coding: utf-8 -*-
from .user import *
from .permission import *
from .cart import *
from .coupon import *
from .inventory import *
from .order import *
from .reward import *
from .content import *
from .log import *

def all():
    result = []
    models = [user, permission, cart, coupon, inventory, order,
            reward, content, log]
    for m in models:
        result += m.__all__
    return result


__all__ = all()
