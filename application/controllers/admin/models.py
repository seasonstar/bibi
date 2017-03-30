# -*- coding: utf-8 -*-

from flask_admin.babel import gettext
from flask_admin.contrib.mongoengine.filters import BaseMongoEngineFilter
from application.extensions import admin
import application.models as Models
from . import MBModelView


class UserView(MBModelView):
    form_subdocuments = {
        'account': {
            'form_columns': ('email',  'mobile_number', 'activation_key', 'activate_key_expire_date')
        },
    }

class LogView(MBModelView):
    can_create = False
    column_default_sort = ('created_at', True)
    column_filters = ('log_type', )



admin.add_view(MBModelView(Models.BackendPermission, category='Admin'))
admin.add_view(MBModelView(Models.Role, category='Admin'))

admin.add_view(UserView(Models.User, category='User', endpoint='usermodel'))
admin.add_view(MBModelView(Models.SocialOAuth, category='User'))
admin.add_view(MBModelView(Models.Cart, category='User', endpoint='cartmodel'))
admin.add_view(MBModelView(Models.EntrySpec, category='User'))
admin.add_view(MBModelView(Models.Coupon, category='User'))
admin.add_view(MBModelView(Models.CouponWallet, category='User'))
admin.add_view(MBModelView(Models.OrderEntry, category='User'))
admin.add_view(MBModelView(Models.CoinWallet, category='User'))
admin.add_view(MBModelView(Models.CoinTrade, category='User'))
admin.add_view(MBModelView(Models.Address, category='User', endpoint='addressmodel'))
admin.add_view(MBModelView(Models.GuestRecord, category='User'))

admin.add_view(MBModelView(Models.Item, category='Inventory', endpoint ='itemmodel'))
admin.add_view(MBModelView(Models.ItemSpec, category='Inventory'))
admin.add_view(MBModelView(Models.Brand, category='Inventory'))
admin.add_view(MBModelView(Models.Category, category='Inventory'))
admin.add_view(MBModelView(Models.Tag, category='Inventory'))
admin.add_view(MBModelView(Models.Vendor, category='Inventory'))
admin.add_view(MBModelView(Models.PriceHistory, category='Inventory'))
admin.add_view(MBModelView(Models.ForexRate, category='Inventory'))

admin.add_view(MBModelView(Models.Payment, category='Order', endpoint="paymentmodel"))
admin.add_view(MBModelView(Models.LogisticProvider, category='Logistics'))
admin.add_view(MBModelView(Models.ChannelProvider, category='Logistics'))
admin.add_view(MBModelView(Models.Partner, category='Logistics'))
admin.add_view(MBModelView(Models.Order, category='Order'))
admin.add_view(MBModelView(Models.TransferOrderCode, category='Order'))
admin.add_view(MBModelView(Models.OrderExtra, category='Order'))

admin.add_view(MBModelView(Models.Board, category='Content'))
admin.add_view(MBModelView(Models.Post, category='Content'))
admin.add_view(MBModelView(Models.PostComment, category='Content'))
admin.add_view(MBModelView(Models.PostLike, category='Content'))
admin.add_view(MBModelView(Models.PostActivity, category='Content'))
admin.add_view(MBModelView(Models.PostFeedback, category='Content'))
admin.add_view(MBModelView(Models.PostTag, category='Content'))
