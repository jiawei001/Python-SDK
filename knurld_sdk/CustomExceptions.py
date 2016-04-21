# -*- coding: utf-8 -*-
"""
# Copyright 2016 Intellisis Inc.  All rights reserved.
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file
"""

class ImproperArgumentsException(Exception):

    def __init__(self, error_text=None):
        error = Exception.__init__(self, error_text)
        print(error)

