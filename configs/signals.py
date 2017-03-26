# -*- coding: utf-8 -*-

from blinker import Namespace

_signals = Namespace()


noti = _signals.signal('noti')

# user actions
user_signup = _signals.signal('user_signup')

ref_visit = _signals.signal('ref_visit')
item_visit = _signals.signal('item_visit')
item_bought = _signals.signal('item_bought')
coupon_received = _signals.signal('coupon_received')

# system notification
cart_changed = _signals.signal('cart_changed')
payment_received = _signals.signal('payment_received')
# model events
order_created = _signals.signal('order_created')
order_finished = _signals.signal('order_finished')

order_logistic_stat_changed = _signals.signal('order_logistic_stat_changed')
logistic_stat_changed = _signals.signal('logistic_stat_changed')
logistic_auto_splitted = _signals.signal('logistic_auto_splitted')

order_status_changed = _signals.signal('order_status_changed')
logistic_info_updated = _signals.signal('logistic_info_updated')

express_tracking_updated = _signals.signal('express_tracking_updated')
