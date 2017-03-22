# -*- coding: utf-8 -*-
from datetime import datetime
from application.extensions import db


__all__ = ['Address']


class Address(db.Document):
    created_at = db.DateTimeField(default=datetime.utcnow)

    # address detail
    country = db.StringField(required=True)
    state = db.StringField(required=True)
    city = db.StringField()
    street1 = db.StringField()
    street2 = db.StringField()
    postcode = db.StringField()

    # receiver infomation
    receiver = db.StringField(required=True)
    mobile_number = db.StringField()

    def __unicode__(self):
        return '%s' % str(self.id)

    @property
    def fields(self):
        return ['country', 'state', 'city', 'street1', 'street2', 'postcode',
                'receiver', 'mobile_number']

    def to_json(self):
        result = {f: getattr(self, f) for f in self.fields}
        result.update({'id': str(self.id)})
        return result
