# -*- coding: utf-8 -*-
from application.extensions import db

__all__ = ['Brand']

class Brand(db.Document):
    meta = {
        'db_alias': 'inventory_db',
        'indexes': ['en']
    }
    en = db.StringField(required=True, unique=True)
    cn = db.StringField()
    description = db.StringField()
    logo = db.StringField()

    def __unicode__(self):
        return '%s' % self.en

    def to_json(self):
        return dict(
            id=str(self.id),
            en=self.en,
            cn=self.cn,
            logo=self.logo,
            description=self.description)

    @classmethod
    def get_brand_or_create(cls, en):
        try:
            brand = cls.objects.get(en=en)
        except:
            brand = cls(en=en).save()
        return brand
