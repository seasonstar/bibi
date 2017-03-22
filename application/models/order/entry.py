# -*- coding: utf-8 -*-
import time
from mongoengine import signals
from datetime import datetime
from bson.dbref import DBRef
from flask_login import current_user
from application.extensions import db

__all__ = ['BaseEntry', 'OrderEntry']


def get_time():
    return unicode(time.time())


class BaseEntry(db.Document):
    meta = {
        'allow_inheritance': True
    }

    spec = db.ReferenceField('ItemSpec')
    item = db.ReferenceField('Item')

    amount_usd = db.FloatField(default=0)
    amount = db.FloatField(default=0) #CNY

    quantity = db.IntField(default=1, required=True)
    unit_price = db.FloatField(default=0)

    # after discount
    discount = db.ListField(db.DictField())

    modified = db.DateTimeField()
    created_at = db.DateTimeField(default=datetime.utcnow)

    @property
    def is_available(self):
        return (self.spec.availability and self.item.availability)

    def __unicode__(self):
        return '%s' % self.id

    def __repr__(self):
        # __repr__ method can be used by flask-cache
        return '{}({}:{})'.format(self.__class__.__name__,
                                  self.item_spec_snapshot.sku, self.quantity)

    def update_amount(self):
        from application.models import ForexRate
        self.unit_price = self.item_spec_snapshot.price
        unit_price_cny = self.unit_price * ForexRate.get()
        self.amount_usd = self.unit_price * self.quantity
        self.amount = unit_price_cny * self.quantity
        self.save()

    def to_json(self, snapshot=False):
        item = self.item_snapshot
        spec = self.item_spec_snapshot
        item_json = item.to_simple_json()
        return dict(
            id=str(self.id),
            item=item_json,
            spec=spec.to_json(),
            unit_price=self.unit_price,
            amount=self.amount,
            quantity=self.quantity,
            weight=item.weight)

    def clean(self):
        if self.spec and not self.item:
            self.item = self.spec.item


class OrderEntry(BaseEntry):
    meta = {
        'db_alias': 'order_db',
    }

    _item_snapshot = db.ReferenceField('ItemSnapshot') # store the info of the item when an order is produced
    _item_spec_snapshot = db.ReferenceField('ItemSpecSnapshot')

    remark = db.StringField()
    shipping_info = db.DictField()


    @property
    def item_snapshot(self):
        return self._item_snapshot or self.item

    @property
    def item_spec_snapshot(self):
        return self._item_spec_snapshot or self.spec

    @property
    def item_changed(self):
        if self.item_spec_snapshot and self.item_snapshot:
            return self.item_snapshot.is_changed or self.item_spec_snapshot.is_changed
        else:
            return False

    def create_snapshot(self, item=None, spec=None):
        if not spec:
            spec = self.spec
        if not item:
            item = self.spec.item
        from application import models as Models

        if not self._item_snapshot:
            item_snapshot = Models.ItemSnapshot.create(item)
            self._item_snapshot = item_snapshot

            self._item_snapshot.price = item.price
            self._item_snapshot.save()

        if not self._item_spec_snapshot:
            item_spec_snapshot = Models.ItemSpecSnapshot.create(
                spec, item_snapshot)
            self._item_spec_snapshot = item_spec_snapshot

            self._item_spec_snapshot.price = spec.price
            self._item_spec_snapshot.save()

        self.save()
        return self._item_snapshot, self._item_spec_snapshot

    def update_snapshot(self):
        if not (self._item_spec_snapshot and self._item_snapshot):
            return self.create_snapshot()

        self.item_snapshot.update_to_head()
        self.item_spec_snapshot.update_to_head()
        return self.save()
