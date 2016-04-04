import json
import requests
from datetime import datetime

from knurld_sdk import app_globals as g


def authorization_header(token, _type='json', developer_id=None):

    headers = {
        'Content-Type': 'application/' + str(_type),
        'Authorization': 'Bearer ' + str(token),
        'Developer-Id': g.config['DEVELOPER_ID']
    }

    # for a consumer the consumer token replaces the Developer-Id
    if developer_id:
        headers['Developer-Id'] = developer_id

    return headers


class Verification(object):
    pass


class Enrollment(object):

    def __init__(self, token, model, consumer):
        self.enrollment = None
        self.consumer_token = None
        self._token = token
        self.app_model = model
        self.consumer = consumer

    @property
    def enrollment_id(self):
        if self.enrollment:
            return str(self.enrollment.split('/')[-1])
        return ''

    @property
    def payload(self):

        payload = {
            "consumer": self.consumer,
            "application": self.app_model
        }
        return payload

    def upsert_enrollment(self, enrollment_id=None, wav_file=None):
        """
        TODO: sample test for the Sphinx documentation
        py:function:: upsert_enrollment(sequence[, start=0])

           Return an iterator that yields tuples of an index and an item of the
           *sequence*. (And so on.)
        """

        headers = authorization_header(self._token)

        if wav_file:
            self.payload['enrollment.wav'] = wav_file

        url = g.config['URL_ENROLLMENTS']
        if enrollment_id:
            url += '/' + enrollment_id

        print(url)
        print(self.payload)
        print(headers)
        response = requests.post(url, json=self.payload, headers=headers)
        print(response)
        result = json.loads(response.content)

        if result.get('href'):
            self.enrollment = result.get('href')

        return result

    def get_enrollment(self, enrollment_id=None):

        headers = authorization_header(self._token)

        url = g.config['URL_ENROLLMENTS']
        if enrollment_id:
            url += '/' + enrollment_id

        response = requests.get(url, headers=headers)
        result = json.loads(response.content)

        if result.get('href'):
            self.enrollment = result.get('href')

        return result

    def get_consumer_token(self, username, password):

        payload = {'username': username,
                   'password': password}

        headers = authorization_header(self._token)
        url = g.config['URL_CONSUMERS'] + '/token'

        response = requests.post(url, json=payload, headers=headers)
        self.consumer_token = json.loads(response.content).get('token')

        return self.consumer_token


class Consumer(object):

    def __init__(self, token):
        self._token = token
        self.consumer = None

    @property
    def consumer_id(self):
        if self.consumer:
            return self.consumer.split('/')[-1]
        return ''

    def upsert_consumer(self, payload, consumer_id=None):
        """
        TODO: convert it as per the following definition using consumer_id
        update or insert the app model
        :param
        payload (e.g. format) = {
            "gender": "M",
            "username": "theo",
            "password": "walcott"
        }
        consumer_id: an existing consumer_id
        :return: href for the created or updated consumer
        """

        headers = authorization_header(self._token)

        url = g.config['URL_CONSUMERS']
        if consumer_id:
            url += '/' + consumer_id

        response = requests.post(url, json=payload, headers=headers)
        self.consumer = json.loads(response.content).get('href')

        return self.consumer_id

    def get_consumer(self, consumer_id=None):

        headers = authorization_header(self._token)

        url = g.config['URL_CONSUMERS']
        if consumer_id:
            url += '/' + consumer_id

        response = requests.get(url, headers=headers)
        result = json.loads(response.content)

        # if you are getting multiple consumers in result
        if result.get('items'):
            for item in result.get('items'):
                print item.get('href')
            # set the first one from result to be the consumer for this result
            self.consumer = result.get('items')[0].get('href')
        elif result.get('href'):
            print result.get('href')
            self.consumer = result.get('href')

        return self.consumer_id


class AppModeler(object):

    def __init__(self, token):
        self._token = token
        self.app_model = None

    @property
    def app_model_id(self):
        if self.app_model:
            return self.app_model.split('/')[-1]
        return ''

    def upsert_app_model(self, payload, app_model_id=None):
        """
        TODO: convert it as per the following definition using app_model_id
        update or insert the app model
        :param
        payload (e.g. format) = {
                "vocabulary": ["boston", "chicago", "pyramid"],
                "verificationLength": 3,
                "enrollmentRepeats": 3
            }
        app_model_id: an existing app model
        :return: href for the created or updated app model
        """

        headers = authorization_header(self._token)

        url = g.config['URL_APP_MODELS']
        if app_model_id:
            url += '/' + app_model_id

        response = requests.post(url, json=payload, headers=headers)
        self.app_model = json.loads(response.content).get('href')

        return self.app_model_id

    def get_app_model(self, app_model_id=None):

        headers = authorization_header(self._token)

        url = g.config['URL_APP_MODELS']
        if app_model_id:
            url += '/' + app_model_id

        response = requests.get(url, headers=headers)
        result = json.loads(response.content)
        if result.get('href'):
            self.app_model = result.get('href')

        return result


class TokenGetter(object):
    """
    Makes sure you always get a valid token. Validates the current available token and renews it if it has expired
    """

    def __init__(self, token=None, expires=None):
        self._token = token
        self._token_timestamp = datetime.now()
        self._token_expires = expires if expires else g.config['TOKEN_EXPIRES']

    def _is_valid_token(self, token):
        """
        checking the validity of token based on the time it was issued last
        """
        try:
            time_lapse = (datetime.now() - self._token_timestamp).total_seconds()
            # print('time_lapse: ' + str(time_lapse))
            if time_lapse < self._token_expires:
                return True
            else:
                # print("Invalid token {} with timestamp {}".format(token, self._token_timestamp))
                return False
        except ValueError as e:
            print("Invalid token {} Details: {}".format(token, e))

        return False

    def __deprecated__is_valid_token_status(self):
        """
        TO BE OBSOLETE METHOD
        Brian: do not rely on the token status api as it is going to go obsolete
        """
        params = authorization_header(self._token)

        response = requests.get(g.config['URL_TOKEN_STATUS'], params=params)
        return True if response.status_code == 200 else False

    def renew_access_token(self):

        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Host': g.config['HOST']
                   }

        payload = {'client_id': g.config['CLIENT_ID'],
                   'client_secret': g.config['CLIENT_SECRET']
                   }

        response = requests.post(g.config['URL_ACCESS_TOKEN'], data=payload, headers=headers)
        self._token = json.loads(response.content).get('access_token')
        self._token_timestamp = datetime.now()

        return self._token

    def get_token(self):
        """
        caching the already fetched token for duration configed in TOKEN_EXPIRES before the token could be renewed again
        """
        # check the cached version of the token first
        self._token = g.region.get_or_create("this_hour_token", creator=self.renew_access_token,
                                             expiration_time=self._token_expires,
                                             should_cache_fn=self._is_valid_token)
        return self._token
