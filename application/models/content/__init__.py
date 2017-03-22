# -*- coding: utf-8 -*-

from .board import *
from .banner import *
from .post import *


def all():
    result = []
    models = [board, banner, post]
    for m in models:
        result += m.__all__
    return result


__all__ = all()
