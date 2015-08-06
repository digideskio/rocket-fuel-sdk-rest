import json
import os.path
import requests


class RestSFMC:
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

    def _call_api(self, url_path, json_parameters, http_method,
                  allow_access_token_refresh=True):
        '''
        calls api, handles expired access_token
        '''
        url = self.URL_DOMAIN + url_path
        payload = json.dumps(json_parameters)
        print(url)
        print(payload)
        if http_method == 'post':
            r = requests.post(url,
                              headers=self._request_header(),
                              data=payload)
        elif http_method == 'put':
            r = requests.put(url,
                             headers=self._request_header(),
                             data=payload)
        r = requests.post(url,
                          headers=self._request_header(),
                          data=payload)
        if r.status_code == 401:
            # handle access_token expiry after an hour.
            if allow_access_token_refresh:
                self.refresh_access_token(force_refresh=True)
                return self._call_api(url_path=url_path,
                                      json_parameters=json_parameters,
                                      http_method=http_method,
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
        # TODO: replace print with logging calls.
        # TODO: check last modified date with an hour?
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
        r = self._call_api(url_path, json_parameters, http_method='post')
        return r.json()['valid']

    def upsert_data_extension_rows(self, data_extension_key, pk_fields,
                                   rows):
        '''
        https://code.exacttarget.com/apis-sdks/rest-api/v1/hub/data-events/postDataExtensionRowsetByKey.html

        returns whether successful.

        Note: if a field is nullable, it can not be specified in the uploaded
        rows data.
        '''
        # TODO: limit max number of rows to upsert at once.
        path_template = '/hub/v1/dataevents/key:{key}/rowset'
        path = path_template.format(key=data_extension_key)
        json_parameters = []
        for row in rows:
            primary_keys = {pk_field: row[pk_field] for pk_field in pk_fields}
            json_parameter = {
                'keys': primary_keys,
                'values': row,
            }
            json_parameters.append(json_parameter)
        r = self._call_api(path, json_parameters, http_method='post')
        return r.status_code == 200

    def upsert_data_extension_row(self, data_extension_key, pk_fields,
                                  row):
        return self.upsert_data_extension_rows(data_extension_key=data_extension_key,
                                               pk_fields=pk_fields,
                                               rows=[row])

    def trigger_send(self, triggered_send_key):
        '''
        https://code.exacttarget.com/apis-sdks/rest-api/v1/messaging/messageDefinitionSends.html
        '''
        # TODO: implement me.
        pass
