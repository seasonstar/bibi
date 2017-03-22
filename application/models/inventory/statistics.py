# -*- coding: utf-8 -*-
from application.extensions import db

__all__ = ['Statistics']


class Statistics(db.Document):
    meta = {
        'db_alias': 'inventory_db',
        'indexes': ['tag', 'sub_category', 'main_category', 'brand'],
    }

    main_category = db.StringField()
    sub_category = db.StringField()
    brand = db.StringField()
    tag = db.StringField()
    sex_tag = db.StringField()
    count = db.IntField(required=True, default=1)

    @classmethod
    def create(cls, main, sub, brand, tags, sex_tag):
        if not tags:
            tags = [None]

        for tag in tags:
            try:
                stats = cls.objects.get(main_category=main, sub_category=sub,
                        brand=brand, tag=tag, sex_tag=sex_tag)
                stats.count += 1
                stats.save()
            except:
                stats = cls(main_category=main, sub_category=sub,
                        brand=brand, tag=tag, sex_tag=sex_tag)
                stats.save()

    def to_json(self):
        return dict(
            main=self.main_category,
            sub=self.sub_category,
            brand=self.brand,
            tag=self.tag,
            sex_tag=self.sex_tag,
            count=self.count)
