# -*- coding: utf-8 -*-
from urllib import parse
from uuid import uuid4
import application.models as Models
from application.services.bingtrans import MSTranslate
from application.services.jobs.image import upload
from configs.enum import DictEnum

def get_specs_info(skus):
    if not skus:
        return []
    return map(get_spec_info, skus)


def get_spec_info(sku):
    spec = Models.ItemSpec.objects(sku=sku).first()
    if not spec:
        return {'sku': sku, 'found': False}
    item = Models.Item.objects(item_id=spec.item_id).first()
    brand = Models.Brand.objects(en=item.brand).first()
    brand_json = brand and brand.to_json() or ''

    return {
        'sku': sku,
        'found': True,
        'item_id': spec.item_id,
        'title': item.title,
        'brand': brand_json,

        'primary_image': item.primary_img,
        'item_available': item.availability,

        'price': spec.price,
        'available': spec.availability,
        'attributes': spec.attributes,
        'images': spec.images,
        'can_not_return': item.extra.get('can_return') is False,
    }


def get_items_weight(item_ids):
    total = 0
    for item_id, quantity in item_ids:
        item = Models.Item.objects(item_id=item_id).first()
        if not item:
            continue
        total += item.weight * quantity

    return total


def import_items(ls):
    translator = MSTranslate("maybi","UwX8zu/WCCOsrnEbbI36hGI3JNkQ7LwESYDm8e05xIk=")

    for row in ls:
        f =  row.split("\t")
        url = f[0]
        title = f[1]
        title_en = translator.translate(title, 'en', 'zh')
        china_price = float(float(f[2])+float(f[3]))
        price = float((str(china_price/6.3).split(".")[0] + '.99'))
        orig_price = float(str(price*1.2).split(".")[0]+'.99')
        weight = float(f[4])
        attributes = f[8].replace("{","").replace("}","").split(":")
        vendor='taobao'
        brand = 'other'
        main_category = 'home'
        sub_category = 'storage box'
        primary_img = f[9].replace("，",",").split(",")
        description = f[10]
        ps = parse.urlparse(url)
        web_id = parse.parse_qs(ps.query)['id'][0]

        images = []
        for img in primary_img:
            path = '{}/{}.jpeg'.format(brand, uuid4())
            url = upload('maybi-img', path, url=img, make_thumbnails=True)
            images.append(url)

        item = Models.Item.objects(web_id=web_id).first()
        if item:
            web_sku = 'taobao:%s'%primary_img[0].split("/")[-2]
            Models.ItemSpec(**{
                    'item_id': item.item_id,
                    'web_sku': web_sku,
                    'images': images,
                    'original_price': orig_price,
                    'price':price,
                    'attributes': {attributes[0]:attributes[1]}
            }).save()
            continue

        data = {
            'meta': {
                'url':url,
                'web_id': web_id,
                'title':title,
                'title_en': title_en,
                'china_price': china_price ,
                'original_price':orig_price,
                'main_category': main_category,
                'sub_category':sub_category,
                'price': price,
                'weight':weight,
                'attributes':[attributes[0]],
                'vendor':vendor,
                'brand':brand,
                'primary_img': primary_img[0],
                'description': description,
                'currency': 'USD',
                'sex_tag': 'UNCLASSIFIED',
                'tags': []
            },
            'specs':[{
                    'web_sku': 'taobao:%s'%primary_img[0].split("/")[-2],
                    'images': images,
                    'original_price': orig_price,
                    'price':price,
                    'attributes': {attributes[0]:attributes[1]}
                }],
        }
        Models.Item.create(data)

def import_entries(entries):
    translator = MSTranslate("maybi","UwX8zu/WCCOsrnEbbI36hGI3JNkQ7LwESYDm8e05xIk=")
    order_entries = []
    for entry in entries:
        item = DictEnum({
            '_data': dict(
                item_id = 0,
                url = 'http://maybi.cn/static/img/logo3.png',
                web_id = 'maybi',
                availability = False,
                currency = 'USD',
                china_price = entry['amount'],
                price = float(0),
                original_price = float(0),
                discount = 0,
                primary_img = 'http://maybi.cn/static/img/logo3.png',
                vendor= 'self',
                brand = 'self',
                main_category = entry['main_category'],
                sub_category = 'default',
                sex_tag = 'UNKNOWN',
                status = 'MOD',
                weight = float(0),
                extra = {'remark': entry.get('remark', '')},
                attributes = [],
                title = entry['title'],
                title_en = translator.translate(entry['title'], 'en', 'zh'),
            ),
        })

        ### spec
        spec = DictEnum({'_data': dict(
                item_id = 0,
                sku = 0,
                web_sku = 'maybi',
                images = [item._data.primary_img],
                china_price = item._data.china_price,
                price = item._data.price,
                original_price = item._data.price,
                discount = 0,
                availability = False,
                attributes = {},
                extra = item._data.extra,
            ),
        })
        item_snapshot = Models.ItemSnapshot.create(item)
        item_spec_snapshot = Models.ItemSpecSnapshot.create(spec, item_snapshot)

        entry = Models.OrderEntry(
            quantity=entry['quantity'],
            _item_snapshot=item_snapshot,
            _item_spec_snapshot=item_spec_snapshot,
            remark=entry['remark'],
            ).save()
        entry.update_amount()
        order_entries.append(entry)

    return order_entries
