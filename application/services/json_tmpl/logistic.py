# -*- coding: utf-8 -*-
from flask_login import current_user
import application.models as Models

def channel_prices(items, country):
    total_weight = sum([item.weight * quantity
                    for item, quantity in items])
    weight_desc = u'商品总重量{}kg'.format(total_weight/1000)
    channels_json = []
    channels = Models.ChannelProvider.active(country=country)
    for channel in channels:
        channels_json.append(dict(
            name = channel.name,
            display_name = channel.display_name,
            desc = channel.description,
            service_intro = channel.service_intro,
            cn_shipping = channel.shipping,
        ))
    return {'weight': total_weight, 'weight_desc': weight_desc,
            'providers': channels_json}

def logistic_provider_prices(items, country, weight=0):
    if weight:
        total_weight = weight
    else:
        total_weight = sum([item.weight * quantity
                        for item, quantity in items])
    weight_desc = u'商品总重量{}kg'.format(total_weight/1000)
    providers_json = []
    providers = Models.LogisticProvider.active(country=country,
            limited_weight__gte=total_weight)
    for provider in providers:
        shipping = provider.get_shipping(total_weight)
        providers_json.append(dict(
            name = provider.name,
            display_name = provider.display_name,
            desc = provider.description,
            service_intro = provider.service_intro,
            cn_shipping = shipping,
        ))
    return {'weight': total_weight, 'weight_desc': weight_desc,
            'providers': providers_json}


def get_display_provider_info(country, total_weight):
    weight_desc = u'商品总重量{}kg'.format(total_weight/1000)
    providers_json = []
    providers = Models.LogisticProvider.active(country=country,
            limited_weight__gte=total_weight)
    for provider in providers:
        shipping = provider.get_shipping(total_weight)
        providers_json.append(dict(
            name=provider.display_name,
            logo=provider.logo,
            init_price=provider.init_price,
            init_weight=provider.init_weight,
            continued_price=provider.continued_price,
            continued_weight=provider.continued_weight,
            desc=provider.description,
            service_intro=provider.service_intro,
            rule_desc=provider.rule_desc,
            cn_shipping = shipping,
        ))
    return {'weight': total_weight, 'weight_desc': weight_desc,
            'providers': providers_json}
