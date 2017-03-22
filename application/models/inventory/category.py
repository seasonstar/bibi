# -*- coding: utf-8 -*-
from application.extensions import db

__all__ = ['Category']

class Category(db.Document):
    meta = {
        'db_alias': 'inventory_db',
        'indexes': ['en']
    }
    en = db.StringField(required=True, unique=True)
    cn = db.StringField()
    level = db.IntField(required=True)
    logo = db.StringField()

    def __unicode__(self):
        return '%s' % self.en

    @classmethod
    def get_category_or_create(cls, sub, lv):
        category = cls.objects(en=sub, level=lv).first()
        if not category:
            category = cls(en=sub, level=lv).save()
        return category

    @classmethod
    def update_cn(cls, en, cn):
        cls.objects(en=en).update(set__cn=cn)

    def to_json(self):
        return dict(
            en=self.en,
            cn=self.cn,
            level=self.level,
            logo=self.logo)
