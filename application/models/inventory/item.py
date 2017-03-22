# -*- coding: utf-8 -*-
from datetime import datetime
from math import ceil

from mongoengine.errors import DoesNotExist
from flask import current_app, url_for, g
from application.extensions import db
from .brand import Brand
from .category import Category
from .tag import Tag
from .vendor import Vendor
from .price import PriceHistory
from .statistics import Statistics
from configs.enum import SEX_TAG, CURRENCY, ITEM_STATUS

from application.utils import update_modified

__all__ = ['Item', 'ItemSpec']


@update_modified.apply
class Item(db.Document):
    meta = {
        'db_alias': 'inventory_db',
        'indexes': ['item_id', 'url', 'web_id', 'price', 'brand', 'main_category', 'sub_category',
                    'vendor', 'title', 'num_views','attributes', 'created_at'],
        'ordering': ['price']
    }

    item_id = db.SequenceField(required=True, unique=True, primary_key=True) # id
    url = db.StringField(required=True)
    web_id = db.StringField(required=True, unique=True)

    ## price
    currency = db.StringField(required=True, choices=CURRENCY)
    original_price = db.FloatField(required=True, min_value=0)
    price = db.FloatField(required=True, min_value=0)
    china_price = db.FloatField(min_value=0, default=0)
    discount = db.IntField()

    primary_img = db.StringField(required=True)

    # basic information
    vendor = db.StringField(required=True)
    brand = db.StringField(required=True)
    main_category = db.StringField(required=True)
    sub_category = db.StringField(required=True)
    sex_tag = db.StringField(required=True, choices=SEX_TAG)
    tags = db.ListField(db.StringField())

    # descritpion
    title = db.StringField(required=True)
    title_en = db.StringField()
    description = db.StringField(default='')

    attributes = db.ListField(db.StringField())

    # 如果有材质的话，以材质开头
    information = db.ListField(db.StringField())

    size_lookup = db.DictField(default={})
    extra = db.DictField(default={})

    stock = db.IntField(default=-1)

    # ratings for editors
    rating = db.FloatField(default=0)
    num_rates = db.IntField(default=0)

    # extra
    num_favors = db.IntField(default=0)
    num_likes = db.IntField(default=0)
    num_views = db.IntField(default=0)
    num_buy = db.IntField(default=0)

    status = db.StringField(default=ITEM_STATUS.NEW, required=True,
        choices=ITEM_STATUS)
    availability = db.BooleanField(default=True, required=True)

    # time
    created_at = db.DateTimeField(default=datetime.utcnow, required=True)
    modified = db.DateTimeField()
    creator = db.StringField()

    weight = db.FloatField()
    time_limited = db.BooleanField(default=False)

    lookup_table = db.StringField()
    size_chart = db.ListField(db.StringField())

    fields_to_log = {
        'url', 'original_price', 'price', 'discount', 'primary_img',
        'vendor', 'brand', 'main_category', 'sub_category', 'sex_tag', 'tags',
        'availability',
    }

    def __unicode__(self):
        return '%s' % self.item_id

    def __repr__(self):
        return '%s' % self.item_id

    @db.queryset_manager
    def available_items(doc_cls, queryset):
        return queryset.filter(availability=True)

    @property
    def specs(self):
        return ItemSpec.objects(item_id=self.item_id)

    @property
    def available_specs(self):
        return ItemSpec.objects(item_id=self.item_id, availability=True)

    @property
    def small_thumbnail(self):
        return self.primary_img[:23] + 'thumbnails/150x150/' + self.primary_img[23:]

    @property
    def large_thumbnail(self):
        return self.primary_img[:23] + 'thumbnails/400x400/' + self.primary_img[23:]

    @classmethod
    def create(cls, item):
        meta = item['meta']
        specs = item.get('specs',[])

        i = Item.objects(web_id=meta['web_id'])
        if i:
            item['meta']['status'] = ITEM_STATUS.MOD
            return cls.modify(item)

        # If category, brand and tags does not exisit then create.
        Category.get_category_or_create(meta['main_category'], 1)
        Category.get_category_or_create(meta['sub_category'], 2)
        Brand.get_brand_or_create(meta['brand'])
        Vendor.get_or_create(meta['vendor'])
        for tag in meta['tags']:
            Tag.get_tag_or_create(tag)

        Statistics.create(meta['main_category'], meta['sub_category'],
            meta['brand'], meta['tags'], meta['sex_tag'])

        item = Item(**meta).save()
        item_id = item.item_id

        # Keep item specs clean. Remove accidentally left useless specs.
        old_specs = ItemSpec.objects(item_id=item_id)
        for spec in old_specs:
            spec.delete()

        for spec in specs:
            spec['item_id'] = item_id
            ItemSpec(**spec).save()

        PriceHistory.upsert_price_history(item_id, meta['price'])

        return item_id

    @classmethod
    def modify(cls, new_item, current_price=None):
        # If the item does not exist in our db, then do not trust the coming
        # mod data.
        try:
            old_item = Item.objects.get(web_id=new_item['meta']['web_id'])
        except DoesNotExist:
            current_app.logger.warning('crawler send item not exist in db: {}'.format(new_item))
            return

        # Old item is an mongoengine object.
        # New item is a dictionary.
        cls.update_item(old_item, new_item)
        old_item.save()

        if current_price:
            PriceHistory.upsert_price_history(old_item.item_id, current_price)

        return old_item.item_id

    @classmethod
    def update_item(cls, old_item, new_item):
        meta = new_item['meta']

        # If category, brand and tags does not exisit then create.
        Category.get_category_or_create(meta['main_category'], 1)
        Category.get_category_or_create(meta['sub_category'], 2)
        Brand.get_brand_or_create(meta['brand'])
        Vendor.get_or_create(meta['vendor'])
        Statistics.create(meta['main_category'], meta['sub_category'],
            meta['brand'], meta['tags'], meta['sex_tag'])

        for k, v in meta.items():
            setattr(old_item, k, v)
        old_item.save()

    @classmethod
    def delete_item(cls, web_id):
        try:
            item = cls.objects.get(web_id=web_id)
            item.status = 'DEL'
            item.availability = False
            item.save()
            return item.item_id
        except DoesNotExist:
            pass


    def to_simple_json(self):
        return dict(
            id=str(self.item_id),
            title=self.title,
            price=getattr(self, 'price_details', lambda:'')(),
            primary_image=self.primary_img,
            status=self.status)

    def price_details(self):
        return dict(price=self.price,
                    orig_price= self.original_price,
                    discount=ceil(((self.original_price-self.price)/self.original_price) * 100),
                    )


