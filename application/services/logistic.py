# -*- coding: utf-8 -*-
from datetime import datetime
import configs.signals as Signals
import application.models as Models
from application.models.order.logistic import gen_uid
import application.services.jobs as Jobs
from configs.enum import LOG_STATS, ORDER_TYPE
from application.utils import groupby, to_utc


class LogisticSpliter(object):

    def __init__(self, order=None, entries=None, log=None, debug=False):

        if order:
            self.order = order
            self.entries = entries or order.entries
            self.log = log

        if log:
            self.order = log.order
            self.entries = entries or log.entries
            self.log = log

        self.debug = debug

    def check_shoes_and_handbags(self):
        main_categories = [e.item_snapshot.main_category for e in self.entries]
        if 'shoes' in main_categories and not len(main_categories) == 1:
            # all are shoes
            if len(set(main_categories)) == 1:
                return False
            else:
                grouped_entries = groupby(
                    self.entries,
                    lambda x: x.item_snapshot.main_category == 'shoes'
                )
                return [self.do(self.order, list(e))
                        for k, e in grouped_entries]
        else:
            return False

    def split_with_amount(self):

        def gen_split_case(entries, packages=[], p_total=0):
            for e in entries:
                if e.amount_usd > 200:
                    yield [e]
                    continue
                if p_total + e.amount_usd > 200:
                    p_total = e.amount_usd
                    if packages:
                        pkg = packages
                        packages = [e]
                        yield pkg
                    else:
                        yield [e]
                else:
                    packages.append(e)
                    p_total += e.amount_usd

                if entries.index(e) == len(entries) - 1:
                    if packages:
                        yield packages

        amount = reduce(lambda x, y: x + y.amount_usd, self.entries, 0)

        if not amount > 200:
            return False
        else:
            ents = sorted(self.entries, key=lambda x: x.amount_usd, reverse=True)
            cases = [i for i in gen_split_case(ents)]
            if len(cases) == 1:
                return False
            return [self.do(self.order, e) for e in cases]

    def create(self):
        try:
            log = Models.Logistic(detail=self.log.detail)
        except:
            log = Models.Logistic(detail=Models.LogisticDetail())
        log.order = self.order
        log.entries = list(self.entries)
        self.order.logistics.append(log)
        if not self.debug:
            log.detail.partner = Models.Partner.objects().first()
            log.detail.partner_tracking_no = gen_uid()
            log.save()
            self.order.save()
        return log

    def do(self, order=None, entries=None):
        self.__init__(order=order, entries=entries, log=self.log)
        return reduce(lambda x, y: x or y(),
                      [self.check_shoes_and_handbags,
                       self.split_with_amount,
                       self.create], False)


@Signals.logistic_info_updated.connect
def look_for_new_tracking_no(sender, logistic):
    tracking = logistic.express_tracking
    if not tracking: return
    if not tracking.is_subscribed:
        Jobs.express.kuaidi_request.delay(
            tracking.company, tracking.number
        )
    else:
        print (tracking.number, ' is already subscribed')


def logistic_provider_dispatcher(order):
    Models.Logistic.create(order)

    for lo in order.logistics:
        if len(lo.entries) > 1:
            logs = LogisticSpliter(log=lo).do()
            # splitted
            if len(logs) > 1:
                lo.close(reason="close by auto spliter")

    order.reload()
    for lo in order.logistics:
        if order.order_type == ORDER_TYPE.TRANSFER:
            lo.detail.route = order.order_type
        lo.save()

    return order
