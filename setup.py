# -*- coding: utf-8 -*-
"""
# Copyright 2016 Intellisis Inc.  All rights reserved.
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file
"""

from setuptools import setup


with open('knurld_sdk/requirements.txt') as f:
    knurld_sdk_requirements = f.read().splitlines()

setup(name='knurld_sdk',
      version='release-v1.0.0',
      description='Python wrapper for knurld.io REST API',
      url='https://github.com/knurld/Python-SDK',
      author='Rohan Bakare',
      author_email='rbakare@knurld.com',
      license='https://github.com/knurld/Python-SDK/blob/master/LICENSE',
      packages=['knurld_sdk'],
      zip_safe=False,
      install_requires=knurld_sdk_requirements,  # includes all the dependencies while installation
      test_suite='nose.collector',
      tests_require=['nose'],
      include_package_data=True     # allows data files as part of the distribution via MANIFEST.in
      )
