# -*- coding: utf-8 -*-
import application.models as Models
from flask_login import current_user

def get_user_info(user):
    coin_wallet = user.coin_wallet
    coins = coin_wallet.balance
    cash = coin_wallet.cash
    stat = Models.OrderStat.by_user(user_id=user.id)

    info = dict(
        id=str(user.id),
        name=user.name,
        avatar_url=user.avatar_url,
        avatar_thumb=user.avatar_thumb,
        coins=coins,
        cash=cash,
        consumable_coupons=[
            c.to_json()
            for c in user.wallet.consumable_coupons
            if not c.is_expired],
        num_followers=user.num_followers,
        num_followings=user.num_followings,
        total=stat.received,
        num_orders=stat.num_orders,
        num_waiting=stat.num_waiting,
        num_unpaid=stat.num_unpaid,
        num_favors=user.num_favors)
    return info


def user_json(user):
    return dict(
        id=str(user.id),
        name=user.name,
        avatar_url=user.avatar_url,
        avatar_thumb=user.avatar_thumb,
        num_followers=user.num_followers,
        num_followings=user.num_followings,
        is_following=current_user.is_following(user) if \
            current_user and current_user.is_authenticated else False,
    )
