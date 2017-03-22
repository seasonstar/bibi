# -*- coding: utf-8 -*-
import datetime
import json
from io import StringIO

from flask import Blueprint, jsonify, request, redirect, url_for, make_response, render_template
from flask_login import login_required, current_user
from flask_babel import gettext as _
import application.services.jobs as Jobs
from application.services.payment.paypal import paypal_checkout, paypal_update_payment, \
    paypal_sdk_update_payment
from application.services.payment.wechat import JSWXPay, APPWXPay
from application.services.payment.config import WECHAT_CONFIG, MP_WECHAT_CONFIG
import application.models as Models
from configs.enum import PAYMENT_TYPE, PAYMENT_TRADERS, ORDER_TYPE

payment = Blueprint('payment', __name__, url_prefix='/payment')


js_wxpay = JSWXPay(**MP_WECHAT_CONFIG)
app_wxpay = APPWXPay(**WECHAT_CONFIG)


@payment.route('/paypal/success', methods=['GET'])
def paypal_success():
    '''
    Asynchronised POST of result from paypal
    '''
    payer_id = request.args.get('PayerID')
    payment_id= request.args.get('paymentId')

    pending_payment = Models.Payment.objects(ref_number=payment_id).first()
    if paypal_update_payment(pending_payment, payer_id):
        order = pending_payment.order
        #return redirect('http://127.0.0.1:8888/#/payment/success?order_type=%s&order_id=%s' %
        return redirect('http://m.maybi.cn/#/payment/success?order_type=%s&order_id=%s' %
                (order.order_type, str(order.id)))
    else:
        return redirect('http://m.maybi.cn/#/payment/cancel')


@payment.route('/paypal/cancel', methods=['GET'])
def paypal_cancel():
    return redirect('http://m.maybi.cn/#/payment/cancel')


@payment.route('/paypal/notify', methods=['POST'])
def paypal_sdk_notify():
    data = request.json
    order = Models.Order.objects(id=data['order_id']).first_or_404()
    payment_res = data['payment']

    ptype = PAYMENT_TYPE.WITHOUT_TAX
    payment_obj = order.create_payment(ptype, PAYMENT_TRADERS.PAYPAL)
    payment_obj.ref_number = payment_res['response']['id']
    payment_obj.save()
    if paypal_sdk_update_payment(payment_obj):
        return jsonify(message="OK")
    else:
        return jsonify(message="Failed")



@payment.route('/checkout', methods=['POST'])
@payment.route('/checkout/<order_id>', methods=['POST'])
@login_required
def checkout(order_id=None):
    data = request.json
    order = Models.Order.objects(id=order_id).first_or_404()

    ptype = PAYMENT_TYPE.WITHOUT_TAX
    payment_method = data.get('payment_method', 'paypal')
    if payment_method == 'paypal':

        payment, obj = paypal_checkout(order, ptype)
        # Create Payment and return status

        if not obj.redirect_url:
            return jsonify(message='Failed', error=_('order expired'))
        return jsonify(message='OK', url=obj.redirect_url, payment_method=payment_method,
                       order_id=str(order.id))

    elif payment_method == 'wechat':

        url = wechat_checkout_url(order, ptype)
        return jsonify(message='OK', url=url, payment_method=payment_method,
                       order_id=str(order.id))

    return jsonify(message='Failed', error=_('invalid payment method'))

@payment.route('/checkout/sdk', methods=['POST'])
@payment.route('/checkout/sdk/<order_id>', methods=['POST'])
@login_required
def sdk_checkout(order_id=None):
    data = request.json
    order = Models.Order.objects(id=order_id).first_or_404()

    ptype = PAYMENT_TYPE.WITHOUT_TAX
    payment_method = data.get('payment_method', 'paypal')
    if payment_method == 'paypal':

        #payment, obj = paypal_sdk_checkout(order, ptype)
        # Create Payment and return status
        subject = u'Maybi Order %s' % str(order.short_id)
        data = {"subject": subject,
                "final": "%.2f" % order.final
            }
        return jsonify(message='OK', order=data, payment_method=payment_method,
                       order_id=str(order.id))

    elif payment_method == 'wechat':

        data = wechat_sdk_checkout(order, ptype)
        return jsonify(message='OK', data=data, payment_method=payment_method,
                       order_id=str(order.id))

    return jsonify(message='Failed', error=_('invalid payment method'))

