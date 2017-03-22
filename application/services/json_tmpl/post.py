# -*- coding: utf-8 -*-
from flask_login import current_user
import application.models as Models
from configs.enum import NOTI_TYPE

def post_json(post):
    post_dt = post.to_simple_json()
    location = ''
    if post.location_extra:
        location = ", ".join(post.location_extra.values())
    post_dt.update({'location': location})
    is_liked = bool(Models.PostLike.objects(post=post, user_id=current_user.id))\
            if current_user.is_authenticated else False

    post_dt.update({'is_liked': is_liked})

    user = post.user
    user_info = dict(
            id = str(user.id),
            name = user.name,
            avatar_url = user.avatar_url,
            avatar_thumb = user.avatar_thumb,
        )
    post_dt.update({'user': user_info})
    return post_dt

def noti_json(noti):
    if noti.action == NOTI_TYPE.POST_LIKED:
        sub_title = u'赞你的帖子'
    if noti.action == NOTI_TYPE.FOLLOW:
        sub_title = u'关注你'
    if noti.action == NOTI_TYPE.COMMENT:
        sub_title = u'评论了你的帖子'
    if noti.action == NOTI_TYPE.REPLY:
        sub_title = u'回复了你'

    user = noti.user
    return dict(
        created_at = noti.created_at.strftime("%Y-%m-%dT%H:%M:%S Z"),
        action = noti.action,
        sub_title = sub_title,
        content = noti.info,
        user = dict(
                id = str(user.id),
                name = user.name,
                avatar_url = user.avatar_url,
                avatar_thumb = user.avatar_thumb,
            ),
        )
