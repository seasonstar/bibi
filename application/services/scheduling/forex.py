from application.services.price.forex import OpenExchangeRatesClient
from configs.settings import OPENEXCHANGERATES_APPID
import application.models as Models
from application.cel import celery


@celery.task
def record_latest_forex_rate():
    client = OpenExchangeRatesClient(OPENEXCHANGERATES_APPID)
    res = client.latest()
    usd_to_cny = res['rates']['CNY']
    Models.ForexRate.put(usd_to_cny)
