# -*- coding: utf-8 -*-
import decimal
import requests

class OpenExchangeRatesClientException(requests.exceptions.RequestException):
    pass


class OpenExchangeRatesClient(object):
    BASE_URL = 'http://openexchangerates.org/api'
    ENDPOINT_LATEST = BASE_URL + '/latest.json'
    ENDPOINT_CURRENCIES = BASE_URL + '/currencies.json'
    ENDPOINT_HISTORICAL = BASE_URL + '/historical/%s.json'

    def __init__(self, api_key):
        self.client = requests.Session()
        self.client.params.update({'app_id': api_key})

    def latest(self, base='USD'):
        """Fetches latest exchange rate data from service
        :Example Data:
            {
                disclaimer: "<Disclaimer data>",
                license: "<License data>",
                timestamp: 1358150409,
                base: "USD",
                rates: {
                    AED: 3.666311,
                    AFN: 51.2281,
                    ALL: 104.748751,
                    AMD: 406.919999,
                    ANG: 1.7831,
                    ...
                }
            }
        """
        try:
            resp = self.client.get(self.ENDPOINT_LATEST, params={'base': base})
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise OpenExchangeRatesClientException(e)
        return resp.json(parse_int=decimal.Decimal,
                         parse_float=decimal.Decimal)

    def currencies(self):
        """Fetches current currency data of the service
        :Example Data:
        {
            AED: "United Arab Emirates Dirham",
            AFN: "Afghan Afghani",
            ALL: "Albanian Lek",
            AMD: "Armenian Dram",
            ANG: "Netherlands Antillean Guilder",
            AOA: "Angolan Kwanza",
            ARS: "Argentine Peso",
            AUD: "Australian Dollar",
            AWG: "Aruban Florin",
            AZN: "Azerbaijani Manat"
            ...
        }
        """
        try:
            resp = self.client.get(self.ENDPOINT_CURRENCIES)
        except requests.exceptions.RequestException as e:
            raise OpenExchangeRatesClientException(e)

        return resp.json()

    def historical(self, date, base='USD'):
        """Fetches historical exchange rate data from service
        :Example Data:
            {
                disclaimer: "<Disclaimer data>",
                license: "<License data>",
                timestamp: 1358150409,
                base: "USD",
                rates: {
                    AED: 3.666311,
                    AFN: 51.2281,
                    ALL: 104.748751,
                    AMD: 406.919999,
                    ANG: 1.7831,
                    ...
                }
            }
        """
        try:
            resp = self.client.get(self.ENDPOINT_HISTORICAL %
                                   date.strftime("%Y-%m-%d"),
                                   params={'base': base})
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise OpenExchangeRatesClientException(e)
        return resp.json(parse_int=decimal.Decimal,
                         parse_float=decimal.Decimal)
