# -*- coding: utf-8 -*-
import datetime
from application.extensions import db


__all__ = ['ItemSnapshot', 'ItemSpecSnapshot']


''''
The collection name of snapshot is
'item' (no abstract model), and the
HEAD is a index which pointed to
the unique primary_key of the item.

       +--------+
       |  HEAD  |
       +--------+
       |SNAPSHOT|
       +--------+
       |SNAPSHOT|
       +--------+
       |SNAPSHOT|
       +--------+
       |SNAPSHOT|
       +--------+
'''

def get_fields(cls):
    for k in cls.__dict__.keys():
        if not k.startswith('_'):
            yield k


class ItemSnapshot(db.DynamicDocument):
    meta = {
        'db_alias': 'order_db',
        'indexes': ['item_id', 'web_id', 'head']
    }
    head = db.IntField(required=True, default=0)
    specs = db.ListField(db.ReferenceField('ItemSpecSnapshot'))
    created_at = db.DateTimeField(default=datetime.datetime.utcnow())

    def __unicode__(self):
        return '%s' % self.head

    @classmethod
    def create(cls, item):
        data = item._data
        shot = cls(**data)
        shot.head = shot.item_id
        shot.save()
        return shot

    @property
    def small_thumbnail(self):
        return self.primary_img[:23] + 'thumbnails/150x150/' + self.primary_img[23:]

    @property
    def large_thumbnail(self):
        return self.primary_img[:23] + 'thumbnails/400x400/' + self.primary_img[23:]

    def update_to_head(self):

        from application.models import Item

        head = Item.objects(item_id=self.head).first()

        if head:
            data = head._data
            for k, v in data.items():
                setattr(self, k, v)
            self.save()
        else:
            return self

    @property
    def is_changed(self):
        from application.models import Item
        head = Item.objects(item_id=self.head).first()
        if not head: return True
        if self.modified != head.modified:return True

        return False


class ItemSpecSnapshot(db.DynamicDocument):
    meta = {
        'db_alias': 'order_db',
        'indexes': ['item_id', 'sku', 'head']
    }
    head = db.IntField(required=True, default=0)
    item = db.ReferenceField('ItemSnapshot')
    created_at = db.DateTimeField(default=datetime.datetime.utcnow())

    def __unicode__(self):
        return '%s:%s' % (self.item.head, self.head)

    @classmethod
    def create(cls, spec, itemsnapshot=None):
        if not itemsnapshot:
            itemsnapshot = ItemSnapshot.create(spec.item).save()
        data = spec._data
        shot = cls(**data)
        shot.head = shot.sku
        shot.item = itemsnapshot
        shot.save()

        itemsnapshot.specs.append(shot)
        itemsnapshot.save()
        return shot

    def update_to_head(self):
        from application.models import ItemSpec
        head = ItemSpec.objects(sku=self.head).first()

        if self.item and isinstance(self.item, ItemSnapshot):
            self.item.update_to_head()

        if head:
            data = head._data
            for k, v in data.items():
                setattr(self, k, v)
            self.save()
        else:
            return self

    @property
    def is_changed(self):
        from application.models import ItemSpec
        head = ItemSpec.objects(sku=self.head).first()
        if not head: return True
        if self.modified != head.modified: return True

        return False
