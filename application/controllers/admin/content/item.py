# -*- coding: utf-8 -*-
import json
import os
import datetime
import time
import random
from urllib import parse
from math import ceil
from collections import defaultdict
from uuid import uuid4
from copy import deepcopy
from bson import ObjectId, json_util
from itertools import chain
from flask_admin import BaseView, expose
from flask_babel import gettext as _
from flask_login import current_user
from mongoengine.queryset import Q
from flask import request, current_app, redirect, jsonify, Response, \
        Markup, flash, url_for, make_response
import application.models as Models
from application.controllers.admin import AdminView
from application.extensions import admin
import application.services.jobs as Jobs
from application.services.cache import cached
from application.services.bingtrans import MSTranslate
from application.utils import Pagination, format_date
from configs.config import TEMPLATE_DIR
from configs.ueditor import UEDITOR_CONFIG
from configs.price import COST_PRICE, CURR_PRICE, ORIG_PRICE


num_per_page = 50

def restruct_query(data):
    status = data.get('status')
    query = {}
    for k,v in data.items():
        if v in [None, u"None", "", "null"]: continue
        if k == 'query':
            query.update({'item_id': v})
        elif k == 'cate':
            query.update({'sub_category': v})
        elif k == 'availability':
            query.update({k: v=='true' and True or False})
        else:
            query.update({'%s'%k: v})
    return query

def to_json(item):
    return dict(
            meta=item.to_mongo(),
            specs=[spec.to_mongo() for spec in item.specs]
        )

