import json
import re
import time
import requests


class AuthenticationFailed(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ArgumentException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class MSTranslate():
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = ''

    def accessToken(self):
        data = {'client_id': self.client_id, 'client_secret': self.client_secret,
                'scope': 'http://api.microsofttranslator.com',
                'grant_type': 'client_credentials'}
        r = requests.post('https://datamarket.accesscontrol.windows.net/v2/OAuth2-13/', data=data)
        result = json.loads(r.text)
        if 'error_description' in result:
            raise AuthenticationFailed(result['error_description'])
        else:
            self.access_token = result['access_token']
            self.time = time.time()

    def translate(self, text, toLang, fromLang=None):
        if (not self.access_token):
            self.accessToken()
        elif int(time.time() - self.time) > 550:
            self.accessToken()
        authToken = 'Bearer ' + self.access_token
        headers = {'Authorization': authToken}
        params = {'text': text, 'from': fromLang, 'to': toLang}
        result = requests.get('http://api.microsofttranslator.com/v2/Http.svc/Translate', params=params,
                              headers=headers)
        if 'Argument Exception' in result.text:
            error = re.search(r'<p>Message:(.*?)</p>', result.text.replace('\n', '')).group(1)
            raise ArgumentException(error)
        else:
            return result.text[68:-9]
