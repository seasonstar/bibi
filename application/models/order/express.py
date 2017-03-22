# -*- coding: utf-8 -*-
from datetime import datetime
from configs.enum import LOG_STATS
from application.extensions import db


__all__ = ['ExpressTracking', 'Express', 'ExpressRequestLog', 'PartnerExpressTracking']


class Express(db.Document):
    meta = {
        'indexes': ['name']
    }

    name = db.StringField(unique=True)
    cn_name = db.StringField()
    logo_url = db.StringField()
    desc = db.StringField()

    def to_json(self):
        return dict(
            key=self.name,
            name=self.cn_name,
            logo=self.logo_url,
            desc=self.desc)


class ExpressRequestLog(db.Document):
    created_at = db.DateTimeField(default=datetime.utcnow, required=True)
    company = db.StringField()
    number = db.StringField()
    respond = db.DictField()
    is_success = db.BooleanField()


STATE = {
        '1': '在途中',
        '2': '已揽收',
        '3': '已签收',
        '4': '退签',
        '5': '同城派送中',
        '6': '退回',
        '7': '转单'
    }


class ExpressTracking(db.Document):
    company = db.StringField(required=True)
    number = db.StringField(required=True, unique_with='company')
    to = db.StringField()
    ischeck = db.StringField(required=True, default='0')

    # 快递单当前签收状态，包括0在途中、1已揽收、2疑难、3已签收、4退签、5同城派送中、
    # 6退回、7转单等7个状态
    state = db.StringField()

    # Dictionary in data
    # {
    #     "context":"上海分拨中心/下车扫描 ",     /*内容*/
    #     "time":"2012-08-27 23:22:42",          /*时间，原始格式*/
    #     "ftime":"2012-08-27 23:22:42",        /*格式化后时间*/
    #     "status":"在途",
    #     "areaCode":"310000000000",
    #     "areaName":"上海市",
    # }
    data = db.ListField(db.DictField())

    # time
    created_at = db.DateTimeField(default=datetime.utcnow, required=True)
    is_subscribed = db.BooleanField(default=False)
    modified = db.DateTimeField()
    retries = db.IntField(default=0)

    @classmethod
    def find(cls, company, number):
        cls.objects(company=company, number=number).update_one(set__company=company,
                                                               set__number=number,
                                                               upsert=True)
        return cls.objects.get(company=company, number=number)

    @classmethod
    def subscribed(cls, company, number):
        obj = cls.objects(company=company, number=number, is_subscribed=True)
        return True if obj else False

    @classmethod
    def update_info(cls, data):
        cls.objects(company=data['com'], number=data['nu']).update_one(
            set__ischeck=data['ischeck'],
            set__state=STATE.get(data['state']),
            set__data=data['data'],
            set__modified=datetime.utcnow(),
            upsert=True)

    @property
    def is_checked(self):
        if self.ischeck and self.ischeck == '0':
            return False
        elif self.ischeck == '1':
            return True

    @property
    def history(self):
        result = []
        for d in self.data:
            formated = {k:v for k, v in d.items() if k in ['ftime', 'context']}
            result.append(formated)
        return result

    def to_json(self):
        return dict(
            company=self.company,
            number=self.number,
            ischeck=self.ischeck,
            state=self.state,
            data=self.data
            )


class PartnerExpressTracking(db.Document):

    company = db.StringField(required=True)
    number = db.StringField(required=True, unique_with='company')
    data = db.ListField(db.DictField())
    created_at = db.DateTimeField(default=datetime.utcnow, required=True)
