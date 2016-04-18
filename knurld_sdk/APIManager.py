# -*- coding: utf-8 -*-

import json
import re
import requests
import time
from datetime import datetime

from knurld_sdk import app_globals as g
from knurld_sdk import helpers as h
from knurld_sdk.uploader.Dropbox import upload, share, dropbox_client
from knurld_sdk.CustomExceptions import ImproperArgumentsException


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

    def __init__(self, token, app_model_id, consumer_id):
        self.token = token
        self.app_model_id = app_model_id
        self.consumer_id = consumer_id
        self.enrollment_url = None

    @property
    def enrollment_id(self):
        return h.parse_id_from_href(self.enrollment_url)

    @property
    def payload(self):
        p = {
            "application": self.app_model_id,
            "consumer": self.consumer_id
        }
        return p

    def create(self):
        """ create the enrollment using an app-model and consumer
        """
        headers = authorization_header()

        try:
            url = g.config['URL_ENROLLMENTS']

            response = requests.post(url, json=self.payload, headers=headers)
            if response.status_code == 201:
                result = json.loads(response.content)
                self.enrollment_url = result.get('href')
                return self.enrollment_id
            else:
                return response.status_code, response.content

        except Exception as e:
            print('Could not perform the operation: ' + str(e))
            return None

    def update(self, enrollment_id, payload_update):
        """ update existing app-model with a payload containing wav_file and/or intervals
        """
        # TODO: could change this to use the consumer specific tokens in the future, with developer_id param
        headers = authorization_header()

        try:
            url = g.config['URL_ENROLLMENTS'] + '/' + enrollment_id
            response = requests.post(url, json=payload_update, headers=headers)

            if response.status_code == 202:
                result = json.loads(response.content)
                self.enrollment_url = result.get('href')
                return self.enrollment_id
            else:
                return response.status_code, response.content

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
            if response.status_code == 200:
                result = json.loads(response.content)
                self.enrollment_url = result.get('href')
                return result
            else:
                return response.status_code, response.content

        except Exception as e:
            print('Could not perform the operation: ' + str(e))
            return None

    @staticmethod
    def get_all(start=0, end=10, offset=10):
        """ return all the enrollments for given offset, start, end
            TODO: the proper usage of parameters
        """
        headers = authorization_header()

        try:
            url = g.config['URL_ENROLLMENTS']

            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                result = json.loads(response.content)
                return result
            else:
                # TODO: log errors
                print(response.status_code)
                print(response.content)
                return response.status_code, response.content

        except Exception as e:
            print('Could not perform the operation: ' + str(e))
            return None

    def steps(self, payload_update):

        # step-1: put consumer_id, model_id then the self.enrollment_id will be set automatically upon successful create
        _ = self.create()
        print('step-1: create: put consumer_id, model_id: self.enrollment_id ' + str(self.enrollment_id))

        # step-2: get consumer token, to be used instead of the admin token in the header
        # consumer_token = self.consumer.get_token()
        # print('step-2: get consumer token: consumer_token: ' + str(consumer_token))

        # step-3: get enrollment instructions
        instructions = self.get(self.enrollment_id)
        print('Follow these instructions to Enroll properly: ' + str(instructions))

        # step-4: record the .wav file - this should now be the part of the payload_update passed to this method
        # this step is independent of the other operations in this method
        # recorded_file_url = record_upload_share

        # step-5: get the endpoint analysis for the recorded .wav file
        # try:
        #    payload_update['audioUrl'] = payload_update.pop('enrollment.wav')
        # except KeyError as e:
        #    print("Your payload update must have 'enrollment.wav' key having a recorded file url as its value.")
        #    return None

        # a = Analysis(self.token, self.app_model_id, self.consumer_id, payload=payload_update)
        # task_name = a.start_task()
        # completed_task_name = a.check_status(task_name)
        # intervals = instructions.get('intervals')

        # build the intervals for enrollment

        # step-6: post the .wav file along with the intervals, complete enrollment
        response = self.update(self.enrollment_id, payload_update=payload_update)
        print(response)
        return response


