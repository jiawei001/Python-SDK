# -*- coding: utf-8 -*-
"""
# Copyright 2016 Intellisis Inc.  All rights reserved.
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file
"""

from dogpile.cache import make_region

from knurld_sdk.config import Configuration

c = Configuration()
config = c.config
app_root = str(c.app_root)

region = make_region().configure('dogpile.cache.memory',
                                 expiration_time=config['TOKEN_EXPIRES'],
                                 )
