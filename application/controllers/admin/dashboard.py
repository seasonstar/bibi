# -*- coding: utf-8 -*-
from flask import request, flash, jsonify, url_for, redirect
from flask_admin import expose, AdminIndexView
from flask_admin.base import MenuLink
from flask_babel import gettext as _
from flask_login import current_user, logout_user
from application.extensions import admin
from application.utils import redirect_url
import application.models as Models


class IndexView(AdminIndexView):
    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('frontend.login'))

    def is_accessible(self):
        return current_user.is_authenticated

    @expose('/')
    def index(self):
        return self.render("admin/index.html")
