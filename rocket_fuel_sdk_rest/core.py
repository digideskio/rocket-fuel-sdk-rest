import datetime
import json
import logging
import os.path
import requests
import time


logger = logging.getLogger(__name__)

class RestSFMC:
    '''
    Sales Force Marketing Cloud API
    '''

    URL_DOMAIN = 'https://www.exacttargetapis.com'
    REQUEST_TOKEN_URL = 'https://auth.exacttargetapis.com/v1/requestToken'

    def __init__(self, client_id, client_secret,
                 access_token_cache='/tmp/rocket_fuel_access_token.txt'):
        # TODO(shauno): cache be default based on hash of client_id and client_secret
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
        logger.info("API call url: " + url)
        logger.info("API payload: " + payload)
        for attempt in range(5):
            try:
                if http_method == 'post':
                    r = requests.post(url,
                                      headers=self._request_header(),
                                      data=payload)
                elif http_method == 'put':
                    r = requests.put(url,
                                     headers=self._request_header(),
                                     data=payload)
                break
            except requests.exceptions.ConnectionError:
                time.sleep(3)
        else:   # no-break
            raise requests.exceptions.ConnectionError

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
            logger.info(self.access_token, 'from web')
        else:
            with open(self.access_token_cache, 'r') as f:
                self.access_token = f.read()
                logger.info(self.access_token, 'from file')

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
            for k, v in row.items():
                if isinstance(v, (datetime.date, datetime.datetime)):
                    row[k] = v.isoformat()
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

    def trigger_send(self, triggered_send_key,
                     subscriber_key, email_address, recipient_attributes):
        '''
        https://code.exacttarget.com/apis-sdks/rest-api/v1/messaging/messageDefinitionSends.html

        example response from API
        status_code: 202

        {
            'requestId': 'f37f134b-8e3e-445f-a9cc-3b2296b6f627',
            'responses': [
                {
                    'messages': ['Queued'],
                    'hasErrors': False,
                    'recipientSendId': 'f37f134b-8e3e-445f-a9cc-3b2296b6f627'
                }
            ]
        }
        '''
        path_template = '/messaging/v1/messageDefinitionSends/key:{key}/send'
        path = path_template.format(key=triggered_send_key)

        json_parameters = {
            'To': {
                'Address': email_address,
                'SubscriberKey': email_address,
                'ContactAttributes': {
                    'SubscriberAttributes': recipient_attributes,
                },
            },
        }
        r = self._call_api(path, json_parameters, http_method='post')
        return r.status_code == 202

    def send_sms(self, message_key, mobile_numbers, message=None,
        subscribe=False, resubscribe=False, keyword=None, override=False):
        '''
        https://code.exacttarget.com/apis-sdks/rest-api/v1/sms/postMessageContactSend.html

        example response from API
        status_code: 202

        HTTP/1.1 202 Accepted
        {
          "tokenId": "c21NCNSDN2sMMWM2miosdjEHH",
        }

        SEND /sms/v1/messageContact/Mjo3ODow/send
        {
            "mobileNumbers": [
            "61413682052"
            ],
            "Subscribe": true,
            "Resubscribe": true,
            "keyword": "ROBTEST"
        }
        '''
        path_template = '/sms/v1/messageContact/{message_key}/send'
        path = path_template.format(message_key=message_key)

        json_parameters = {
            "mobileNumbers": mobile_numbers,
            "subscribe": subscribe,
            "resubscribe": resubscribe,
            "keyword": keyword,
            "override": override
        }

        if message:
            json_parameters['messageText'] = message

        if keyword:
            json_parameters['keyword'] = keyword

        r = self._call_api(path, json_parameters, http_method='post')
        return r.status_code == 202
