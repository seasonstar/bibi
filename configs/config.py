# -*- coding: utf-8 -*-

import os
import re
import socket
import datetime
from .enum import Enum
from pymongo import ReadPreference
from celery.schedules import crontab


_basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
TEMPLATE_DIR = os.path.join(_basedir,'application', 'templates')


E = Enum(['development', 'production', 'test'])
APP_NAME = Enum(['maybi', 'worker', 'admin'])


class BaseConfig(object):

    # Get app root path
    # ../../configs/config.py

    PROJECT = APP_NAME.maybi
    VERSION = '2016.15.05'
    DEBUG = True
    TESTING = False
    PROD = False

    # Flask Toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    DEBUG_TB_INTERCEPT_REDIRECTS
    DEBUG_TB_TEMPLATE_EDITOR_ENABLED = True
    DEBUG_TB_PROFILER_ENABLED = True
    DEBUG_TB_PANELS = [
        'flask_debugtoolbar.panels.versions.VersionDebugPanel',
        'flask_debugtoolbar.panels.timer.TimerDebugPanel',
        'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
        'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
        'flask_debugtoolbar.panels.config_vars.ConfigVarsDebugPanel',
        'flask_debugtoolbar.panels.template.TemplateDebugPanel',
        'flask_debugtoolbar.panels.logger.LoggingPanel',
        'flask_debugtoolbar.panels.profiler.ProfilerDebugPanel',
        'flask_mongoengine.panels.MongoDebugPanel'
    ]

    ENV = E.development

    ADMINS = frozenset(['season@maybi.cn'])

    # os.urandom(24)
    SECRET_KEY = 'WhatIsTheMeaningOfLife'
    IDCARD_KEY = 'HowAreYouDoing'
    CSRF_ENABLED = False
    WTF_CSRF_ENABLED = False

    UPLOAD_FOLDER = os.path.join(_basedir, 'application', 'static/csv/')

    AVATAR_FOLDER = os.path.join(_basedir, 'application/static/img/avatar')

    # ===========================================
    # Maybi
    #
    # flask session, should available for all sub domain
    # SESSION_COOKIE_DOMAIN = '.maybi.cn'
    # SERVER_NAME = 'maybi.cn'

    # Flask-login
    REMEMBER_COOKIE_DOMAIN = '.maybi.cn'
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=31)

    # ===========================================
    # Flask-PyMongo
    #
    # https://flask-pymongo.readthedocs.org/en/latest/

    MONGODB_SETTINGS = {
        'db': 'bibi',
        'host': 'localhost',
        'read_preference': ReadPreference.PRIMARY_PREFERRED,
        'port': 27017,
    }
    ORDER_DB_CONFIG = {
        'alias': 'order_db',
        'name': 'order',
        'host': 'localhost',
        'port': 27017,
    }

    INVENTORY_DB_CONFIG = {
        'alias': 'inventory_db',
        'name': 'inventory',
        'host': 'localhost',
        'port': 27017,
    }

    CART_DB_CONFIG = {
        'alias': 'cart_db',
        'name': 'cart',
        'host': 'localhost',
        'port': 27017,
    }

    CONTENT_DB_CONFIG = {
        'alias': 'content_db',
        'name': 'content',
        'host': 'localhost',
        'port': 27017,
    }

    LOG_DB_CONFIG = {
        'alias': 'log_db',
        'name': 'order',
        'host': 'localhost',
        'port': 27017,
    }

    SESSION_REDIS = {
        'host': 'localhost',
        'port': 6379,
        'db': 0,
        'encoding': 'utf-8',
        'encoding_errors': 'strict',
        'decode_responses': False
    }

    REDIS_CONFIG = {
        'host': 'localhost',
        'port': 6379,
        'db': 0,
        'encoding': 'utf-8',
        'encoding_errors': 'strict',
        'decode_responses': False
    }

    MONGO_INVENTORY_HOST = 'localhost'
    MONGO_INVENTORY_PORT = 27017
    MONGO_INVENTORY_DBNAME = 'inventory'

    # ===========================================
    # Flask-mail
    #
    # Should be imported from env var.
    # https://bitbucket.org/danjac/flask-mail/issue/3/problem-with-gmails-smtp-server
    MAIL_DEBUG = False
    MAIL_SERVER = ''
    #MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = ''
    MAIL_PASSWORD = ''
    DEFAULT_MAIL_SENDER = MAIL_USERNAME

    # ===========================================
    # Flask-babel
    #
    ACCEPT_LANGUAGES = ['zh','en']
    BABEL_DEFAULT_LOCALE = 'zh'

    # ===========================================
    # Flask-cache
    CACHE_TYPE = 'redis'

    TRACKING_EXCLUDE = (
        '^/favicon.ico',
        '^/static/',
        '^/admin/',
        '^/_debug_toolbar/',
    )

    CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//',
    CELERY_RESULT_BACKEND = 'amqp://guest:guest@localhost:5672//'

    CELERY_IMPORTS = (
        'application.services.jobs.image',
        'application.services.jobs.noti',
        'application.services.jobs.express',
        'application.services.scheduling.forex',
        'application.services.scheduling.express',
    )

    CELERYD_TASK_TIME_LIMIT = 300
    CELERYD_TASK_SOFT_TIME_LIMIT = 120
    CELERYD_OPTS = "--time-limit=300 --concurrency=1"

    CELERYBEAT_SCHEDULE = {
    'record_latest_forex_rate_every_2_hours': {
        'task': 'application.services.scheduling.forex.record_latest_forex_rate',
        'schedule': crontab(minute=0, hour="*/2"),
    },
    'kuaidi_request_every_8_hour': {
        'task': 'application.services.scheduling.express.check_kuaidi',
        'schedule': crontab(minute=0, hour="*/8"),
    },
}


class ProdConfig(BaseConfig):
    DEBUG = True
    PROD = True
    ENV = E.production

    MONGODB_SETTINGS = {
        'db': 'bibi',
        'host': 'localhost',
        'read_preference': ReadPreference.PRIMARY_PREFERRED,
        'port': 27017,
    }


class DevConfig(BaseConfig):

    DEBUG = True
    ENV = E.development

    # ===========================================
    # Flask-Assets
    #
    ASSETS_DEBUG = True

    # You should overwrite in production.py
    # Limited the maximum allowed payload to 16 megabytes.
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024


class TestConfig(DevConfig):
    TESTING = True
    ENV = E.test

    MONGODB_SETTINGS = {
        'db': 'bibi_test',
        'host': 'localhost',
        'port': 27017,
    }

    # flask cache
    CACHE_TYPE = 'null'
    CACHE_NO_NULL_WARNING = True

config_map = {
    'development': DevConfig,
    'test': TestConfig,
    'production': ProdConfig,
}


def get_config(env, app=''):
    if app == 'worker':
        env = 'production'
    return config_map[env]()

def get_config_from_host(app_name):
    # set env via hostname/environment variable
    flask_env = os.environ.get('FLASK_ENV','production')
    config = get_config(flask_env, app_name)
    return config
