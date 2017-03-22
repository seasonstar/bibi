# -*- coding: utf-8 -*-
from datetime import datetime
from application.extensions import db
from application.models.inventory import Item


__all__ = ['Board', 'ChangeLog']

class ChangeLog(db.EmbeddedDocument):
    '''
    log all user actions of change for a board
    '''
    user = db.StringField()
    date = db.DateTimeField(required=True, default=datetime.utcnow)
    action = db.StringField()
    item = db.StringField()
    info = db.StringField()


class Board(db.Document):
    meta = {
        'db_alias': 'content_db',
        'indexes': ['published_at', 'title'],
        'ordering': ['-published_at']
    }
    title = db.StringField(required=True)
    description = db.StringField()
    status = db.StringField(default="PENDING", choices=["PUBLISHED", "PENDING"])
    board_type = db.StringField()
    items = db.ListField(db.StringField())
    image = db.StringField()
    author = db.StringField()
    participants = db.ListField(db.StringField())
    view_count = db.IntField(default=0)
    created_at = db.DateTimeField(default=datetime.utcnow)
    modified = db.DateTimeField()
    published_at = db.DateTimeField()
    expired_date = db.DateTimeField()

    def __unicode__(self):
        return '%s' % str(self.id)

    @classmethod
    def create(cls, user, board_type):
        default_title = str(datetime.utcnow().date())
        b = Board(
            title=default_title,
            author=user,
            board_type=board_type,
            participants=[user])
        b._add_log(user, 'NEW')
        b.save()

    @classmethod
    def get_board(cls, board_id):
        return cls.objects(id=board_id).first()


    def add_item(self, user, item):
        self._add_remove_item(user, 'ADD', item)

    def remove_item(self, user, item):
        self._add_remove_item(user, 'REMOVE', item)

    def publish(self, user):
        self.status = "PUBLISHED"
        self.published_at = datetime.utcnow()
        self._add_log(user, 'PUBLISH')

    def unpublish(self, user):
        self.status = "PENDING"
        self.published_at = None
        self._add_log(user, 'UNPUBLISH')

    def reorder_item(self, item, index):
        self.items.remove(item)
        self.items.insert(index, item)

    def add_comment(self, user, comment):
        self._add_log(user, 'COMMENT', info=comment)

    def _add_remove_item(self, user, action, item):
        if not item in self.items:
            self.items.append(item)
        else:
            self.items.remove(item)

        self._add_log(user, action, item)

    def _add_log(self, user, action, item=None, info=''):
        if not user in self.participants:
            self.participants.append(user)

        self.logs.insert(0, ChangeLog(user=user, action=action,
                                      item=item, info=info))
        self.save()

    def to_json(self):
        return dict(
            id=str(self.id),
            date=str(self.published_at),
            image=self.image,
            desc=self.description,
            title=self.title,
        )
