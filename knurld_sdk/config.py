# -*- coding: utf-8 -*-
import json
import os


class Configuration(object):

    def __init__(self, max_expiration_time=3599):  # as per the APIs after every 3599 seconds current token expires
        self._config = None
        self._max_expiration_time = max_expiration_time
        self._app_root = None

    @property
    def app_root(self):
        try:
            self._app_root = os.path.dirname(os.path.abspath(__file__))
        except IOError as e:
            print('Unable to set APP_ROOT {}'.format(e))

        return self._app_root

    @property
    def config(self):
        try:
            with open(str(self.app_root) + '/config.cfg', 'r+') as cf:
                content = cf.read().replace('\r\n', '')
                self._config = json.loads(content)

                # Do the type checks and set appropriate types
                self._config['TOKEN_EXPIRES'] = float(self._config['TOKEN_EXPIRES'])

                # if the Token Expire time is greater than max allowable duration then reset it to max
                if self._config['TOKEN_EXPIRES'] > self._max_expiration_time:
                    self._config['TOKEN_EXPIRES'] = self._max_expiration_time

        except ValueError as e:
            print('Could not load the configuration! {}'.format(e))

        return self._config
