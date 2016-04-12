# -*- coding: utf-8 -*-

import json
import re
import requests
import time
from datetime import datetime

from knurld_sdk import app_globals as g
from knurld_sdk import helpers as h
from knurld_sdk.uploader.Dropbox import upload, share, dropbox_client


def authorization_header(token=None, content_type='application/json', developer_id=None):

    try:
        tg = TokenGetter()
        token = token if token else tg.get_token()

        headers = {
            'Content-Type': content_type,
            'Authorization': 'Bearer ' + str(token),
            'Developer-Id': g.config['DEVELOPER_ID']
        }
        # for a consumer the consumer token replaces the Developer-Id
        if developer_id:
            headers['Developer-Id'] = developer_id

        return headers

    except Exception as e:
        print('Could not obtain Authorization header' + str(e))
        return None


class Verification(object):
    pass


class Enrollment(object):

    def __init__(self, token, model, consumer):
        self.token = token
        self.app_model = model
        self.consumer = consumer
        self.enrollment_url = None

    @property
    def enrollment_id(self):
        return h.parse_id_from_href(self.enrollment_url)

    @property
    def payload(self):
        p = {
            "application": self.app_model,
            "consumer": self.consumer
        }
        return p

    def create(self):
        """ create the enrollment using an app-model and consumer
        """
        headers = authorization_header()

        try:
            url = g.config['URL_ENROLLMENTS']

            response = requests.post(url, json=self.payload, headers=headers)
            return h.get_response_content(response)

        except Exception as e:
            print('Could not perform the operation: ' + str(e))
            return None

    def update(self, enrollment_id, wav_file=None, intervals=None):

        if not enrollment_id:
            print('Enrollment Id is required.')
            return None

        headers = authorization_header()

        if wav_file:
            self.payload['enrollment.wav'] = wav_file

        if intervals:
            self.payload['intervals'] = intervals

        try:
            url = g.config['URL_ENROLLMENTS'] + '/' + enrollment_id

            response = requests.post(url, json=self.payload, headers=headers)
            return h.get_response_content(response)

        except Exception as e:
            print('Could not perform the operation: ' + str(e))
            return None

    def get(self, enrollment_id):
        """ get enrollment for the given enrollment id
        """
        headers = authorization_header()

        try:
            url = g.config['URL_ENROLLMENTS'] + '/' + enrollment_id

            response = requests.get(url, headers=headers)
            return h.get_response_content(response)

        except Exception as e:
            print('Could not perform the operation: ' + str(e))
            return None

    def get_all(self, start=0, end=10, offset=10):
        """ return all the enrollments for given offset, start, end
            TODO: the proper usage of parameters
        """

        headers = authorization_header()

        try:
            url = g.config['URL_ENROLLMENTS']

            response = requests.get(url, headers=headers)
            return h.get_response_content(response)

        except Exception as e:
            print('Could not perform the operation: ' + str(e))
            return None

    def steps(self, recorded_file_url):
        # step-1: put consumer_id, model_id
        response = self.create()
        self.enrollment_url = h.parse_response(response, get_field='href')
        print('step-1: create: put consumer_id, model_id: self.enrollment_id ' + str(self.enrollment_id))

        # step-2: get consumer token
        consumer_token = self.consumer.get_token()
        print('step-2: get consumer token: consumer_token: ' + str(consumer_token))

        # step-3: get enrollment instructions
        res = self.get(self.enrollment_id)

        # step-4: record the .wav file
        # this step is independent of the other operations in this method
        # recorded_file_url = record_upload_share

        # step-5: get the endpoint analysis for the recorded .wav file

        hosted_audio_url = 'https://www.dropbox.com/s/uawm0lb0p3zl4nj/enrollment.wav?dl=1'
        a = Analysis(consumer_token, hosted_audio_url, num_words=3, )
        intervals = res.get('intervals')

        # step-6: post the .wav file along with the intervals, complete enrollment
        response = self.update(self.enrollment_id, wav_file=hosted_audio_url, intervals=intervals)
        print(response)