class I(AdminView):
    _permission = 'content'

    @expose('/', methods = ['GET', 'POST', 'DELETE', 'PATCH'])
    def index(self, status="ALL"):
        def render_tpml(status):
            return make_response(open(os.path.join(
                TEMPLATE_DIR, 'admin/logistic/index.html')).read())

        def render_json(lid):
            return jsonify(message="OK")

        return request.is_xhr and {
            'GET': lambda f: render_json(f.get('id')),
        }[request.method](request.form) or render_tpml(status)

    @expose("/items", methods=["GET"])
    def items(self):
        items_range = request.headers.get('Range', '0-24')
        start, end = items_range.split('-')

        query = restruct_query(request.args)
        try:
            items = Models.Item.objects(**query).order_by('-created_at')
        except:
            pass

        try:
            items_size = items.count()
        except:
            items_size = len(items)
        data = items[int(start): int(end)]
        data  = [to_json(i) for i in data]
        resp = make_response(json_util.dumps(data), 200)
        resp.headers['Range-Unit'] = 'items'
        resp.headers['Content-Range'] = '%s-%s/%s'% (start, end, items_size)
        resp.headers['Content-Type'] = 'application/json'
        return resp

    @expose("/update", methods=["PUT"])
    def update(self):
        query = request.get_json()
        dt = {}
        for k,v in query['meta'].items():
            if v in [None, u"None", "", "null"]: continue
            if type(v) == dict: continue
            elif 'price' in k:
                val = float(v)
            elif k == 'weight':
                val = float(v)
            elif k == 'primary_img':
                path = '{}/{}.jpeg'.format('other', uuid4())
                val = Jobs.image.upload('maybi-img', path, url=v, make_thumbnails=True)
            else:
                val = v
            dt.update({k:val})
        dt.update({
            'discount': ceil(((dt['original_price']-dt['price'])/dt['original_price']) * 100)
            })
        dt.update({'meta': dt})
        try:
            item = Models.Item.objects(web_id=dt['web_id']).first()
            item.modify(dt, dt['price'])

            return jsonify(message="OK")

        except Exception as e:
            return jsonify(message="Failed", desc=e.message)

    @expose('/categories', methods=["GET"])
    @cached(timeout=120)
    def categories(self):
        category_dict = defaultdict(set)
        for stats in Models.Statistics.objects:
            category_dict[stats.main_category].add(stats.sub_category)

        category_list = []
        for main_category in category_dict.keys():
            main = Models.Category.objects(level=1, en=main_category).first()
            sub_list = []
            for sub_category in category_dict[main_category]:
                sub = Models.Category.objects(level=2, en=sub_category).first()
                if main and sub:
                    sub_list.append(dict(en=sub.en,cn=sub.cn))
            category_list.append(
                    dict(en=main.en,
                        cn=main.cn,
                        sub_list=sub_list,
                    )
                )
        return jsonify(dict(message='OK', categories=category_list))


    @expose("/update_spec", methods=["PUT"])
    def update_spec(self):
        query = request.get_json()
        dt = {}
        for k,v in query.items():
            if v in [None, u"None", "", "null"]: continue
            if k != 'attributes' and type(v) == dict: continue
            elif 'price' in k:
                val = float(v)
            elif k == 'images':
                val = []
                if type(v) == unicode:
                    v = v.split(",")
                for img in v:
                    if img.startswith('http://assets.maybi'):
                        val.append(img)
                    else:
                        path = '{}/{}.jpeg'.format(query.get('brand', 'other'), uuid4())
                        url = Jobs.image.upload('maybi-img', path, url=img, make_thumbnails=True)
                        val.append(url)
            else:
                val = v
            dt.update({k:val})
        try:
            spec = Models.ItemSpec.objects(sku=dt['_id']).first()
            spec.update_spec(dt)
            return jsonify(message="OK", spec=spec)
        except Exception as e:
            return jsonify(message="Failed", desc=e.message)

    @expose("/add_spec", methods=["POST"])
    def add_spec(self):
        query = request.get_json()
        dt = {}
        for k,v in query.items():
            if v in [None, u"None", "", "null"]: continue
            elif 'price' in k:
                val = float(v)
            elif k == 'images':
                images = v.split(",")
                val = []
                for img in images:
                    if img.startswith('http://assets.maybi'):
                        val.append(img)
                    else:
                        path = '{}/{}.jpeg'.format(query.get('brand', 'other'), uuid4())
                        url = Jobs.image.upload('maybi-img', path, url=img, make_thumbnails=True)
                        val.append(url)
            else:
                val = v
            dt.update({k:val})

        dt.update({'web_sku': str(time.time()).replace(".", "")})
        try:
            spec = Models.ItemSpec(**dt).save()
            return jsonify(message="OK", spec=spec)
        except Exception as e:
            return jsonify(message="Failed", desc=e.message)


    @expose("/delete_spec", methods=["DELETE"])
    def delete_spec(self):
        query = request.get_json()
        sku = query.get('sku')
        if "ADMIN" not in current_user.roles:
            return jsonify(message="Failed", desc="sorry, u dont have permission to do this")
        try:
            Models.ItemSpec.objects(sku=sku).delete()
            return jsonify(message="OK")
        except Exception as e:
            return jsonify(message="Failed", desc=e.message)


    @expose("/add_item", methods=["POST"])
    def add_item(self):
        query = request.get_json()
        dt = {}
        for k,v in query.items():
            if v in [None, u"None", "", "null"]: continue
            elif 'price' in k:
                val = float(v)
            elif k == 'primary_img':
                path = '{}/{}.jpeg'.format('other', uuid4())
                val = Jobs.image.upload('maybi-img', path, url=v, make_thumbnails=True)
            else:
                val = v
            dt.update({k:val})
        try:
            china_price = dt['china_price']+dt.pop('express_price')
            cost_price = COST_PRICE(china_price, dt['weight'])
            price = CURR_PRICE(cost_price)
            orig_price = ORIG_PRICE(price)
            vendor='taobao'
            brand = 'other'
            main_category = 'home'
            sub_category = 'unclassified'
            ps = parse.urlparse(dt['url'])
            web_id = parse.parse_qs(ps.query)['id'][0]
            translator = MSTranslate("maybi","UwX8zu/WCCOsrnEbbI36hGI3JNkQ7LwESYDm8e05xIk=")
            title_en = translator.translate(dt['title'], 'en', 'zh')

            dt.update({
                'web_id': web_id,
                'title_en': title_en,
                'china_price': china_price,
                'original_price':orig_price,
                'price': price,
                'main_category': main_category,
                'sub_category':sub_category,
                'creator': current_user.name,
                'vendor':vendor,
                'brand':brand,
                'availability':False,
                'currency': 'USD',
                'sex_tag': 'UNCLASSIFIED',
                'tags': [],
                'discount': ceil(((orig_price - price) / orig_price) * 100),
            })
            attr_dt = {}
            for attr in dt['attributes']:
                attr_dt.update({attr:None})
            spec_dt = {
                'web_sku': str(time.time()).replace(".", ""),
                'images': [dt['primary_img']],
                'china_price': china_price,
                'original_price': orig_price,
                'price':price,
                'attributes': attr_dt ,
            }

            data = {'meta':dt, 'specs': [spec_dt]}
            item = Models.Item.create(data)
            return jsonify(message="OK", item=item)
        except Exception as e:
            return jsonify(message="Failed", desc=e.message)


    @expose('/upload', methods=['GET', 'POST', 'OPTIONS'])
    def upload_img(self):
        """UEditor文件上传接口
        config 配置文件
        result 返回结果
        """
        result = {}
        action = request.args.get('action')

        # 解析JSON格式的配置文件
        CONFIG = UEDITOR_CONFIG

        if action == 'config':
            # 初始化时，返回配置文件给客户端
            result = CONFIG

        elif action  == 'uploadimage':
            img = request.files.get('upfile')

            name, ext = img.filename.rsplit('.', 1)
            filename = uuid4()
            path = '{}/{}.{}'.format('details', filename, ext)
            url = Jobs.image.upload('maybi-img', path, image=img.read(), make_thumbnails=False)

            result = {"state": "SUCCESS",
                    "url": url,
                    "title": filename,
                    "original": filename,
                    "type": ext,
                    "size": ""}

        elif action == 'catchimage':
            fieldName = CONFIG['catcherFieldName']
            if fieldName in request.form:
                # 这里比较奇怪，远程抓图提交的表单名称不是这个
                source = []
            elif '%s[]' % fieldName in request.form:
                # 而是这个
                source = request.form.getlist('%s[]' % fieldName)

            _list = []
            for imgurl in source:
                filename = uuid4()
                path = '{}/{}.jpeg'.format('details', filename)
                url = Jobs.image.upload('maybi-img', path, url=imgurl, make_thumbnails=False)
                _list.append({
                    'state': "SUCCESS",
                    'url': url,
                    'original': filename,
                    'source': imgurl,
                })

            result['state'] = 'SUCCESS' if len(_list) > 0 else 'ERROR'
            result['list'] = _list
        else:
            result['state'] = u'请求地址出错'

        return jsonify(result)


admin.add_view(I(name=_('Item Backend'), category=_('Content'), menu_icon_type="fa", menu_icon_value="gift"))
