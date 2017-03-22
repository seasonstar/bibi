# -*- coding: utf-8 -*-
import datetime

from flask import redirect, url_for, request
from flask_admin.contrib.mongoengine import ModelView
from flask_admin import BaseView, expose, AdminIndexView
from flask_admin.base import MenuLink
from flask_babel import gettext as _
from flask_login import current_user

import application.models as Models
from application.utils import format_date
from application.extensions import admin
from .dashboard import IndexView

admin._views = [IndexView(name=_("Dashboard"))]


class Roled(object):

    def is_accessible(self):
        roles_accepted = getattr(self, '_permission', 'admin')

        m = Models.BackendPermission.objects(
            name=roles_accepted).first()
        if 'ADMIN' in current_user.roles:
            return True
        if m.roles:
            accessible = any(
                [role in current_user.roles for role in m.roles]
            )
            return accessible
        return False

    def _handle_view(self, name, *args, **kwargs):
        if not current_user.is_authenticated or not self.is_accessible():
            return redirect(url_for(
                'frontend.login',
                next=url_for(self.endpoint + '.' + name, **request.args)))


class AdminView(Roled, BaseView):
    pass


class PermissionModelView(Roled, ModelView):

    def __init__(self, *args, **kwargs):
        self._permission = kwargs.pop('permission', 'admin')
        return super(PermissionModelView, self).__init__(*args, **kwargs)


class MBModelView(PermissionModelView):
    column_type_formatters = {datetime.datetime:
                              lambda view, value: format_date(value)}


class PermissionMenuLink(Roled, MenuLink):
    def __init__(self, *args, **kwargs):
        self.permission = kwargs.pop('permission', 'admin')
        return super(PermissionMenuLink, self).__init__(*args, **kwargs)


class AuthenticatedMenuLink(MenuLink):
    def is_accessible(self):
        return current_user.is_authenticated


class NotAuthenticatedMenuLink(MenuLink):
    def is_accessible(self):
        return not current_user.is_authenticated


from . import models, dashboard, content, order
