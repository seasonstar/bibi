# -*- coding: utf-8 -*-
"""
    Utils has nothing to do with models and views.
"""

import json
import math
from bson import json_util
import string
import uuid
import base64
import time
import random
import datetime
import os
import subprocess
import sys
from functools import partial

import pytz
from flask import session, request, url_for, current_app, g

from flask_mail import Message
from flask_babel import gettext as _
from application.extensions import mail

from application.extensions import db


ALLOWED_IMAGE_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

# Form validation

USERNAME_LEN_MIN = 4
USERNAME_LEN_MAX = 25

REALNAME_LEN_MIN = 4
REALNAME_LEN_MAX = 25

PASSWORD_LEN_MIN = 6
PASSWORD_LEN_MAX = 16

AGE_MIN = 1
AGE_MAX = 300

DEPOSIT_MIN = 0.00
DEPOSIT_MAX = 9999999999.99

# typical values for text_subtype are plain, html, xml
text_subtype = 'plain'


def send_mail(recipients, title, message, sender='seasonstar@126.com'):
    with mail.app.app_context():
        msg = Message(title, recipients=recipients)
        if sender:
            msg.sender = sender
        msg.html = message
        mail.send(msg)


def redirect_url():
    return request.args.get('next') or \
            request.referrer or \
            url_for('.index')


def get_session_key():
    return session.sid
    # check if client side has passed in key
    key = request.args.get('session_key')
    if key:
        return key
    key = session.setdefault('session_key', str(uuid.uuid4()))
    return key


def get_current_time():
    return datetime.datetime.utcnow()


def timesince(dt, default=None, reverse=False):
    """
    Returns string representing "time since" e.g.
    3 days ago, 5 hours ago etc.
    Ref: https://bitbucket.org/danjac/newsmeme/src/a281babb9ca3/newsmeme/
    """

    if not dt:
        return ''

    if default is None:
        default = u'刚刚'
    now = datetime.datetime.utcnow()
    diff = (dt - now) if reverse else now - dt

    if diff < datetime.timedelta(days=0):
        return default

    periods = (
        (diff.days / 365, u'年', u'年'),
        (diff.days / 30, u'月', u'月'),
        (diff.days / 7, u'周', u'周'),
        (diff.days, u'天', u'天'),
        (diff.seconds / 3600, u'小时', u'小时'),
        (diff.seconds / 60, u'分钟', u'分钟'),
        (diff.seconds, u'秒', u'秒'),
    )

    for period, singular, plural in periods:

        if not period:
            continue

        if reverse:
            if period == 1:
                return u'剩余 %d %s' % (period, singular)
            else:
                return u'剩余 %d %s' % (period, plural)

        else:
            if period == 1:
                return u'%d%s前' % (period, singular)
            else:
                return u'%d%s前' % (period, plural)

    return default


def timeuntil(dt, default=None):
    return timesince(dt, default, reverse=True)


def size_normal(url):
    if 'upaiyun' in url:
        return url + '!normal'
    return url


def get_class( kls ):
    """
    Returns class object specified by a string.
    Args:
        kls: The string representing a class.
    """
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def id_generator(size=10, chars=string.ascii_letters + string.digits):
    #return base64.urlsafe_b64encode(os.urandom(size))
    return ''.join(random.choice(chars) for x in range(size))


def to_json(obj):
    return json.dumps(obj.to_mongo(), default=json_util.default, separators=(',', ':'))


def paginate(objects, page, item_per_page=20, offset=0):
    start = page * item_per_page + offset
    end = start + item_per_page

    if start < 0:
        start = 0
    if end < 0:
        end = 0
    return objects[start:end]


def dup_aware_paging(qs, page, num_per_page, leading_id=None):
    res = paginate(qs, page, num_per_page)
    if leading_id:
        offset = 0
        for i, it in enumerate(res):
            if str(it.id) == leading_id:
                offset = i + 1
                break
        if offset:
            res = paginate(qs, page, num_per_page, offset=offset)
    _res = []
    for i, it in enumerate(res):
        if i >= num_per_page:
            break
        _res.append(it)
    return _res


def paginate_field(query_set, field, page, item_per_page=20):
    start = page * item_per_page
    end = start + item_per_page
    query_set = query_set.fields(**{'slice__'+field: [start, end]})

    return getattr(query_set.first(), field)


def handler(event):
    """Signal decorator to allow use of callback functions as class decorators."""

    def decorator(fn):
        def apply(cls):
            event.connect(fn, sender=cls)
            return cls

        fn.apply = apply
        return fn

    return decorator


@handler(db.pre_save)
def update_modified(sender, document):
    document.modified = datetime.datetime.utcnow()


