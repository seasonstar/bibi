# -*- coding: utf-8 -*-
import datetime
from mongoengine.queryset import queryset_manager
from application.extensions import db
from application.utils import format_date

__all__ = ['Banner']

class Banner(db.Document):
    meta = {
        'db_alias': 'content_db',
        'indexes': ['published']
    }
    created_at = db.DateTimeField(
        default=datetime.datetime.utcnow, required=True)
    banner_type = db.StringField(default="BOARD", choices=['BOARD', 'URL'])
    target = db.StringField()
    img = db.StringField()
    date_from = db.DateTimeField(default=datetime.datetime.today())
    date_until = db.DateTimeField(default=datetime.datetime(2029, 12, 30))
    published = db.BooleanField(default=True)
    order = db.SequenceField()

    def __repr__(self):
        return '<Banner object: {}>'.format(str(self.id))

    @classmethod
    def get_latest(cls, n=10):
        now = datetime.datetime.now()
        docs = cls.objects(date_from__lte=now, date_until__gt=now).order_by(
            '-order', '-created_at').limit(n)
        return docs

    @property
    def target_obj(self):
        import application.models as Models
        if self.banner_type == 'BOARD':
            # if BOARD, return title
            return Models.Board.objects(id=self.target).first()
        return self.target

    def to_json(self):
        return {
            'type': self.banner_type,
            'target': self.target,
            'img': self.img,
            'created_at': format_date(self.created_at),
        }
