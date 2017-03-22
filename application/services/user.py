# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import application.models as Models
from application.services.cart import merge_carts


def merge_coin_wallet(to_coin_wallet, from_coin_wallet):
    to_coin_wallet.balance += from_coin_wallet.balance
    to_coin_wallet.holdding += from_coin_wallet.holdding
    to_coin_wallet.cash += from_coin_wallet.cash
    to_coin_wallet.holdding_cash += from_coin_wallet.holdding_cash

    # merge coin trades
    Models.Trade.objects(wallet=from_coin_wallet).update(
        set__wallet=to_coin_wallet, set__user=to_coin_wallet.user)

    to_coin_wallet.save()
    from_coin_wallet.delete(w=1)


def merge_coupon_wallet(to_wallet, from_wallet):
    for c in from_wallet.consumable_coupons:
        to_wallet.consumable_coupons.append(c)
        to_wallet.save()
    from_wallet.delete(w=1)


def merge_users(user1, user2):
    if not user1.account.is_email_verified and \
            user2.account.is_email_verified:
        user1.account.email = user2.account.email
        user1.account.is_email_verified = True
    user1.level = max(user1.level, user2.level)
    user1.followers = list(set(user1.followers) | set(user2.followers))
    user1.following = list(set(user1.followings) | set(user2.followings))
    user1.num_followers = len(user1.followers)
    user1.num_followings = len(user1.followings)

    user1.favor_items = list(set(user1.favor_items) | set(user2.favor_items))
    user1.num_favors = len(user1.favor_items)

    # merge cart
    merge_carts(user_id_from=str(user2.id), user_id_to=str(user1.id))

    # merge coupon wallet.
    merge_coupon_wallet(user1.wallet, user2.wallet)

    # merge coin wallet
    merge_coin_wallet(user1.coin_wallet, user2.coin_wallet)

    # update orders
    Models.Order.objects(customer_id=user2.id).update(
        set__customer_id=user1.id)

    # merge logs
    Models.Log.objects(user_id=str(user2.id), is_guest=False).update(
        set__user_id=str(user1.id))

    # merge address
    for addr in user2.addresses:
        user1.addresses.append(addr)

    user1.save()
    user2.mark_deleted()
    return user1


def add_oauth(user, oauth):
    another_user = oauth.user
    if another_user and another_user is not user:
        merge_users(user, another_user)
    oauth.update(set__user=user)
