# -*- coding: utf-8 -*-
import math
import random
import datetime
import hashlib
from flask_login import current_user
from mongoengine.queryset import queryset_manager
from configs.enum import LOG_STATS
from configs.order_status import SHIPPING_HISTORY
import configs.signals as Signals
from configs.enum import PAYMENT_TYPE
from application.extensions import db, bcrypt
from application.utils import format_date

__all__ = ['Partner', 'LogisticProvider', 'ChannelProvider']


class WeightPrice(object):
    init_weight = 0
    continued_weight = 0
    init_price = 0
    continued_price = 0

    def get_shipping(self, weight):
        if weight <= 0:
            return 0
        if weight <= self.init_weight:
            return self.init_price
        return round(
            self.init_price +
            math.ceil((float(weight) - self.init_weight) / self.continued_weight) *
            self.continued_price,
            ndigits=2)


class LogisticProvider(db.Document, WeightPrice):
    meta = {
        'db_alias': 'order_db'
    }
    name = db.StringField()
    display_name = db.StringField()
    description = db.StringField()
    service_intro = db.DictField()
    logo = db.StringField()
    country = db.StringField()
    is_active = db.BooleanField(default=False)

    rule_desc = db.StringField()
    init_price = db.FloatField(required=True)
    init_weight = db.IntField(required=True)
    continued_price = db.FloatField(required=True)
    continued_weight = db.IntField(required=True)
    init_coin = db.IntField(default=0)

    features = db.ListField(db.StringField())
    promotion = db.StringField(default='')

    limited_weight = db.IntField(required=True)
    limited_category = db.ListField(db.StringField())
    is_recommended = db.BooleanField(default=False)

    rating = db.DecimalField(precision=1)
    rating_users = db.IntField()

    def __repr__(self):
        return '<LogisticProvider {}>'.format(self.name)

    # TODO: memoize here
    @classmethod
    def get_provider_shipping(cls, logistic_name, country, weight):
        if not logistic_name:
            logistic_name = 'default'
        provider = cls.objects(name=logistic_name, country=country).first()
        return provider.get_shipping(weight)

    @queryset_manager
    def active(doc_cls, queryset):
        return queryset.filter(is_active=True)

    def to_json(self):
        return dict(
            name = self.name,
            display_name = self.display_name,
            service_intro = self.service_intro,
            desc = self.description)


class Partner(db.Document):
    name = db.StringField(unique=True)
    auth = db.StringField()
    _password = db.StringField()
    description = db.StringField()

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.save()

    @classmethod
    def create(cls, name, password, description):
        partner = cls(
            name=name,
            auth=hashlib.sha1(name).hexdigest(),
            description=description
        )
        partner.password = password

        partner.save()

    def check_password(self, password):
        if self.password is None:
            return False
        return bcrypt.check_password_hash(self.password, password)

    def __str__(self):
        return self.name

    @classmethod
    def authorization(cls, auth, password):

        partner = cls.objects(auth=auth.lower()).first()
        if partner:
            authenticated = partner.check_password(password)
        else:
            authenticated = False

        return partner, authenticated

    def get_shipping(self, weight):
        provider = LogisticProvider.objects.get(
            name=self.name)
        shipping = provider.get_shipping(weight)
        return shipping


class ChannelProvider(db.Document):
    meta = {
        'db_alias': 'order_db'
    }
    name = db.StringField()
    display_name = db.StringField()
    description = db.StringField()
    service_intro = db.DictField()
    country = db.StringField()
    is_active = db.BooleanField(default=False)

    shipping = db.FloatField(required=True)
    is_recommended = db.BooleanField(default=False)

    def __repr__(self):
        return '<ChannelProvider {}>'.format(self.name)

    @classmethod
    def get_shipping(cls, channel_name, country):
        if not channel_name:
            channel_name = 'default'
        provider = cls.objects(name=channel_name, country=country).first()
        return provider.shipping

    @queryset_manager
    def active(doc_cls, queryset):
        return queryset.filter(is_active=True)

    def to_json(self):
        return dict(
            name = self.name,
            display_name = self.display_name,
            service_intro = self.service_intro,
            desc = self.description)