class Analysis(object):

    def __init__(self, token, model_id, consumer_id, payload=None):
        self.token = token
        self.model_id = model_id
        self.consumer_id = consumer_id
        if payload:
            # read-only objects do not need to set the payload
            self.payload = self.set_payload(payload)
        self.task_name = None
        self.task_status = None

    def set_payload(self, kwargs):
        """ setter method for attribute payload which validates and stores parameters for creating Analysis Endpoint
        :param kwargs: the parameters you want to set to while creating analysis endpoint
        """

        mandatory_fields = ['audioUrl']
        all_mandatory_fields_present = all([x in kwargs.keys() for x in mandatory_fields])

        try:
            if not all_mandatory_fields_present:
                error_text = 'Must provide all mandatory fields: ' + str(mandatory_fields)
                raise ImproperArgumentsException(error_text)
        except ImproperArgumentsException as e:
            print('Error while creating app model. ' + str(e))
            return None

        self.payload = kwargs
        return self.payload

    def start_task(self):
        """ starts the analysis process on the supplied .wav file, and returns the task_name (unique-id)
        """
        # could change this to use the consumer specific tokens in the future, with developer_id param
        headers = authorization_header()

        try:
            endpoint_analysis_url = g.config['URL_ANALYSIS']
            response = requests.post(endpoint_analysis_url, json=self.payload, headers=headers)
            if response and response.status_code == 200:
                result = json.loads(response.content)
                self.task_name = result.get('taskName')
                self.task_name = result.get('taskStatus')
                return result
            else:
                return response.status_code, response.content
        except Exception as e:
            print('Could not perform the operation: ' + str(e))
            return None

    @staticmethod
    def check_status(task_name):
        """ returns the current status of an already started task
        """
        # could change this to use the consumer specific tokens in the future, with developer_id param
        headers = authorization_header()

        try:
            # for endpointAnalysis-id-get, the trailing word 'url' needs to be removed
            endpoint_analysis_url = re.sub(r'url$', str(task_name), g.config['URL_ANALYSIS'])
            response = requests.get(endpoint_analysis_url, headers=headers)

            if response and response.content:
                result = json.loads(response.content)
                return result
            else:
                return response.status_code, response.content

        except Exception as e:
            print('Could not perform the operation: ' + str(e))
            return None

    def execute_step(self):
        """ combines both start_task and the check_status methods, if the status is not complete it re-attempts for
        n number of seconds indicated by REATTEMPT_ANALYSIS_CALL_FOR config option
        ideally should return the task_name in the result with a task_status as 'completed'
        """
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
                    and status_time_lapse < float(g.config['REATTEMPT_ANALYSIS_CALL_FOR']):

                time.sleep(0.01)
                result = self.check_status(self.task_name)
                self.task_status = result.get('taskStatus')
                status_time_lapse = (datetime.now() - status_timestamp).total_seconds()

        except AttributeError as e:
            print('Analysis check status error {}'.format(e))

        return result


