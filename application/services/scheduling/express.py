import application.models as Models
from application.cel import celery
import application.services.jobs as Jobs


@celery.task
def check_kuaidi():
    los = Models.Logistic.objects(is_closed=False,
            detail__cn_tracking_no__ne='', detail__cn_logistic_name__ne='',
            detail__status__in=['SHIPPING', 'PORT_ARRIVED'])
    for lo in los:
        Jobs.express.kuaidi_request(lo.detail.cn_logistic_name, lo.detail.cn_tracking_no)
