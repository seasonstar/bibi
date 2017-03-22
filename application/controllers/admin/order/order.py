# -*- coding: utf-8 -*-
import time
import datetime
from itertools import chain, groupby
from flask_admin import expose
from flask_login import current_user
from flask_babel import gettext as _
from application.extensions import admin
import application.models as Models
from flask import redirect, url_for, request, jsonify
from application.controllers.admin import AdminView
from application.utils import redirect_url, groupby, Pagination


class OrderView(AdminView):
    _permission = 'order'

    @expose('/<tab>/')
    @expose('/')
    def index(self, tab='all'):
        page = request.args.get('page',1)
        if tab == 'all':
            orders = Models.Order.commodities(is_paid=True,
                status__nin=['ABNORMAL', 'CANCELLED', 'REFUNDED'], is_test=False)
        elif tab == 'test':
            orders = Models.Order.commodities(is_paid=True,
                status__nin=['ABNORMAL', 'CANCELLED', 'REFUNDED'], is_test=True)
        elif tab == 'transfer':
            orders = Models.Order.transfer()
        elif tab == 'unpaid':
            orders = Models.Order.commodities(is_paid=False)
        elif tab == 'irregularity':
            orders = Models.Order.commodities(
                status__in=['ABNORMAL', 'CANCELLED', 'REFUNDED'])
        elif tab == 'payment_abnormal':
            orders = Models.Order.objects(is_payment_abnormal=True)
        else:
            orders = Models.Order.commodities(is_paid=True)

        orders = orders.order_by('-paid_date', '-created_at')
        data = Pagination(orders, int(page), 10)

        return self.render('admin/order/orders.html',
                           tab=tab,
                           page=page,
                           orders=data,
                           section='orders')


    @expose('/search/<page>')
    @expose('/search')
    def search(self, page=1):
        name = request.args.get(u'name')
        if name.isdigit():
            orders = Models.Order.objects(short_id=int(name))
        else:
            addrs = Models.Address.objects(receiver=name).distinct('id')
            orders = Models.Order.commodities(address__in=addrs)
        if len(name) > 15:
            orders = Models.Order.objects(id=name)

        data = Pagination(orders, int(page), 10)

        return self.render('admin/order/orders.html',
                           name=name,
                           orders=data,
                           page=page,
                           section='search')

    @expose('/<order_id>/cancel')
    def cancel_order(self, order_id):
        order = Models.Order.objects(id=order_id).first_or_404()
        reason = request.args.get(u'reason')
        order.cancel_order(reason=reason or 'cancelled from content page')
        return redirect(url_for('.index'))

    @expose('/mall_info', methods=['GET', 'POST'])
    def edit_mall_info(self):
        if not request.is_xhr: return jsonify({'message': 'FAILED'})# only for AJAX

        if request.method == 'GET':
            logistic_id = request.args.get('id')
            logistic = Models.Logistic.objects(id=logistic_id).first()
            return jsonify({'remark': logistic.detail.extra,
                            'id': str(logistic.id)
                            })

        if request.method == 'POST':
            logistic_id = request.form.get('lid')
            logistic = Models.Logistic.objects(id=str(logistic_id)).first()
            logistic.detail.extra = request.form.get('remark')
            return jsonify({'remark': logistic.detail.extra,
                            'message': "OK"})


admin.add_view(OrderView(name=_('Order'), category=_('Order'), menu_icon_type="fa", menu_icon_value="bar-chart-o"))
