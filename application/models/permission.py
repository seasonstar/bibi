# -*- coding: utf-8 -*-
from application.extensions import db
from configs.enum import USER_ROLE


__all__ = ['BackendPermission', 'Role']


class BackendPermission(db.Document):
    meta = {
        'indexes': ['name'],
    }

    name = db.StringField(required=True, unique=True)
    roles = db.ListField(db.ReferenceField('Role'))


class Role(db.Document):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)

    def __unicode__(self):
        return self.name

    def __eq__(self, other):
        return (self.name == other or
                self.name == getattr(other, 'name', None))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name)
