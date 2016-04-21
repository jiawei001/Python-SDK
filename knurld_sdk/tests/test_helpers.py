# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from knurld_sdk import helpers as h


class TestHelpers(unittest.TestCase):

    def test_merge_intervals_with_phrases(self):
        vocabulary = [u'boston', u'chicago', u'pyramid']
        repetitions = 3
        # need deepcopy of the object as we need to make sure not to modify the original intervals
        expected_intervals = deepcopy(h.DummyData.enrollment_intervals)
        # for testing purposes, removing key 'phrase' from the intervals we have
        test_intervals = filter(lambda x: x.pop('phrase'), deepcopy(h.DummyData.enrollment_intervals))

        merged_intervals = h.merge_intervals_with_phrases(vocabulary, repetitions, test_intervals)
        self.assertEqual(merged_intervals, expected_intervals)


if __name__ == '__main__':
    unittest.main()
