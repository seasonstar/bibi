# -*- coding: utf-8 -*-
from math import ceil
import application.models as Models


ATTRIBUTES_MAPPING = {
    'size':           u'尺码',
    'color':          u'颜色',
    'style':          u'样式',
}


def get_item_attribute_list(item):
    attribute_desc = {}
    for k in item.attributes:
        attribute_desc[k] = ATTRIBUTES_MAPPING.get(k)
    return attribute_desc


def old_combination_json(item):
    def get_combination_values(spec, fields):
        values = {}
        for k in fields:
            value = spec.attributes[k]
            values.update({k:value})
        return values

    specs = item.available_specs
    fields = item.attributes

    combinations = []
    for s in specs:
        if not s.availability:
            continue
        values = get_combination_values(s, fields)

        combinations.append(values)

    return combinations

def combination_json(item):
    specs = item.available_specs
    combinations = []
    for s in specs:
        if not s.availability:
            continue
        combinations.append(s.attributes)

    return combinations



def item_json_in_list(item):
    title = item.title

    return dict(
        item_id=item.item_id,
        title=title,
        primary_img=item.primary_img,
        thumbnail=item.large_thumbnail,
        main_category=item.main_category,
        sub_category=item.sub_category,
        brand=item.brand,
        status=item.status,
        price=item.price,
        weight=item.weight,
        orig_price=item.original_price,
        discount=item.discount,
    )

def item_json(item):
    main = Models.Category.objects(en=item.main_category, level=1).first()
    sub = Models.Category.objects(en=item.sub_category, level=2).first()
    brand_doc = Models.Brand.objects(en=item.brand).first()

    main_category = main.to_json() if main else ''
    sub_category = sub.to_json() if sub else ''
    brand = brand_doc.to_json() if brand_doc else dict(cn=item.brand,
                                                       en=item.brand)
    attributes_desc = get_item_attribute_list(item)

    item_dict = dict(item_id=item.item_id,
                     title=item.title,
                     brand=brand,
                     attributes_desc=attributes_desc,
                     main_category=main_category,
                     sub_category=sub_category,
                     detail=item.description,
                     source=item.vendor,
                     price=item.price,
                     weight=item.weight,
                     orig_price=item.original_price,
                     discount=item.discount,
                     primary_img=item.primary_img,
                     large_thumbnail=item.large_thumbnail,
                     small_thumbnail=item.small_thumbnail,
                     status=item.status,
                     specs=[spec_json(s) for s in item.available_specs])
    return item_dict

def spec_json(spec):
    return dict(
        item_id=spec.item_id,
        sku=spec.sku,
        images=spec.images,
        orig_price=spec.original_price,
        price=spec.price,
        available=spec.availability,
        attributes=getattr(spec, "attributes", None),
    )

def board_json(board):
    return dict(
        id=str(board.id),
        date=str(board.published_at),
        image=board.image,
        desc=board.description,
        title=board.title,
        items=[item_json_in_list(item) for item in
            Models.Item.objects(web_id__in=board.items[:8])]
    )