def wechat_sdk_checkout(order, ptype):
    payment_obj = order.create_payment(ptype, PAYMENT_TRADERS.WEIXIN)

    product = {
        'attach': str(order.short_id),
        'body': u'美比订单%s'%order.short_id,
        'out_trade_no': str(payment_obj.id),
        'total_fee': float("%.2f" % (order.final * order.forex)),
    }
    ret_dict = app_wxpay.generate_req(product)
    return ret_dict

def wechat_checkout_url(order, ptype):
    info_dict = {
        'redirect_uri': url_for('payment.wechat_jspay', _external=True),
        'state': '%s:%s' % (ptype, str(order.id)),
    }
    url = js_wxpay.generate_redirect_url(info_dict)
    return url

def wechat_checkout(ptype, order_id, code):
    order = Models.Order.objects(id=order_id).first()
    payment_obj = order.create_payment(ptype, PAYMENT_TRADERS.WEIXIN)

    openid = js_wxpay.generate_openid(code)
    product = {
        'attach': str(order.short_id),
        'body': u'美比订单%s'%order.short_id,
        'out_trade_no': str(payment_obj.id),
        'total_fee': float("%.2f" % (order.final * order.forex)),
    }
    ret_dict = js_wxpay.generate_jsapi(product, openid)
    return ret_dict

def wechat_update_payment(ret_dict):
    if ret_dict['result_code'] == 'SUCCESS':
        pending_payment = Models.Payment.objects(id=ret_dict['out_trade_no']).first()
        pay_dt = datetime.datetime.utcnow(),
        data = dict(
            paid_amount = float(ret_dict['cash_fee'])/100,
            currency = "CNY",
            buyer_id =  ret_dict['openid'],
            trade_status = ret_dict['result_code'],
            ref_number = ret_dict['transaction_id'],
            modified = pay_dt,
        )
        pending_payment.mark_paid(data)


@payment.route('/wechat/jspay', methods=["GET"])
def wechat_jspay():
    code = request.args.get('code')
    state = request.args.get('state')
    ptype, order_id = state.split(":")

    ret_dict = wechat_checkout(ptype, order_id, code)

    ret_str = '''
    <html>
    <head></head>
    <body>
    <script type="text/javascript">
    function callpay()
    {
        if (typeof WeixinJSBridge == "undefined"){
            if( document.addEventListener ){
                document.addEventListener('WeixinJSBridgeReady', jsApiCall, false);
            }else if (document.attachEvent){
                document.attachEvent('WeixinJSBridgeReady', jsApiCall);
                document.attachEvent('onWeixinJSBridgeReady', jsApiCall);
            }
        }else{
            jsApiCall();
        }
    }
    function jsApiCall(){
        //alert("正在进入");
        WeixinJSBridge.invoke(
            'getBrandWCPayRequest',
            %s,
            function(res){
                //alert(JSON.stringify(res));
                window.location.href="http://m.maybi.cn/#/orders";
            }
        );
    }
    callpay();
    </script>
    </body>
    </html>
    ''' % json.dumps(ret_dict)
    return make_response(ret_str, 200)

@payment.route('/wechat/notify', methods=['GET', 'POST'])
def wechat_notify():
    xml_str = request.data
    ret, ret_dict = js_wxpay.verify_notify(xml_str)
    # 在这里添加订单更新逻辑
    wechat_update_payment(ret_dict)

    if ret:
        ret_dict = {
            'return_code': 'SUCCESS',
            'return_msg': 'OK',
        }
    else:
        ret_dict = {
            'return_code': 'FAIL',
            'return_msg': 'verify error',
        }
    ret_xml = js_wxpay.generate_notify_resp(ret_dict)
    return ret_xml

@payment.route('/wechat/sdk/notify', methods=['GET', 'POST'])
def wechat_sdk_notify():
    xml_str = request.data
    ret, ret_dict = app_wxpay.verify_notify(xml_str)
    # 在这里添加订单更新逻辑
    wechat_update_payment(ret_dict)

    if ret:
        ret_dict = {
            'return_code': 'SUCCESS',
            'return_msg': 'OK',
        }
    else:
        ret_dict = {
            'return_code': 'FAIL',
            'return_msg': 'verify error',
        }
    ret_xml = app_wxpay.generate_notify_resp(ret_dict)
    return ret_xml


@payment.route('/wechat/order/<order_id>', methods=['GET'])
def order(order_id):
    xml_dict = js_wxpay.verify_order(out_trade_no=order_id)
    return json.dumps(xml_dict)
