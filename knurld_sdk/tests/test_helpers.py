# -*- coding: utf-8 -*-
import unittest

from knurld_sdk import helpers as h


class TestHelpers(unittest.TestCase):

    sample_response = {'href': 'https://api.knurld.io/v1/app-models/bfd6574b6388a249e386157f3a004b0c'}

    def test_parse_response(self):

        href = h.parse_response(self.sample_response, get_field='href')
        self.assertRegexpMatches(href, h.regx_pattern_url())


if __name__ == '__main__':
    unittest.main()
