# -*- coding: utf-8 -*-

class Enum(list):
    ''' Enumeration class '''
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError

    def __add__(self, other):
        # list addition
        result = super(Enum, self).__add__(other)
        return Enum(result)


class TupleEnum(list):
    '''
     Enumeration class expecting element as 2-tuple
    '''
    def __getattr__(self, name):
        keys = [k for k, v in self]
        if name in keys:
            return name
        raise AttributeError

    def __add__(self, other):
        # list addition
        result = super(TupleEnum, self).__add__(other)
        return TupleEnum(result)

    def __contains__(self, key):
        keys = [k for k, v in self]
        return key in keys


class DictEnum(dict):
    __getattr__ = lambda self, k: DictEnum(self.get(k)) if type(self.get(k)) is dict else self.get(k)


# user
USER_GENDER = Enum(['M', 'F'])
USER_ROLE = Enum(['MEMBER',
                  'ADMIN',
                  'CUSTOMER_SERVICE',
                  'OPERATION',
                  'MARKETING',
                  'TESTER',  # whose orders' final will always be 0.01
                  'LOGISTIC'])

USER_STATUS = Enum(['ACTIVE', 'INACTIVE', 'NEW'])

# item
ITEM_STATUS = Enum(['NEW', 'MOD', 'DEL'])
SEX_TAG = Enum(['MEN', 'WOMEN',
                'GIRLS', 'BOYS', 'INFANTS', 'TODDLERS', 'MOMS',
                'UNCLASSIFIED', 'UNKNOWN'])

# order
ORDER_TYPE = Enum(['COMMODITY', 'TRANSFER'])
PAYMENT_TRADERS = Enum([
    'WEIXIN', 'PAYPAL'
])

PAYMENT_TYPE = Enum(['WITHOUT_TAX', 'WITH_TAX'])
PAYMENT_STATUS = Enum(['UNPAID', 'PAID'])
TRADE_TYPE = Enum(['INSTANCE', 'ESCROW'])
LOG_STATS = Enum(['PENDING_REVIEW', 'TRANSFER_APPROVED', 'WAREHOUSE_IN',
        'PAYMENT_RECEIVED', 'PROCESSING', 'SHIPPING', 'PORT_ARRIVED', 'RECEIVED',
        'PENDING_RETURN', 'RETURNED'])

ORDER_STATUS = Enum(['PAYMENT_PENDING', 'CANCELLED', 'ABNORMAL', 'ORDER_DELETED', \
                    'EXPIRED', 'REFUNDED'] +
                    LOG_STATS)

ORDER_SOURCES = Enum(['WECHAT', 'IOS', 'ANDROID', 'MANUALLY'])

CURRENCY = Enum(['USD', 'HKD', 'CNY'])

# coupon
COUPON_SCOPE = Enum(['ORDER', 'ENTRY'])
COUPON_TYPES = Enum([
    'NORMAL', 'AMOUNT_DEDUCTION', 'PERCENT_DEDUCTION',
    'FINAL_PERCENT_DEDUCTION',
    'FREE_SHIPPING', 'SHIPPING_DEDUCTION',
])
COUPON_APPLY = Enum(['AUTO', 'BY_CODE', 'BY_DISPLAY_ID'])

# tags
TAG_TYPES = TupleEnum([
    ('CATEGORY', 'tag of category type is used as level 3 category.'),
    ('MATERIAL', 'tag of material type denotes item materials.'),
    ('ELEMENT', 'tag of element type denotes special elements that the item contains.'),
    ('STYLE', 'tag of style type denotes the specific style of the item.')])


# Coin
COIN_ONETIME_TASK = Enum(['VERIFIED_ID'])
COIN_REPEAT_TASK = Enum(['SHARED', 'SECOND_SHARED', 'SHARED_ORDER', 'ORDER'])
COIN_TASK = COIN_REPEAT_TASK + COIN_ONETIME_TASK
COIN_TRADE_REASON = Enum([
    'PAY', 'OTHER', 'CANCEL', 'WITHDRAW', 'CUSTOMS', 'SHIPPING_FEE', 'PROMOTE', 'REFUND',
    'CONVERT'] +
    COIN_TASK)
COIN_TRADE_TYPE = Enum(['INCOME', 'OUTCOME'])
COIN_TYPE = Enum(['COIN', 'CASH'])


# noti
NOTI_TYPE = Enum([
    'SYSTEM', 'COMMENT', 'FOLLOW',
    'SHIPPING_DELAYED',
    'LOGISTIC_DELAYED',
    'ORDER_REFUNDED',
    'ADMIN_ORDER_PAID',  # Notify admins that an order is paid.
    'DAILY_ORDER_REPORT',
    'USER_SIGNUP',  # noti after user signup
    'POST_LIKED', 'REPLY',
] +
    ORDER_STATUS)

# noti channels
CHANNELS = Enum(['EMAIL', 'SMS', 'VOICE', 'WECHAT', 'WECHATFORMAL', 'IOS', 'NODEJS'])

QUEUE = Enum(['HIGH', 'NORMAL', 'LOW'])

# refunds
REFUND_TYPE = Enum(['CANCEL', 'RETURN', 'SUBSIDY', 'MANUALLY'])

# report
REPORT_TYPE = Enum(['ORDER', 'LOGISTIC', 'ORDER_SOURCE', 'EXPENDITURE', 'IOS_SIGNUP_SOURCE',
                    'SHARE_LOG', 'REFUND'])

# POST
POST_STATUS = Enum(['NEW', 'MOD', 'DEL'])
ACTIVITY_STATUS= Enum(['PENDING', 'PROCESSED', 'REFUSED'])
POST_TAG_TYPES = Enum(['TRADE', 'SERVICE', 'SHOW', 'UNCLASSIFIED'])
