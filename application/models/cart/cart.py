# -*- coding: utf-8 -*-

from application.extensions import db


__all__ = ['Cart', 'EntrySpec', 'CartEntry']


class EntrySpec(db.Document):
    meta = {
        'db_alias': 'cart_db',
        'indexes': ['sku', 'item_id', ]
    }

    sku = db.IntField(required=True, unique=True)

    item_id = db.IntField()
    title = db.StringField()

    primary_image = db.StringField()
    item_available = db.BooleanField()

    price = db.FloatField()
    available = db.BooleanField()
    attributes = db.DictField()
    images = db.ListField(db.StringField())

    attribute_list = db.ListField(db.StringField())
    attribute_desc = db.DictField()

    brand = db.DictField()

    last_update_date = db.DateTimeField()

    carts = db.ListField(db.ReferenceField('Cart'))
    last_empty_date = db.DateTimeField()


class CartEntry(db.EmbeddedDocument):
    sku = db.IntField(required=True)
    quantity = db.IntField(default=1, required=True)
    created_at = db.DateTimeField()

    first_price = db.FloatField(default=0)


class Cart(db.Document):
    meta = {
        'db_alias': 'cart_db',
        'indexes': ['user_id', 'session_key']
    }
    entries = db.EmbeddedDocumentListField('CartEntry')

    user_id = db.StringField()
    session_key = db.StringField()


    def __repr__(self):
        return '<Cart: {}>'.format(self.id)
