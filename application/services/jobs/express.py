# encoding: utf-8
import json
import requests
from datetime import datetime

import application.models as Models
from application.cel import celery
from flask import current_app
from configs.enum import LOG_STATS
from application.utils import to_utc

__all__ = ['kuaidi_request']


@celery.task
def kuaidi_request(company, num):
    tracking = Models.ExpressTracking.find(company, num)

    data = {
        "id": "42d34cf10adedb39",  # 授权码，签订合同后发放
        "com": company,  # 订阅的快递公司的编码，一律用小写字母，见章五《快递公司编码》
        "nu": num,  # 订阅的快递单号
    }

    res = requests.get(
        'http://api.kuaidi100.com/api',
        params=data).json()

    Models.ExpressTracking.update_info(res)
    Models.ExpressRequestLog(company=company, number=num,
            respond=res).save()
    update_logistic_received_status(
        state=res['state'],
        com=res['com'],
        nu=res['nu'],
        data=res['data'])

    return res

def update_logistic_received_status(state, com, nu, data):
    latest_time = datetime.strptime(data[0]['time'], '%Y-%m-%d %H:%M:%S')
    first_time = datetime.strptime(data[-1]['time'], '%Y-%m-%d %H:%M:%S')
    check = (state == '3')   # received status

    # update cn logistic status
    for lo in Models.Logistic.objects(detail__cn_tracking_no=nu):

        if not check and lo.detail.status != LOG_STATS.SHIPPING:
            lo.update_logistic({
                'status': LOG_STATS.SHIPPING,
                'shipping_date': to_utc(first_time).replace(tzinfo=None),
                'modified_by': 'kuaidi100'
            })

        elif not check and 'ISC' in data[0]['ISC'] and lo.detail.status != LOG_STATS.PORT_ARRIVED:
            lo.update_logistic({
                'status': LOG_STATS.PORT_ARRIVED,
                'port_arrived_date': to_utc(latest_time).replace(tzinfo=None),
                'modified_by': 'kuaidi100'
            })


        elif check and lo.detail.status != LOG_STATS.RECEIVED:
            lo.update_logistic({
                'status': LOG_STATS.RECEIVED,
                'received_date': to_utc(latest_time).replace(tzinfo=None),
                'modified_by': 'kuaidi100'
            })
