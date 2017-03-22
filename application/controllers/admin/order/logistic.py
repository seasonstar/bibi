# -*- coding: utf-8 -*-
import json
import os
import datetime
import time
import random
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
from application.utils import Pagination, format_date
from configs.config import TEMPLATE_DIR


num_per_page = 50
delay_status_by_date = {
    'PAYMENT_RECEIVED':3,
    'PROCESSING': 1,
    'SHIPPING': 5,
    'PORT_ARRIVED': 4,
    }

def to_json(lo):
    dt = {}
    dt['id'] = str(lo.id)
    dt['is_closed'] = lo.is_closed
    dt['close_reason'] = lo.close_reason
    dt['created_at'] = lo.created_at
    dt['detail'] = lo.detail.to_mongo()
    dt['detail']['partner'] = (lambda p: p and p.name)(lo.detail.partner)
    dt['address'] = lo.order.address.to_json()
    dt['order_id'] = lo.order.short_id
    dt['logistic_provider'] = lo.order.logistic_provider
    dt['entries'] = [entry_to_json(entry) for entry in lo.entries]
    dt['estimated_weight'] = lo.estimated_weight
    dt['returned_entries'] = [entry_to_json(entry) for entry in lo.returned_entries]
    return dt

def entry_to_json(entry):
    dt = {}
    dt['id'] = str(entry.id)
    dt['item'] = entry.item_snapshot.to_mongo()
    dt['spec'] = entry.item_spec_snapshot.to_mongo()
    try:
        dt['item']['weight'] = entry.item_snapshot.weight
    except:
        pass
    try:
        dt['item']['title_en'] = entry.item_snapshot.title_en
    except:
        pass
    dt['amount_usd'] = entry.amount_usd
    dt['amount'] = entry.amount
    dt['quantity'] = entry.quantity
    dt['unit_price'] = entry.unit_price
    dt['created_at'] = entry.created_at
    dt['remark'] = entry.remark
    dt['shipping_info'] = entry.shipping_info
    return dt


def restruct_query(data):
    format_date = lambda d: datetime.datetime.strptime(d, '%Y-%m-%dT%H:%M:%S.%fZ')
    status = data.get('status')
    query = {}
    for k,v in data.items():
        if v in [None, u"None", "", "null"]: continue
        if k[-3:] == '_no':
            query.update({'detail__%s'%k: v})
        elif k in ['status']:
            query.update({'detail__%s'%k: v})
        elif k == 'start':
            if status:
                date_field = Models.LogisticDetail.attr_by_log_stat[status]
                query.update({'detail__%s__gte' % date_field: format_date(v)})
            else:
                query.update({'created_at__gte': format_date(v)})
        elif k == 'end':
            if status:
                date_field = Models.LogisticDetail.attr_by_log_stat[status]
                query.update({'detail__%s__lt' % date_field: format_date(v)})
            else:
                query.update({'created_at__lt': format_date(v)})
        elif k == 'query':
            if v.startswith('MB'):
                query.update({'detail__partner_tracking_no': v})
            elif ObjectId.is_valid(v):
                query.update({'id': v})
            else:
                query.update({'tracking_no': v})
        elif k == 'partner':
            partner = Models.Partner.objects(name=v).first()
            query.update({'detail__partner': partner})
        elif k == 'channel':
            query.update({'detail__channel': v})
        else:
            query.update({'%s'%k: v})

    return query