@update_modified.apply
class ItemSpec(db.Document):
    meta = {
        'db_alias': 'inventory_db',
        'indexes': ['item_id', 'web_sku', 'sku', 'price', 'original_price',
                    'availability', 'attributes', 'created_at', 'stock'],
        'ordering': ['price']
    }

    item_id = db.IntField(required=True)
    sku = db.SequenceField(required=True, unique=True, primary_key=True)
    web_sku = db.StringField(required=True)

    images = db.ListField(db.StringField(required=True))

    original_price = db.FloatField(required=True, min_value=0)
    price = db.FloatField(required=True, min_value=0)
    china_price = db.FloatField(min_value=0, default=0)

    availability = db.BooleanField(default=True, required=True)
    stock = db.IntField(default=-1)

    # spec.attributes: {color: 'Blue', size: 'M'}
    attributes = db.DictField()
    shipping_info = db.DictField()

    created_at = db.DateTimeField(default=datetime.utcnow, required=True)
    modified = db.DateTimeField()

    url = db.StringField()

    extra = db.DictField(default={})

    @property
    def item(self):
        return Item.objects(item_id=self.item_id).first()

    def __unicode__(self):
        return '%s' % self.sku

    def update_spec(self, new_spec):
        for k, v in new_spec.items():
            setattr(self, k, v)
        self.save()
