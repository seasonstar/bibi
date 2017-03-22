# -*- coding: utf-8 -*-
from flask_login import current_user
import application.models as Models
import configs.signals as Signals
from application.extensions import db


def log_item_visit(user_id, item_id):
    Models.Item.objects(item_id=item_id).update_one(inc__num_views=1)

def log_post_visit(user_id, post_id):
    Models.Post.objects(post_id=post_id).update_one(inc__num_views=1)

@Signals.item_bought.connect
def inc_num_buy(sender, item_id):
    Models.Item.objects(item_id=item_id).update_one(inc__num_buy=1)

def get_user_id():
    if current_user and not current_user.is_anonymous:
        return str(current_user._get_current_object().id)
    return 'system'

def log_logistic_modified(document_id, info):
    user_id = get_user_id()
    Models.LogisticLog(
        logistic_id=document_id,
        info=info,
        user_id=user_id
    ).save()

def logistic_pre_save(sender, document, created, **kwargs):
    if created:
        return
    detail_changes_to_log = document.detail._changed_fields
    if detail_changes_to_log:
        info = {field: getattr(document.detail, field) for field in detail_changes_to_log if field not in ['remarks', 'irregular_details', 'delay_details', 'attachment']}
        log_logistic_modified(document.id, info)


db.pre_save_post_validation.connect(logistic_pre_save, sender=Models.Logistic)
