# -*- coding: utf-8 -*-

from . import admin, website, frontend


default_blueprints = [
    frontend.frontend,
]

default_blueprints.extend(website.website_blueprints)
