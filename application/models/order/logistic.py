# -*- coding: utf-8 -*-
import math
import random
import datetime
import hashlib
from flask_login import current_user
from configs.enum import LOG_STATS
from configs.order_status import SHIPPING_HISTORY
import configs.signals as Signals
from configs.enum import PAYMENT_TYPE
from application.extensions import db
from application.utils import format_date

__all__ = ['LogisticDetail', 'Logistic',
           'LogisticDelay', 'LogisticRemark', 'LogisticIrregular']

date_format = '%Y-%m-%d %H:%M'


def gen_uid():
    current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    num = random.randint(1, 999)
    return 'MB' + current_time + str(num)


def get_date(obj, field):
    value = getattr(obj, field)
    return value.strftime(date_format) if value else ''


class LogisticDetail(db.EmbeddedDocument):
    partner_tracking_no = db.StringField(default='', required=True)
    cn_tracking_no = db.StringField(default='')
    cn_logistic_name = db.StringField(default='')
    carrier_tracking_no = db.StringField(default='')
    partner = db.ReferenceField('Partner')
    channel = db.StringField()
    route = db.StringField(default="DEFAULT")

    pending_review_date = db.DateTimeField()
    transfer_approved_date = db.DateTimeField()
    warehouse_in_date = db.DateTimeField()
    payment_received_date = db.DateTimeField(default=datetime.datetime.utcnow)
    processing_date = db.DateTimeField()
    shipping_date = db.DateTimeField()
    port_arrived_date = db.DateTimeField()
    received_date = db.DateTimeField()
    pending_return_date = db.DateTimeField()
    returned_date = db.DateTimeField()

    remarks = db.EmbeddedDocumentListField('LogisticRemark')
    delay_details = db.EmbeddedDocumentListField('LogisticDelay')
    irregular_details = db.EmbeddedDocumentListField('LogisticIrregular')
    extra = db.StringField(default='')

    real_weight = db.FloatField(default=0)
    real_fee = db.FloatField()

    modified = db.DateTimeField()
    modified_by = db.StringField()
    status = db.StringField(max_length=255, required=True,
                            choices=LOG_STATS,
                            default=LOG_STATS.PAYMENT_RECEIVED)
    attr_by_log_stat = {
        'PENDING_REVIEW': 'pending_review_date',
        'TRANSFER_APPROVED': 'transfer_approved_date',
        'WAREHOUSE_IN': 'warehouse_in_date',
        'PAYMENT_RECEIVED': 'payment_received_date',
        'PROCESSING': 'processing_date',
        'SHIPPING': 'shipping_date',
        'PORT_ARRIVED': 'port_arrived_date',
        'RECEIVED': 'received_date',
        'PENDING_RETURN': 'pending_return_date',
        'RETURNED': 'returned_date'
    }

    fields_to_log = {
        'cn_tracking_no', 'partner_tracking_no', 'status',
        'cn_logistic_name', 'partner', 'payment_received_date',
        'shipping_date', 'processing_date',
        'received_date', 'port_arrived_date', 'modified_by',
    }

    def next(self):
        if self.status in LOG_STATS and self.status != 'RECEIVED':
            self.status = LOG_STATS[LOG_STATS.index(self.status) + 1]

    @property
    def cn_logistic(self):
        from application.models import Express
        return Express.objects(name=self.cn_logistic_name).first()


class LogisticRemark(db.EmbeddedDocument):
    content = db.StringField()
    creator = db.StringField()
    created_at = db.DateTimeField(default=datetime.datetime.utcnow)


class LogisticDelay(db.EmbeddedDocument):
    reason = db.StringField()
    is_done = db.BooleanField(default=False)
    status = db.StringField(choices=LOG_STATS)
    creator = db.StringField()
    created_at = db.DateTimeField(default=datetime.datetime.utcnow)


class LogisticIrregular(db.EmbeddedDocument):
    steps = db.DictField()
    process_status = db.StringField(
        choices=['WAITING_PROCESS', 'PROCESSING', 'PROCESSED'],
        default='WAITING_PROCESS')
    irr_at_status = db.StringField(choices=LOG_STATS)
    irr_type = db.StringField(default=u'OTHER')

    reason = db.StringField()
    desc = db.StringField()
    creator = db.StringField()
    created_at = db.DateTimeField(default=datetime.datetime.utcnow)
    remarks = db.EmbeddedDocumentListField('LogisticRemark')


