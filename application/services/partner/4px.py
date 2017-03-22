# -*- coding: utf-8 -*-

import simplejson as json
import datetime
import requests
from suds.client import Client

from application.services.bingtrans import MSTranslate
from configs.settings import BING_APPID, BING_APPSECRET

class FourPX(object):

    TOOL_SERVICE_URL = 'http://api.4px.com/OrderOnlineToolService.dll?wsdl'
    ORDER_SERVICE_URL = "http://api.4px.com/OrderOnlineService.dll?wsdl"

    def __init__(self, token):
        '''
        初始化客户端实例
        '''
        self.token = token

    def create_order(self, lo):
        '''
        创建订单
        '''
        address = lo.order.address
        client = Client(self.ORDER_SERVICE_URL)
        order = client.factory.create("createOrderRequest")
        order.orderNo = lo.detail.partner_tracking_no
        order.productCode = lo.detail.channel or 'A1'
        order.initialCountryCode = 'CN'
        order.destinationCountryCode = address.country == 'United States' and 'US' or ''
        order.pieces = str(sum(entry.quantity for entry in lo.entries))
        order.customerWeight = str(lo.estimated_weight/1000)
        order.shipperCompanyName = 'Maybi Tech'
        order.shipperName = 'Shawn Tang'
        order.shipperAddress = 'Nanshanqu Sidadasha'
        order.shipperTelephone = '13822327121'
        order.consigneeName = address.receiver
        order.street = address.street1 + ' ' + str(address.street2) or ''
        order.city = address.city
        order.stateOrProvince = address.state
        order.consigneePostCode = address.postcode

        translator = MSTranslate(BING_APPID, BING_APPSECRET)


        for e in lo.entries:

            item = client.factory.create('declareInvoice')
            item.eName = translator.translate(e.item_snapshot.title, 'en', 'zh')
            item.name = e.item_snapshot.title
            item.declareUnitCode = 'PCE'
            item.declarePieces = e.quantity
            item.unitPrice = e.unit_price
            order.declareInvoice.append(item)

        res = client.service.createOrderService(self.token, order)
        return res


    def query_express(self, no):
        '''
         查询轨迹
        '''
        client = Client(self.TOOL_SERVICE_URL)
        res = client.service.cargoTrackingService(self.token, no)
        return res

    def cal_fee(self, country, weight):
        '''
         查询运费
        '''
        client = Client(self.TOOL_SERVICE_URL)
        charge = client.factory.create("chargeCalculateRequest")
        charge.countryCode = country
        charge.weight = weight
        res = client.service.chargeCalculateService(self.token, charge)
        return res
