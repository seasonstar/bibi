# -*- coding: utf-8 -*-
from application.extensions import db

__all__ = ['Vendor']


class Vendor(db.Document):
    name = db.StringField(required=True, unique=True)
    cn_name = db.StringField()
    logo = db.StringField()
    desc = db.StringField()
    country = db.StringField(default=u'美国')
    url = db.StringField()


    @classmethod
    def get_or_create(cls, name):
        vendor = cls.objects(name=name).first()
        if not vendor:
            vendor = cls(name=name).save()
        return vendor

    def to_json(self):
        return dict(
            name=self.name,
            cn_name=self.cn_name,
            logo=self.logo,
            desc=self.desc,
            country=self.country,
            url=self.url)
