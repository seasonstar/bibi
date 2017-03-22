# -*- coding: utf-8 -*-
import json
from collections import defaultdict

from flask import Blueprint, session
from flask import request, jsonify
from flask_login import current_user, user_logged_in
from application.services.cache import cached
from application.utils import format_date, paginate
import application.services.json_tmpl as Json
import application.models as Models


home = Blueprint('home', __name__, url_prefix='/api/')

@home.route('banners', methods=['GET'])
@cached(900)
def banners():
    res = Models.Banner.get_latest()
    return jsonify(
        message='OK',
        banners=[r.to_json() for r in res]
    )

@home.route('boards', methods=['GET'])
def boards():
    data = request.args
    page = int(data.get('page', 0))
    per_page = int(data.get('per_page', 20))
    boards = Models.Board.objects(status="PUBLISHED")
    res = paginate(boards, page, per_page)

    return jsonify(
        message='OK',
        boards=[Json.board_json(r) for r in res]
    )

@home.route('board/<board_id>', methods=['GET'])
@cached(600)
def get_board(board_id):
    board = Models.Board.get_board(board_id)
    if not board:
        return jsonify(message='Failed')

    items = Models.Item.objects(web_id__in=board.items)

    board.view_count += 1
    board.save()

    return jsonify(message='OK', board=dict(
        date=format_date(board.published_at),
        image=board.image,
        desc=board.description,
        title=board.title,
        items=[Json.item_json_in_list(item) for item in items],
        ))

@home.route('categories', methods=['GET'])
@cached(timeout=21600)
def categories():
    category_dict = defaultdict(set)
    for stats in Models.Statistics.objects:
        category_dict[stats.main_category].add(stats.sub_category)

    category_list = []
    for main_category in category_dict.keys():
        main = Models.Category.objects(level=1, en=main_category).first()
        sub_list = []
        for sub_category in category_dict[main_category]:
            sub = Models.Category.objects(level=2, en=sub_category).first()
            if main and sub:
                sub_list.append(sub.to_json())
        category_list.append(
                dict(en=main.en,
                    cn=main.cn,
                    logo=main.logo,
                    sub_list=sub_list,
                )
            )
    return jsonify(dict(message='OK', categories=category_list))