class Command(object):

    def __init__(self, *args):
        self.lines = ['set -e']
        self.lines.extend(args)

    def get_cmd(self):
        return ";\n".join(self.lines)

    def next(self, *args):
        self.lines.extend(args)
        return self

    def run(self, output_to_pile=False):
        out_source = None
        if output_to_pile:
            out_source = subprocess.PIPE

        print ('\nExecuting: \n%s\n' % self.get_cmd())
        proc = subprocess.Popen(self.get_cmd(), stdout=out_source, shell=True,
                                executable='/bin/bash', env=os.environ.copy())
        out, error = proc.communicate()

        # exit if the proc has error
        if proc.returncode:
            sys.exit(1)


def run_cmd(cmd):
    Command(cmd).run()


LOCAL_TZ = pytz.timezone("Asia/Shanghai")


def to_utc(dt):
    local_dt = LOCAL_TZ.localize(dt, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    return utc_dt


def to_local(dt):
    with_tz = pytz.UTC.localize(dt)
    local_dt = with_tz.astimezone(LOCAL_TZ)
    return local_dt


def format_date(value, format='%Y-%m-%d %H:%M'):
    if value is None:
        return ''
    with_tz = pytz.UTC.localize(value)
    local_dt = with_tz.astimezone(LOCAL_TZ)
    return local_dt.strftime(format)


def isodate_to_local(datestr):
    datestr = datestr.split('+')[0]
    dt = datetime.datetime.strptime(datestr.split('.')[0], '%Y-%m-%dT%H:%M:%S')
    return format_date(dt)


class AttrDict(dict):
    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError("%r object has no attribute %r" %
                                 (self.__class__, attr))

    def __setattr__(self, attr, value):
        self[attr] = value

    def to_dict(self):
        return self


# def format_date(v):
#     return type(v) in [str, unicode] and datetime.datetime.strptime(v, '%Y-%m-%d') or v

def ignore_error(fn):
    def handle(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except:
            pass
    return handle

def groupby(l,fn):
    import itertools
    return itertools.groupby(sorted(l, key=fn), fn)

def fuck_ie(fn):
    def handle(*args, **kwargs):
        if 'MSIE' in request.user_agent.string:
            return redirect('http://www.google.cn/intl/zh-CN/chrome/browser/')
        return fn(*args, **kwargs)
    return handle

def cprint(obj ,color = None, background = False, ):

    import random, sys
    if background:
        base = 40
    else:
        base = 30
    if color is None:
        color = int(random.random()*7+base)

    str = '\x1b[%sm%s\x1b[0m\n'%(color, obj)
    sys.stdout.write(str)


def validate_id_card_no(number):
    date_str = number[6:14]
    try:
        birth = datetime.datetime.strptime(date_str, '%Y%m%d')
    except ValueError:
        return False
    if not datetime.datetime(1900, 1, 1) < birth < datetime.datetime.now():
        return False
    try:
        num_list = map(lambda x: 10 if x in 'xX' else int(x), number)
    except (ValueError, TypeError):
        return False
    weights = map(lambda x: 2**x[0] % 11 * x[1],
                  zip(range(17, -1, -1), num_list))
    return sum(weights) % 11 == 1


round1 = partial(round, ndigits=1)
round2 = partial(round, ndigits=2)


def round_to_string(v):
    return '{:.2f}'.format(round2(v))



def ceil(v):
    return int(math.ceil(v))


class Pagination(object):

    def __init__(self, objects, page, per_page):
        self.page = page
        self.per_page = per_page
        self.objects = objects
        try:
            self.total_count = objects.count()
        except TypeError:
            self.total_count = len(objects)

    @property
    def slice(self):
        start = (self.page - 1) * self.per_page
        end = start + self.per_page
        if start < 0:
            start = 0
        if end < 0:
            end = 0
        return self.objects[start:end]

    @property
    def pages(self):
        return ceil(self.total_count / float(self.per_page))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and \
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num

def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)


BAN_REGEX = None
def banwords_check(content):
    import re
    global BAN_REGEX

    banwords_file = os.path.join(
        current_app.root_path, 'etc', 'banwords.txt')

    if not BAN_REGEX:
        try:
            words = open(banwords_file).read().decode('utf8')
        except:
            return content
        BAN_REGEX = re.compile('(%s)' % words)

    return BAN_REGEX.search(content)


def checked_g_get(key, default_value):
    limit = {
        'num_per_page': 20,
    }
    ret = g.get(key, default_value)
    if limit.get(key, None) and ret > limit['num_per_page']\
        and ret > default_value:
        return default_value
    return ret
