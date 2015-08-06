import json
import os.path
import requests


class SFMC:
    '''
    Sales Force Marketing Cloud API
    '''

    URL_DOMAIN = 'https://www.exacttargetapis.com'
    REQUEST_TOKEN_URL = 'https://auth.exacttargetapis.com/v1/requestToken'

    def __init__(self, client_id, client_secret,
                 access_token_cache='/tmp/rocket_fuel_access_token.txt'):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token_cache = access_token_cache
        self.refresh_access_token()

    def _request_header(self):
        '''
        handles custom header for authorization
        '''
        headers = {'Authorization': 'Bearer {}'.format(self.access_token)}
        headers['Authorization'] = headers['Authorization']
        return headers

    def _call_api(self, url_path, json_parameters,
                  allow_access_token_refresh=True):
        '''
        calls api, handles expired access_token
        '''
        url = self.URL_DOMAIN + url_path
        payload = json.dumps(json_parameters)
        r = requests.post(url,
                          headers=self._request_header(),
                          data=payload)
        if r.status_code == 401:
            # handle access_token expiry after an hour.
            if allow_access_token_refresh:
                self.refresh_access_token(force_refresh=True)
                return self._call_api(url_path,
                                      json_parameters,
                                      allow_access_token_refresh=False)
            else:
                return
        return r

    def request_access_token(self):
        '''
        Get new access token for api authorization
        '''
        payload = {
            'clientId': self.client_id,
            'clientSecret': self.client_secret,
        }
        r = requests.post(self.REQUEST_TOKEN_URL, data=payload)
        access_token = r.json()['accessToken']
        return access_token

    def refresh_access_token(self, force_refresh=False):
        '''
        get access_token, either from on disk cache, or from the web.
        '''
        # check last modified date with an hour?
        if force_refresh or not os.path.isfile(self.access_token_cache):
            self.access_token = self.request_access_token()
            with open(self.access_token_cache, 'w') as f:
                f.write(self.access_token)
            print(self.access_token, 'from web')
        else:
            with open(self.access_token_cache, 'r') as f:
                self.access_token = f.read()
                print(self.access_token, 'from file')

    def validate_email(self, email_address):
        url_path = '/address/v1/validateEmail'
        json_parameters = {
            'email': email_address,
            'validators': ['SyntaxValidator'],
        }
        r = self._call_api(url_path, json_parameters)
        return r.json()['valid']