class Consumer(object):

    def __init__(self, token, payload=None):
        self.token = token
        if payload:
            # read-only objects do not need to set the payload
            self.payload = self.set_payload(payload)
        self.consumer_url = None
        self.consumer_token = None

    @property
    def consumer_id(self):
        if self.consumer_url:
            return h.parse_id_from_href(self.consumer_url)

    def set_payload(self, kwargs):
        """ setter method for attribute payload which validates and stores parameters while creating the consumer
        :param kwargs: the parameters you want to set to while creating a consumer
        """

        mandatory_fields = ['username', 'password', 'gender']
        all_mandatory_fields_present = all([x in kwargs.keys() for x in mandatory_fields])

        try:
            if not all_mandatory_fields_present:
                error_text = 'Must provide all mandatory fields: ' + str(mandatory_fields)
                raise ImproperArgumentsException(error_text)
        except ImproperArgumentsException as e:
            print('Error while creating app model. ' + str(e))
            return None

        self.payload = kwargs
        return self.payload

    def create(self):
        """
        create the app model
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

        try:
            url = g.config['URL_CONSUMERS']

            response = requests.post(url, json=self.payload, headers=headers)
            if response.status_code == 201:
                self.consumer_url = json.loads(response.content).get('href')
                return self.consumer_id
            else:
                return response.status_code, response.content

        except Exception as e:
            print('Could not perform the operation: ' + str(e))
            return None

    def update(self, consumer_id, payload_override=None):
        """
        update the app model's password field. Note: username and the gender are non editable fields
        :param
        payload (e.g. format) = {
            "password": "walcott360"
        }
        consumer_id: an existing consumer_id
        :return: href for the created or updated consumer
        """

        headers = authorization_header()

        try:
            url = g.config['URL_CONSUMERS'] + '/' + consumer_id

            if payload_override:
                self.payload = payload_override

            response = requests.post(url, json=self.payload, headers=headers)
            if response.status_code == 202:
                self.consumer_url = json.loads(response.content).get('href')
                return self.consumer_id
            else:
                return response.status_code, response.content

        except Exception as e:
            print('Could not perform the operation: ' + str(e))
            return None

    def get(self, consumer_id):

        headers = authorization_header()

        try:
            url = g.config['URL_CONSUMERS'] + '/' + consumer_id

            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                result = json.loads(response.content)
                if result.get('href'):
                    self.consumer_url = result.get('href')
            else:
                # TODO: log errors
                print(response.status_code)
                print(response.content)
                return response.status_code, response.content

        except Exception as e:
            print('Could not perform the operation: ' + str(e))
            return None

        return result

    @staticmethod
    def get_all(offset=None):

        headers = authorization_header()

        try:
            url = g.config['URL_CONSUMERS']

            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                result = json.loads(response.content)
                return result
            else:
                # TODO: log errors
                print(response.status_code)
                print(response.content)
                return response.status_code, response.content

        except Exception as e:
            print('Could not perform the operation: ' + str(e))
            return None

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
    """ The application model class that wraps Knurld API resources for application models
    Endpoint: https://api.knurld.io/v1/app-models
    """

    def __init__(self, token, payload=None):
        self.token = token
        if payload:
            # read-only objects do not need to set the payload
            self.payload = self.set_payload(payload)
        self.app_model_url = None

    @property
    def app_model_id(self):
        if self.app_model_url:
            return h.parse_id_from_href(self.app_model_url)

    def set_payload(self, kwargs):
        """ setter method for attribute payload which validates and stores parameters for app model creation
        :param kwargs: the parameters you want to set to while creating an app model
        """
        mandatory_fields = ['vocabulary', 'verificationLength', 'enrollmentRepeats']
        all_mandatory_fields_present = all([x in kwargs.keys() for x in mandatory_fields])

        try:
            if not all_mandatory_fields_present:
                error_text = 'Must provide all mandatory fields: ' + str(mandatory_fields)
                raise ImproperArgumentsException(error_text)
        except ImproperArgumentsException as e:
            print('Error while creating app model. ' + str(e))
            return None

        self.payload = kwargs
        return self.payload

    def create(self):
        """ create an app model using this method. Uses the payload dictionary set during object initialization
        """
        headers = authorization_header()
        try:
            url = g.config['URL_APP_MODELS']

            response = requests.post(url, json=self.payload, headers=headers)
            if response.status_code == 201:
                self.app_model_url = json.loads(response.content).get('href')
                return self.app_model_id
            else:
                return response.status_code, response.content

        except Exception as e:
            print('Could not perform the operation: ' + str(e))
            return None

    def update(self, app_model_id, payload_override=None):
        """ update an app model using this method. Uses the payload dictionary set during object initialization
        :param app_model_id: existing app model id
        :param payload_override: a complete new payload developer might want to set
        """
        headers = authorization_header()
        try:
            url = g.config['URL_APP_MODELS'] + '/' + app_model_id
            if payload_override:
                self.payload = payload_override

            response = requests.post(url, json=self.payload, headers=headers)
            if response.status_code == 202:
                self.app_model_url = json.loads(response.content).get('href')
                return self.app_model_id
            else:
                # TODO: log errors
                print(response.status_code)
                print(response.content)
                return response.status_code, response.content

        except Exception as e:
            print('Could not perform the operation: ' + str(e))
            return None

    def get(self, app_model_id):
        """ get an app model associated with a particular app_model_id.
        """

        headers = authorization_header()

        try:
            url = g.config['URL_APP_MODELS'] + '/' + app_model_id

            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                result = json.loads(response.content)
                if result.get('href'):
                    self.app_model_url = result.get('href')
            else:
                # TODO: log errors
                print(response.status_code)
                print(response.content)
                return response.status_code, response.content

        except Exception as e:
            print('Could not perform the operation: ' + str(e))
            return None

        return result

    @staticmethod
    def get_all(offset=None):
        """ get a range of available app models
        TODO: provide pagination using offsets
        """
        headers = authorization_header()
        try:
            url = g.config['URL_APP_MODELS']

            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                result = json.loads(response.content)
            else:
                return response.status_code, response.content

        except Exception as e:
            print('Could not perform the operation: ' + str(e))
            return None

        return result

    def delete(self):
        pass


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

