# -*- coding: utf-8 -*-

from .user import *
from .address import *
from .guest import *

def all():
    result = []
    models = [user, address, guest]
    for m in models:
        result += m.__all__
    return result


__all__ = all()