class Analysis(object):

    def __init__(self, token, model, consumer, hosted_audio_url, num_words):
        self.token = token
        self.task_name = None
        self.task_status = None
        self.app_model = model
        self.consumer = consumer
        self.hosted_audio_url = hosted_audio_url
        self.num_words = num_words

    @property
    def payload(self):
        p = {
            "audioUrl": self.hosted_audio_url,
            "words": self.num_words
        }
        return p

    def start_task(self):

        headers = authorization_header(developer_id=self.consumer.consumer_token)
        endpoint_analysis_url = g.config['URL_ANALYSIS']
        response = requests.post(endpoint_analysis_url, json=self.payload, headers=headers)

        if response and response.content:
            result = json.loads(response.content)
            self.task_name = result.get('taskName')
            self.task_name = result.get('taskStatus')
            return result

        return None

    def check_status(self, task_name):
        headers = authorization_header(developer_id=self.consumer.consumer_token)
        # for endpointAnalysis-id-get, the trailing word 'url' needs to be removed
        endpoint_analysis_url = re.sub('url$', str(task_name), g.config['URL_ANALYSIS'])

        response = requests.get(endpoint_analysis_url, headers=headers)

        if response and response.content:
            result = json.loads(response.content)
            return result

        return None

    def execute_step(self):

        result = None
        status_timestamp = None
        status_time_lapse = 0
        try:
            result = self.start_task()
            self.task_name = result.get('taskName')
            self.task_status = result.get('taskStatus')
            status_timestamp = datetime.now()
        except Exception as e:
            print('Analysis start task error:'.format(e))

        try:
            print('task_name: ' + str(self.task_name))
            print('task_status: ' + str(self.task_status))

            while unicode(self.task_status) != u'completed' \
                    and status_time_lapse < float(g.config['REATTEMPT_CALL_FOR']):

                time.sleep(1)
                result = self.check_status(self.task_name)
                self.task_status = result.get('taskStatus')
                status_time_lapse = (datetime.now() - status_timestamp).total_seconds()

        except AttributeError as e:
            print('Analysis check status error {}'.format(e))

        return result


class Consumer(object):

    def __init__(self, token, username, password):
        self.token = token
        self.username = username
        self.password = password
        self.consumer_url = None
        self.consumer_token = None

    @property
    def consumer_id(self):
        if self.consumer_url:
            return h.parse_id_from_href(self.consumer_url)

    @property
    def payload(self):
        p = {
            'username': self.username,
            'password': self.password
        }
        return p

    # TODO: upsert to - create and update
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

        headers = authorization_header()

        url = g.config['URL_CONSUMERS']
        if consumer_id:
            url += '/' + consumer_id

        response = requests.post(url, json=payload, headers=headers)
        self.consumer_url = json.loads(response.content).get('href')

        return self.consumer_id

    def get_consumer(self, consumer_id=None):

        headers = authorization_header()

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
            self.consumer_url = result.get('items')[0].get('href')
        elif result.get('href'):
            print result.get('href')
            self.consumer_url = result.get('href')

        return self.consumer_id

    def get_token(self):
        """ returns consumer specific token based on the given user
        """
        headers = authorization_header()

        try:
            url = g.config['URL_CONSUMERS'] + '/token'

            response = requests.post(url, json=self.payload, headers=headers)
            self.consumer_token = json.loads(response.content).get('token')
            return self.consumer_token

        except Exception as e:
            print('Could not perform the operation: ' + str(e))
            return None


class AppModel(object):

    def __init__(self, token):
        self.token = token
        self.payload = None
        self.app_model_url = None

    @property
    def app_model_id(self):
        if self.app_model_url:
            return h.parse_id_from_href(self.app_model_url)

    def set_payload(self, **kwargs):
        """ Accepts keyword arguments
        """

        mandatory_fields = ['vocabulary', 'verificationLength', 'enrollmentRepeats']
        all_mandatory_fields_present = all([x in kwargs.keys() for x in mandatory_fields])

        if not all_mandatory_fields_present:
            print('Must provide all mandatory fields: ' + str(mandatory_fields))
            return None

        self.payload = kwargs

    def create(self):
        """
        :param
        payload (e.g. format) = {
                "vocabulary": ["boston", "chicago", "pyramid"],
                "verificationLength": 3,
                "enrollmentRepeats": 3
            }
        :return: href for the created or updated app model
        """

        headers = authorization_header()

        url = g.config['URL_APP_MODELS']

        # TODO: try catch
        response = requests.post(url, json=self.payload, headers=headers)
        self.app_model_url = json.loads(response.content).get('href')

        return self.app_model_id

    def update(self, app_model_id=None):
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

        headers = authorization_header()

        url = g.config['URL_APP_MODELS']
        if app_model_id:
            url += '/' + app_model_id

        # TODO: try catch
        response = requests.post(url, json=self.payload, headers=headers)
        self.app_model_url = json.loads(response.content).get('href')

        return self.app_model_id

    def get_app_model(self, app_model_id=None):

        headers = authorization_header()

        url = g.config['URL_APP_MODELS']
        if app_model_id:
            url += '/' + app_model_id

        response = requests.get(url, headers=headers)
        result = json.loads(response.content)
        if result.get('href'):
            self.app_model_url = result.get('href')

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


class Recorder(object):

    def record(self):
        pass

    def upload_and_share(self):
        upload(dropbox_client(), local_file_path='', remote_file_path='')

