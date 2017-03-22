# -*- coding: utf-8 -*-
from datetime import datetime
from application.extensions import db

__all__ = ['LogisticLog']

class LogisticLog(db.Document):
    meta = {
        'db_alias': 'log_db',
        'allow_inheritance': True,
        'indexes': ['logistic_id', 'timestamp'],
        'ordering': ['-timestamp'],
    }
    log_type = db.StringField()
    logistic_id = db.ObjectIdField(required=True)
    timestamp = db.DateTimeField(default=datetime.utcnow)
    user_id = db.StringField(required=False)
    info = db.DictField()

    @classmethod
    def create(cls, log, data, user_id='system'):
        return cls(logistic_id=log.id, info=data, user_id=user_id).save()