class Logistic(db.Document):
    meta = {
        'db_alias': 'order_db',
        'indexes': ['is_closed', '-created_at',
                    'order', 'entries',
                    'detail.status',
                    'detail.channel',
                    'detail.modified',
                    'detail.cn_tracking_no',
                    'detail.cn_logistic_name',
                    'detail.payment_received_date',
                    'detail.processing_date',
                    'detail.shipping_date',
                    'detail.port_arrived_date',
                    'detail.received_date',
                    'detail.partner',
                    'detail.partner_tracking_no',
                    ('detail.status', '-created_at'),
        ]
    }
    order = db.ReferenceField('Order', required=True)
    entries = db.ListField(db.ReferenceField('OrderEntry'))
    returned_entries = db.ListField(db.ReferenceField('OrderEntry'))

    is_closed = db.BooleanField(default=False, required=True)
    close_reason = db.StringField()
    closed_at = db.DateTimeField()
    created_at = db.DateTimeField(
        required=True, default=datetime.datetime.utcnow
    )
    detail = db.EmbeddedDocumentField('LogisticDetail')

    def __unicode__(self):
        return '%s' % str(self.id)

    @property
    def estimated_weight(self):
        return sum(float(entry.item_snapshot.weight) * entry.quantity
                   for entry in self.entries)

    def to_json(self):
        detail = self.detail
        return dict(cn_tracking_no=detail.cn_tracking_no,
                    cn_logistic_name=detail.cn_logistic_name,
                    partner_tracking_no=detail.partner_tracking_no,
                    partner_name=detail.partner.name if detail.partner else '',
                    payment_received_date=get_date(detail, 'payment_received_date'),
                    processing_date=get_date(detail, 'processing_date'),
                    shipping_date=get_date(detail, 'shipping_date'),
                    port_arrived_date=get_date(detail, 'port_arrived_date'),
                    received_date=get_date(detail, 'received_date'),
                    estimated_weight=self.estimated_weight,
                    real_weight=detail.real_weight,
                    status=detail.status)

    @property
    def amount(self):
        return sum(entry.amount for entry in  self.entries)

    @property
    def amount_usd(self):
        return sum(entry.amount_usd for entry in  self.entries)

    @classmethod
    def create(cls, order):
        from application.models.order.partner import Partner

        def update_order(o):
            o.logistics.append(log)
            o.save()
            o.update_logistic_status()

        def create_logistic(order):
            log = cls(detail=LogisticDetail())
            log.order = order
            log.entries = order.entries
            log.detail.partner = Partner.objects().first()
            log.detail.partner_tracking_no = gen_uid()
            log.detail.status = order.status
            date_field = log.detail.attr_by_log_stat[order.status]
            setattr(log.detail, date_field, datetime.datetime.utcnow())

            log.save()
            return log

        log = create_logistic(order)
        update_order(order)
        return log

    @classmethod
    def merge_with(cls, los):

        if not type(los) is list:
            return False

        start = 0
        for index in range(len(los)-1):
            if los[index+1].detail.cn_tracking_no != \
                    los[start].detail.cn_tracking_no or \
                    los[index+1].order != los[0].order :
                return False

        for index in range(len(los)-1):
            map(lambda e: los[index+1].entries.append(e),
                los[index].entries)
            los[index].entries = []
            los[index].save()
            los[index].close(
                'merged with %s' %
                los[index+1].id, datetime.datetime.utcnow()
            )
            los[index+1].save()

            if index+1 == len(los)-1:
                comment = LogisticRemark(
                    content=u"合并单", creator=current_user.name
                )
                los[index+1].detail.remarks.append(comment)
                los[index+1].save()
                return los[index+1]

    def close(self, reason, time=None):
        self.is_closed = True
        self.close_reason = reason
        self.closed_at = time or datetime.datetime.utcnow()
        self.save()
        order = self.order
        if self in order.logistics:
            order.logistics.remove(self)
            order.closed_logistics.append(self)
            order.save()

    def fork_by_entries(self, entry_ids):
        def get_entry(entries, eid):
            for e in entries:
                if str(eid) == str(e.id):
                    return e
            return False

        if not type(entry_ids) is list:
            return False

        if len(self.entries) < 2:
            return False

        if self.detail.status != 'PAYMENT_RECEIVED':
            self.detail.status = 'PROCESSING'
            self.detail.processing_date = datetime.datetime.utcnow()
            self.save()
        forked_order = Logistic(detail=self.detail)
        entries = [get_entry(self.entries, e) for e in entry_ids]
        if not entries:
            False
        forked_order.entries = entries
        forked_order.order = self.order
        forked_order.save()
        self.order.logistics.append(forked_order)
        self.order.save()

        map(lambda e: self.entries.remove(e), entries)
        self.save()

        old_ptn = self.detail.partner_tracking_no
        new_ptn = gen_uid()
        forked_order.detail.partner_tracking_no = new_ptn

        remark = u"%s拆出了%s" % (old_ptn, new_ptn)
        forked_order.update_remark(remark, current_user.name)
        self.update_remark(remark, current_user.name)

        return self, forked_order

    def update_status(self, new_status):
        try:
            index = LOG_STATS.index(new_status)
        except ValueError:
            return

        log = self.detail
        old_status = log.status

        if index > LOG_STATS.index(old_status):
            log.status = new_status
            now = datetime.datetime.utcnow()
            date_field = log.attr_by_log_stat[new_status]
            if not getattr(log, date_field):
                setattr(log, date_field, now)
            self.save()

            self.order.update_logistic_status()

    def update_logistic(self, info):
        log = self.detail
        next_status = info.get('status', '')

        require = {
            'SHIPPING': ['cn_tracking_no', 'cn_logistic_name'],
        }
        if next_status in require.keys():
            values = require[next_status]
            for value in values:
                if value in info:
                    continue
                value = getattr(self.detail, value)
                if value in [None, '', 'None', '?', u'?', u'None',
                             'Undefined', u'Undefined']:
                    raise Exception("Fail to update logistic")

        if current_user and not current_user.is_anonymous:
            modified_by = current_user.name
        else:
            modified_by = 'system'

        self.update_status(next_status)

        remark = info.get('remark', None)
        if remark:
            self.update_remark(remark, modified_by)

        delay_content = info.get('delay', None)
        if delay_content:
            self.update_delay(delay_content, modified_by)

        irregularity = info.get('irregularity', None)
        if irregularity:
            self.update_irregularity(irregularity, modified_by)

        for field, value in info.items():
            if field in ['status']:
                continue
            setattr(log, field, value)
        self.save()

        Signals.logistic_stat_changed.send(
            'send to logistic partner', lo=self, status=next_status)

        Signals.logistic_info_updated.send('system', logistic=self)

    def update_remark(self, content, modified_by):
        remark = LogisticRemark(content=content, creator=modified_by)
        self.detail.remarks.append(remark)
        self.save()

    def update_delay(self, content, modified_by):
        delays = self.detail.delay_details.filter(status=self.detail.status)
        if delays:
            delays.update(reason=content, creator=modified_by)
        else:
            delay = LogisticDelay(
                reason=content, creator=modified_by,
                status=self.detail.status
            )
            self.detail.delay_details.append(delay)
        remark = LogisticRemark(content=content, creator=modified_by)
        self.detail.remarks.append(remark)
        self.save()

    def update_irregularity(self, irregularity, modified_by):
        irregularity.creator = modified_by
        self.detail.irregular_details.append(irregularity)
        self.save()

    @property
    def shipping_history(self):
        res = []
        status = self.detail.status
        for st in LOG_STATS:
            field = self.detail.attr_by_log_stat[st]
            val = getattr(self.detail, field)
            if not val:
                continue
            res.append({'time': format_date(val),
                        'desc': SHIPPING_HISTORY[st],
                        'status': st})
            if st == status:
                break
        return res

    @property
    def express_tracking(self):
        import application.models as Models
        com = self.detail.cn_logistic_name
        nu = self.detail.cn_tracking_no
        if com and nu:
            tracking = Models.ExpressTracking.find(
                company=com,
                number=nu)
            return tracking
        return None

    @classmethod
    def pre_save_post_validation(cls, sender, document, **kwargs):
        if not kwargs['created']:
            old_log = cls.objects(id=document.id).first().detail
            new_log = document.detail
            for field in LogisticDetail._fields:
                if field == 'modified':
                    continue
                if (getattr(old_log, field) != getattr(new_log, field)):
                    new_log.modified = datetime.datetime.utcnow()
                    if current_user and not current_user.is_anonymous:
                        new_log.modified_by = current_user.name
                    else:
                        new_log.modified_by = 'system'
                    return
        else:
            document.detail.modified = datetime.datetime.utcnow()


db.pre_save_post_validation.connect(Logistic.pre_save_post_validation,
                                    sender=Logistic)
