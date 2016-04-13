# -*- coding: utf-8 -*-


class ImproperArgumentsException(Exception):

    def __init__(self, error_text=None):
        error = Exception.__init__(self, error_text)
        print(error)