class N(AdminView):
    _permission = 'logistic'

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


    @expose("/logistics", methods=["GET"])
    def logistics(self):
        items_range = request.headers.get('Range', "0-9")
        start, end = items_range.split('-')
        per_page = int(end)-int(start)+1

        query = restruct_query(request.args)
        tracking_no = query.pop("tracking_no", "")

        include_closed = query.get('include_closed') and query.pop('include_closed')

        try:
            if include_closed:
                los = Models.Logistic.objects(**query)
            else:
                los = Models.Logistic.objects(is_closed=False, **query)
            if tracking_no:
                los = los.filter(Q(detail__us_tracking_no=tracking_no) | Q(detail__cn_tracking_no=tracking_no))

            if request.args.get('status'):
                los = los.order_by('detail__%s' %
                        Models.LogisticDetail.attr_by_log_stat[request.args.get('status')])
        except:
            pass

        if query.get('receiver'):
            addrs = Models.Address.objects(receiver=query.get('receiver')).distinct('id')
            orders = Models.Order.commodities(address__in=addrs)
            los = list(chain.from_iterable(order.logistics for order in orders))

        if query.get('order_id'):
            orders = Models.Order.commodities(short_id=int(query.get('order_id')))
            los = list(chain.from_iterable(order.logistics for order in orders))

        try:
            los_size = los.count()
        except:
            los_size = len(los)
        data = los[int(start): int(end)]
        data  = [to_json(l) for l in data]
        resp = make_response(json_util.dumps(data), 200)
        resp.headers['Accept-Range'] = 'items'
        resp.headers['Content-Range'] = '%s-%s/%s'% (start, end, los_size)
        resp.headers['Content-Type'] = 'application/json'
        return resp

    @expose("/logistics_delay/<status>/<delay_type>", methods=["GET"])
    @expose("/logistics_delay/<status>/", methods=["GET"])
    @expose("/logistics_delay/", methods=["GET"])
    def logistics_delay(self, status=None, delay_type=None):
        utcnow = datetime.datetime.utcnow()
        if status:
            items_range = request.headers.get('Range', "0-9")
            start, end = items_range.split('-')
            per_page = int(end)-int(start)+1

            query = restruct_query(request.args)
            tracking_no = query.pop("tracking_no", "")

            date_field = Models.LogisticDetail.attr_by_log_stat[status]
            delay_days = datetime.timedelta(days=delay_status_by_date[status])
            query.update({
                'detail__%s__lt' % date_field: utcnow - delay_days,
                'detail__status': status,
                })

            los = Models.Logistic.objects(is_closed=False, **query).order_by('detail__%s' %
                    date_field)

            if tracking_no:
                los = los.filter(Q(detail__us_tracking_no=tracking_no) | Q(detail__cn_tracking_no=tracking_no))

            if delay_type:
                los = los.filter(detail__delay_details__reason__contains=delay_type)
            data = los[int(start): int(end)]
            data  = [to_json(l) for l in data]
            resp = make_response(json_util.dumps(data), 200)
            resp.headers['Accept-Range'] = 'items'
            resp.headers['Content-Range'] = '%s-%s/%s'% (start, end, los.count())
            resp.headers['Content-Type'] = 'application/json'
            return resp

        data = {}
        for status in ["PAYMENT_RECEIVED", 'PROCESSING', 'SHIPPING', "PORT_ARRIVED"]:
            los = Models.Logistic.objects(is_closed=False)
            date_field = Models.LogisticDetail.attr_by_log_stat[status]
            delay_days = datetime.timedelta(days=delay_status_by_date[status])
            query = {
                'detail__%s__lt' % date_field: utcnow - delay_days,
                'detail__status': status,
                }
            count = los.filter(**query).count()
            data.update({status: count})

        return jsonify(results=data)


    @expose("/logistics_irregular/<process_status>/<irr_type>", methods=["GET"])
    @expose("/logistics_irregular/<process_status>/", methods=["GET"])
    @expose("/logistics_irregular", methods=["GET"])
    def logistics_irregular(self, process_status=None, irr_type=None):
        utcnow = datetime.datetime.utcnow()
        if process_status:
            items_range = request.headers.get('Range', "0-9")
            start, end = items_range.split('-')

            query = restruct_query(request.args)
            tracking_no = query.pop('tracking_no', '')
            los = Models.Logistic.objects(
                    detail__irregular_details__process_status=process_status,
                    **query).order_by('-detail.irregular_details.created_at')
            if irr_type:
                los = los.filter(detail__irregular_details__irr_type=irr_type).order_by('-detail.irregular_details.created_at')

            if tracking_no:
                los = los.filter(Q(detail__us_tracking_no=tracking_no) | Q(detail__cn_tracking_no=tracking_no))
            data = los[int(start): int(end)]
            data  = [to_json(l) for l in data]
            resp = make_response(json_util.dumps(data), 200)
            resp.headers['Accept-Range'] = 'items'
            resp.headers['Content-Range'] = '%s-%s/%s'% (start, end, los.count())
            resp.headers['Content-Type'] = 'application/json'
            return resp

        data = {}
        for status in ["WAITING_PROCESS", "PROCESSING", "PROCESSED"]:
            los = Models.Logistic.objects(detail__irregular_details__process_status=status)
            data.update({status: los.count()})

        return jsonify(results=data)

    @expose("/update", methods=["PUT"])
    def update(self):
        query = request.get_json()
        dt = {}
        for k,v in query.items():
            if v in [None, u"None", "", "null"]: continue
            if 'date' in k:
                val = datetime.datetime.strptime(v, '%Y-%m-%d')
            elif k.startswith('real'):
                val = float(v)
            elif k == 'partner':
                val = Models.Partner.objects(name=v).first()
            elif k == 'irregularity':
                val = Models.LogisticIrregular(irr_at_status=v.get('status'),
                                               irr_type=v.get('type'),
                                               reason=v.get('reason'),
                                               desc=v.get('desc'))
            else:
                val = v.strip()
            dt.update({k:val})

        try:
            lo = Models.Logistic.objects.get(id=dt.pop('lid'))
            lo.update_logistic(dt)

            return jsonify(message="OK",
                           remarks=lo.detail.remarks,
                           delays=lo.detail.delay_details,
                           irregularities=lo.detail.irregular_details)

        except Exception as e:
            return jsonify(message="Failed", desc=e.message)

    @expose("/update_delay", methods=["PUT"])
    def update_delay(self):
        query = request.get_json()
        try:
            lo = Models.Logistic.objects.get(id=query['lid'])
            delays = lo.detail.delay_details.filter(status=query['status'])
            delays.update(is_done=query['is_done'])
            lo.save()
            return jsonify(message="OK")
        except Exception as e:
            return jsonify(message="Failed", desc=e.message)

    @expose("/update_irr_step", methods=["PUT"])
    def update_irr_step(self):
        query = request.get_json()
        dt = {}
        for k,v in query.items():
            dt.update({k:v})

        try:
            lo = Models.Logistic.objects.get(id=dt['lid'])
            irregular = lo.detail.irregular_details.filter(irr_type=dt['irr_type']).first()
            irregular.steps = dt['solutions']
            lo.save()
            return jsonify(message="OK", irr_detail=irregular)
        except Exception as e:
            return jsonify(message="Failed", desc=e.message)

    @expose("/set_irr_done", methods=["PUT"])
    def set_irr_done(self):
        query = request.get_json()
        dt = {}
        for k,v in query.items():
            dt.update({k:v})
        try:
            lo = Models.Logistic.objects.get(id=dt['lid'])
            irregular = lo.detail.irregular_details.filter(irr_type=dt['irr_type']).first()
            irregular.process_status = dt['process_status']
            lo.save()
            return jsonify(message="OK", irr_detail=irregular)
        except Exception as e:
            return jsonify(message="Failed", desc=e.message)

    @expose("/update_irr_remark", methods=["PUT"])
    def update_irr_remark(self):
        query = request.get_json()
        dt = {}
        for k,v in query.items():
            dt.update({k:v})

        try:
            lo = Models.Logistic.objects.get(id=dt['lid'])
            irregular = lo.detail.irregular_details.filter(irr_type=dt['irr_type']).first()
            remark = Models.LogisticRemark(content=dt['irr_remark'], creator=current_user.name)
            irregular.remarks.append(remark)
            lo.save()
            return jsonify(message="OK", irr_detail=irregular)
        except Exception as e:
            return jsonify(message="Failed", desc=e.message)

    @expose("/merge", methods=["POST"])
    def merge(self):
        lids = request.json.get('lids')
        if not lids:
            return jsonify(message="Failed", desc="error~~~")

        los = [Models.Logistic.objects(id=lid).first() for lid in lids]
        if not type(los) is list:
            return jsonify(message="Failed", desc="please select more than 2 logistics")

        start = 0
        for index in range(len(los)-1):
            if los[index+1].detail.cn_tracking_no != \
                    los[start].detail.cn_tracking_no or \
                    los[index+1].order != los[0].order:
                return jsonify(message="Failed", desc="CTN and OrderID should be the same")

        for index in range(len(los)-1):
            map(
                lambda e: los[index+1].entries.append(e),
                los[index].entries
            )
            los[index].entries = []
            los[index].save()
            los[index].close(
                'merged with %s' %
                los[index+1].id, datetime.datetime.utcnow()
            )
            los[index+1].save()

            if index+1 == len(los)-1:
                comment = Models.LogisticRemark(
                    content=u"合并单", creator=current_user.name
                )
                los[index+1].detail.remarks.append(comment)
                los[index+1].save()

        return jsonify(message="OK", lid=str(los[index+1].id))


    @expose("/split_entries", methods=["POST"])
    def split_entries(self):
        entries = request.json.get('selected')
        if not entries:
            return jsonify(message="Failed", desc="Please select entries!")

        lids = []
        entry_ids = []
        for l in entries:
            c = l.split(':')
            lids.append(c[1])
            entry_ids.append(c[0])

        los = [Models.Logistic.objects(id=lid).first() for lid in set(lids)]

        e_lst = []
        for i in entry_ids:
            e = Models.OrderEntry.objects(id=str(i)).first()
            e_lst.append(e)

        entries_groups = map(lambda lo: filter(lambda e: e in lo.entries, e_lst),
                los)

        for lo, lst in zip(los, entries_groups):
            lo.fork_by_entries([e.id for e in lst])

        return jsonify(message="OK", oid=lo.order.short_id)


    @expose('/split_quantity', methods=['POST'])
    def split_quantity(self):
        lid = request.json.get('lid')
        eid = request.json.get('eid')
        quantity = request.json.get('quantity')
        lo = Models.Logistic.objects(id=lid).first()
        entry = Models.OrderEntry.objects(id=eid).first()
        if entry.quantity > 1 and entry.quantity - int(quantity) >=1 and entry and lo:
            entry.quantity -= int(quantity)
            entry.update_snapshot()
            entry.update_amount()

            new_entry = deepcopy(entry)
            new_entry.__class__ = Models.OrderEntry
            new_entry.id = None
            new_entry.quantity = int(quantity)
            new_entry.update_snapshot()
            new_entry.update_amount()
            new_entry.save()
            lo.entries.append(new_entry)
            lo.save()
            order = lo.order
            order.entries.append(new_entry)
            order.save()
        else:
            return jsonify(message="Failed", desc="quantity error~~~~~~")
        return jsonify(message="OK", entries=[json.loads(json_util.dumps(entry_to_json(entry))) for entry in lo.entries])


    @expose('/download', methods=["GET"])
    def download(self):
        FIELDS = [u"包裹ID", u'IMG No', u'CTN', u"下单日期", u"订单ID",u'订单短号', u'收件人', u'手机号', u'合作物流商', u'remark',u"下单备注", u"估重", u"渠道"]

        now = datetime.datetime.now()

        status = request.args.get('status')
        query = restruct_query(request.args)
        delay_export = query.get('delay_export') and query.pop('delay_export')
        delay_type = query.get('delay_type') and query.pop('delay_type')
        try:
            los = Models.Logistic.objects(is_closed=False, **query)
            if status:
                los = los.order_by('detail__%s' %
                        Models.LogisticDetail.attr_by_log_stat[status])
        except:
            pass

        if delay_export:

            date_field = Models.LogisticDetail.attr_by_log_stat[status]
            delay_days = datetime.timedelta(days=delay_status_by_date[status])
            query = {
                'detail__%s__lt' % date_field: datetime.datetime.utcnow() - delay_days,
                'detail__status': status,
                }
            los = los.filter(**query).order_by('detail__%s' %
                    date_field)
            if delay_type:
                los = los.filter(detail__delay_details__reason__contains=delay_type)

        if query.get('receiver'):
            addrs = Models.Address.objects(receiver=query.get('receiver')).distinct('id')
            orders = Models.Order.commodities(address__in=addrs)
            los = list(chain.from_iterable(order.logistics for order in orders))

        if query.get('order_id'):
            orders = Models.Order.commodities(short_id=int(query.get('order_id')))
            los = list(chain.from_iterable(order.logistics for order in orders))

        def generate():
            yield ','.join(st for st in FIELDS) + '\n'
            for log in los:
                yield ','.join([
                   str(log.id),
                   log.detail.partner_tracking_no,
                   log.detail.carrier_tracking_no,
                   log.detail.cn_tracking_no,
                   log.detail.cn_logistic_name,
                   format_date(log.detail.payment_received_date),
                   str(log.order.id),
                   str(log.order.short_id),
                   log.order.address.receiver,
                   log.order.address.mobile_number,
                   format_date(log.detail.processing_date),
                   format_date(log.detail.shipping_date),
                   format_date(log.detail.port_arrived_date),
                   format_date(log.detail.received_date),
                   format_date(log.detail.modified),
                   log.detail.partner.name if log.detail.partner else '',
                   '; '.join([r.content for r in log.detail.remarks]),
                   log.detail.extra or '',
                   str(log.estimated_weight),
                   log.detail.channel,

                ]) + '\n'

        return Response(generate(),
                        mimetype="text/csv",
                        headers={
                            "Content-Disposition":
                            "attachment;filename=%s %s.csv" % (format_date(now,'%Y-%m-%d'),'dumps_file')
                        }
                )

    @expose('/partner', methods=["GET"])
    def partner(self):
        partners = Models.Partner.objects().distinct('name')
        return jsonify(results=partners, message="OK")

    @expose('/close/<lid>', methods=['GET'])
    def close(self, lid):
        lo = Models.Logistic.objects(id=lid).first()
        lo.close("Closed By %s" % current_user.name)
        return jsonify(message="OK")

    @expose('/logs/<ltype>/<lid>', methods=['GET'])
    def logs(self, ltype, lid):
        if ltype == 'express':
            logs = Models.Logistic.objects(id=lid).first().express_tracking
            return self.render('admin/logistic/express.html', logs=logs)
        elif ltype == 'logistic':
            logs = Models.LogisticLog.objects(logistic_id=lid, log_type__ne='API')
            user = lambda i: getattr(Models.User.objects(id=i).first(), 'name', '') if i and i != 'system' else i
            return self.render('admin/logistic/logs.html', logs=logs, user=user)
        elif ltype == 'print':
            lo = Models.Logistic.objects(id=lid).first()
            if lo.is_closed:
                return Response('this logistics id has been closed.')
            return self.render('admin/logistic/print_page.html', lo=lo)

    @expose('/refresh/<company>/<number>', methods=['GET'])
    def refresh(self, company, number):
        Jobs.express.kuaidi_request(company, number)
        return jsonify(message="OK")

    @expose('/back_status', methods=['GET'])
    def back_status(self):
        lid = request.args.get('lid')
        status = request.args.get('status')

        l = Models.Logistic.objects(id=lid).first()

        l.detail.status = status
        setattr(l.detail, Models.LogisticDetail.attr_by_log_stat[status],
                datetime.datetime.utcnow())
        l.save()
        order = l.order
        order.update_logistic_status()

        return jsonify(message="OK")



admin.add_view(N(name=_('Logistics Backend'), category='Logistics', menu_icon_type="fa", menu_icon_value="truck"))
