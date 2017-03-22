# -*- coding: utf-8 -*-
ORDER_STATUS_DESC = {
    'PAYMENT_PENDING': u'未付款',
    'PAYMENT_RECEIVED': u'成功支付',
    'PENDING_REVIEW': u'核验清单',
    'TRANSFER_APPROVED': u'跟踪快递',
    'WAREHOUSE_IN': u'入库称重',
    'CANCELLED': u'订单取消',
    'ABNORMAL': u'订单异常',
    'ORDER_DELETED': u'订单删除',
    'EXPIRED': u'订单过期',
    'REFUNDED': u'已退款',
    'RETURNED': u'已退款',
    'PROCESSING': u'准备发货',
    'SHIPPING': u'正在运送',
    'PORT_ARRIVED': u'航班到港',
    'RECEIVED': u'包裹签收',
    'PENDING_RETURN': u'退款中',
    'RETURNING': u'退款中',
}


SHIPPING_HISTORY = {
    'PAYMENT_RECEIVED': u'您已成功支付，请等待系统确认；',
    'PENDING_REVIEW': u'您的订单已提交，将在12小时内为您核验清单',
    'TRANSFER_APPROVED': u'您的订单商品已通过审核，请将审核通过的商品寄到美比仓库地址，'+\
            u'寄送后请尽快填写包裹快递信息，方便仓库跟踪并确认商品物流信息',
    'WAREHOUSE_IN': u'您的商品已入仓验收，工作人员为你打包称重，请尽快提交运输订单并付款',
    'PROCESSING': u'您的订单已确认，正由仓库拣货，请等待发货；',
    'SHIPPING': u'您的订单已发货，敬请留意物流更新；',
    'PORT_ARRIVED': u'您的包裹已抵达港口',
    'RECEIVED': u'您的包裹已签收。',
    'PENDING_RETURN': u'因商品无货或取消订单，将马上为您操作退款。对您造成的不便表示万分歉意。请稍后留意邮件通知。',
    'RETURNING': u'您的包裹正在退回',
    'RETURNED': u'已退货',
}

ROUTES = {
    'DEFAULT': ['PAYMENT_RECEIVED', 'PROCESSING', 'SHIPPING', 'PORT_ARRIVED', 'RECEIVED'],
    'TRANSFER': ['PENDING_REVIEW', 'TRANSFER_APPROVED', 'WAREHOUSE_IN', 'PAYMENT_RECEIVED', 'SHIPPING', 'PORT_ARRIVED', 'RECEIVED']
}
