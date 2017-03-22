# encoding: utf-8
import application.models as Models
from configs import signals as Signals
import application.services.jobs as Jobs
from flask import render_template
from configs.order_status import ORDER_STATUS_DESC, SHIPPING_HISTORY

@Signals.user_signup.connect
def noti_user_signup(sender, user):
    title = "您已成功注册"
    message = "请进入小程序登录"
    Jobs.noti.send_mail.delay([user.account.email], title, message)

def noti_order(order, status):
    user = order.customer
    title = u"Maybi订单状态改变"
    status_desc = ORDER_STATUS_DESC.get(status)
    status_history = SHIPPING_HISTORY.get(status)
    message = render_template('email/order_stat_changed.html',
            user=user,
            order=order,
            status_history=status_history,
            status_desc = status_desc
        )
    Jobs.noti.send_mail.delay([user.account.email], title, message)
