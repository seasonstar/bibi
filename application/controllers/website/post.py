# -*- coding: utf-8 -*-
import datetime
import json

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from flask_babel import gettext as _

from application.utils import get_session_key, paginate
from application.services.cache import cached
from application.services.log import log_post_visit
import application.models as Models
import application.services.jobs as Jobs
import application.services.json_tmpl as Json


post = Blueprint('posts', __name__, url_prefix='/api/post')

def refactor_query(data):
    query = {}
    for k,v in data.items():
        if v in [None, u"None", "", "null"]:
            continue
        elif k == 'title':
            query.update({'title__icontains': v})
        elif 'page' in k:
            query.update({k: int(v)})
        elif 'type' in k:
            query.update({'post_type': v.upper()})
        else:
            query.update({k: v})
    return query

@post.route('/create', methods=['POST'])
@login_required
def create():
    data = request.json
    post_dict = {
            'primary_image': data.get('primary_image'),
            'images': data.get('photos'),
            'title': data.get('title'),
            'location': data.get('geo') if data.get('geo') else None,
            'tags': data.get('tags'),
            'post_type': data.get('type'),
            'user_id': current_user.id,
        }

    location = data.get('location').split(",")
    if location and len(location) == 3:
        location_extra = {
                'city': location[0],
                'state': location[1],
                'country': location[2],
            }
        post_dict['location_extra'] = location_extra

    objects = Models.Post.create(post_dict)

    return jsonify(message='OK')

@post.route('/list', methods=['GET'])
#@cached(3600)
def posts():
    query = refactor_query(request.args)
    page = query.pop('page', 0)
    per_page = query.pop('per_page', 20)

    objects = Models.Post.approved_posts(**query)
    posts = paginate(objects, page, per_page)
    data=[Json.post_json(p) for p in posts]
    return jsonify(message='OK', posts=data, total=objects.count())


@post.route('/detail/<int:post_id>', methods=['GET'])
def post_detail(post_id):
    post = Models.Post.objects(post_id=post_id).first_or_404()

    post_dict = Json.post_json(post)
    comments = Models.PostComment.objects(post=post)
    comments_json = [c.to_json() for c in comments]
    likes = Models.PostLike.objects(post=post)
    likes_json = [l.to_json() for l in likes]

    post_dict.update({'comments': comments_json})
    post_dict.update({'likes': likes_json})

    if current_user.is_authenticated:
        user = current_user._get_current_object()
    else:
        user = Models.GuestRecord.by_key(get_session_key())

    log_post_visit(user_id=user.id, post_id=post_id)
    return jsonify(message='OK', post=post_dict)

@post.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Models.Post.objects(post_id=post_id, user_id=current_user.id).first_or_404()
    post.approved = False
    post.save()
    return jsonify(message='OK')


@post.route('/comment/add', methods=['POST'])
@login_required
def create_comment():
    data = request.json
    content = data.get('content')
    if not content:
        return jsonify(message='Failed', error=u"请不要为空")

    post_id = data.get('post_id')
    post = Models.Post.objects(post_id=post_id).first_or_404()
    comment = Models.PostComment(content=content, post=post, user_id=current_user.id).save()
    post.num_comments += 1
    post.save()
    if current_user.id != post.user_id:
        Models.PostActivity.create(user=current_user.id, to_user=post.user_id, post=post, action='COMMENT', info=content)
    return jsonify(message='OK', comment=comment.to_json())

@post.route('/comment/delete', methods=['POST'])
@login_required
def delete_comment():
    data = request.json
    post_id = data.get('post_id')
    comment_id = data.get('comment_id')
    comment = Models.PostComment.objects(user_id=current_user.id, id=comment_id)
    if comment:
        comment.delete()
        post = Models.Post.objects(post_id=post_id).first_or_404()
        post.num_comments -= 1
        post.save()
        return jsonify(message='OK')
    return jsonify(message="Failed", error=u"您无权删除此评论")


@post.route('/likes', methods=['GET'])
@login_required
def like_posts():
    data = request.args
    user_id = data.get('user_id', current_user._get_current_object().id)
    page = int(data.get('page', 0))
    per_page = int(data.get('per_page', 20))

    objects = Models.PostLike.objects(user_id=user_id)
    likes = paginate(objects , page, per_page)

    return jsonify(message='OK',
                   posts=[Json.post_json(l.post) for l in likes])


@post.route('/<post_id>/likes', methods=['GET'])
def post_likes(post_id):
    data = request.args
    page = int(data.get('page', 0))
    per_page = int(data.get('per_page', 20))
    post = Models.Post.objects(post_id=post_id).first_or_404()

    objects = Models.PostLike.objects(post=post)
    likes = paginate(objects , page, per_page)

    return jsonify(message='OK',
                    users=[Json.user_json(l.user) for l in likes])


@post.route('/like/<int:post_id>', methods=['POST'])
@login_required
def post_like(post_id):
    post = Models.Post.objects(post_id=post_id).first_or_404()
    if not Models.PostLike.objects(post=post, user_id=current_user.id):
        like = Models.PostLike(user_id=current_user.id, post=post).save()
        current_user.mark_like(post)
        if current_user.id != post.user_id:
            Models.PostActivity.create(user=current_user.id, to_user=post.user_id, post=post, action='POST_LIKED')
        return jsonify(message='OK', like=like.to_json())
    return jsonify(message='Failed', error=u'您已经赞过了')


@post.route('/unlike/<int:post_id>', methods=['POST'])
@login_required
def post_unlike(post_id):
    post = Models.Post.objects(post_id=post_id).first_or_404()
    like = Models.PostLike.objects(user_id=current_user.id, post=post)
    if like:
        like.delete()
        current_user.mark_unlike(post)
        return jsonify(message='OK')
    return jsonify(message='Failed', error=u'您已取消过赞')


@post.route('/image_uploaded', methods=['POST'])
def image_uploaded():
    data = request.json
    path = data.get('url')
    url = "http://assets.maybi.cn/%s" % path
    Jobs.image.make_thumbnails('maybi-img', path, url)

    if data.get('type') == 'primary_image':
        post = Models.Post.objects(primary_image=url).first_or_404()
        post.approved = True
        post.save()

    return jsonify(message='OK')


@post.route('/tags/<kind>', methods=['GET'])
@cached(3600)
def get_tags(kind):
    tags = Models.PostTag.objects(kind=kind)
    if kind == 'TRADE':
        cn_name = u"买卖"
    elif kind == 'SERVICE':
        cn_name = u"服务"
    elif kind == 'SHOW':
        cn_name = u"心情"
    tags_group = {
            'name': cn_name,
            'tag_list': [tag.name for tag in tags]
        }
    return jsonify(message='OK', tags_group=tags_group)


@post.route('/report', methods=['POST'])
@login_required
def report():
    data = request.json
    subject = data.get('subject')
    post_id = data.get('post_id')
    post = Models.Post.objects(post_id=post_id).first_or_404()
    feedback = Models.PostFeedback(post=post, subject=subject, user_id=current_user.id).save()
    return jsonify(message='OK')


@post.route('/activities', methods=['GET'])
@login_required
def get_activities():
    data = request.args
    user_id = data.get('user_id', current_user._get_current_object().id)
    page = int(data.get('page', 0))
    per_page = int(data.get('per_page', 20))

    objects = Models.PostActivity.objects(to_user_id=user_id)
    activities = paginate(objects , page, per_page)

    return jsonify(message='OK',
                   notices=[Json.noti_json(ac) for ac in activities])
