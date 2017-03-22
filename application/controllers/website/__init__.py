# -*- coding: utf-8 -*-

from . import home
from . import auth
from . import user
from . import address
from . import order
from . import cart
from . import item
from . import logistic
from . import payment
from . import post

website_blueprints = [
    home.home,
    auth.auth,
    user.user,
    address.address,
    order.order,
    cart.cart,
    item.item,
    logistic.logistic,
    payment.payment,
    post.post,
]
