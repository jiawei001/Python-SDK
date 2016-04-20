# -*- coding: utf-8 -*-


class DummyData(object):

    enrollment_wav = 'https://www.dropbox.com/s/q0qgr45mzc0bllj/' \
                     '_standalone_e9b14380-05b3-11e6-9b42-f45c89aa5c97enrollment.wav?dl=1'

    verification_wav_files = {
        "boston_chicago_pyramid.wav": {
            "shared_url": 'https://www.dropbox.com/s/pwy9j5kqhhxvw26/'
                          '_standalone_2074860f-0727-11e6-9ee8-f45c89aa5c97verification.wav?dl=1',
            "intervals": [
                {u'phrase': 'boston', u'start': 1082, u'stop': 1983},
                {u'phrase': 'chicago', u'start': 2443, u'stop': 3403},
                {u'phrase': 'pyramid', u'start': 4163, u'stop': 4813}
            ]
        },
        "chicago_boston_pyramid.wav": {
            "shared_url": 'https://www.dropbox.com/s/6ib49b41f0scke5/'
                          '_standalone_32a66799-0727-11e6-a660-f45c89aa5c97verification.wav?dl=1',
            "intervals": [
                {u'phrase': 'chicago', u'start': 1082, u'stop': 1902},
                {u'phrase': 'boston', u'start': 2503, u'stop': 3353},
                {u'phrase': 'pyramid', u'start': 4083, u'stop': 4752}
            ]
        },
        "pyramid_boston_chicago.wav": {
            "shared_url": 'https://www.dropbox.com/s/kkf3r2lutd6z9j6/'
                          '_standalone_3d87ed26-0727-11e6-b52c-f45c89aa5c97verification.wav?dl=1',
            "intervals": [
                {u'phrase': 'pyramid', u'start': 1152, u'stop': 2072},
                {u'phrase': 'boston', u'start': 2433, u'stop': 3263},
                {u'phrase': 'chicago', u'start': 3953, u'stop': 4743}
            ]
        }
    }

    invalid_enrollment_wav = 'http://www.dropbox.com/s/33k10x2vuhhlutt/enrollment_test_solo.wav?dl=0'

    # make sure that the start and stop time intervals are at least 600 milliseconds apart
    enrollment_intervals = [
        {
            "phrase": "boston",
            "start": 822,
            "stop": 1432
        },
        {
            "phrase": "boston",
            "start": 2042,
            "stop": 2672
        },
        {
            "phrase": "boston",
            "start": 3032,
            "stop": 3912
        },
        {
            "phrase": "chicago",
            "start": 4652,
            "stop": 5612
        },
        {
            "phrase": "chicago",
            "start": 6012,
            "stop": 6702
        },
        {
            "phrase": "chicago",
            "start": 6822,
            "stop": 7552
        },
        {
            "phrase": "pyramid",
            "start": 8402,
            "stop": 9032
        },
        {
            "phrase": "pyramid",
            "start": 9402,
            "stop": 10042
        },
        {
            "phrase": "pyramid",
            "start": 10382,
            "stop": 11002
        }
    ]

    invalid_enrollment_intervals = [
        {
            "phrase": "boston",
            "start": 892,   # this is not 600 milliseconds apart, hence non-acceptable
            "stop": 1432
        },
        {
            "phrase": "boston",
            "start": 2042,
            "stop": 2572
        },
        {
            "phrase": "boston",
            "start": 3032,
            "stop": 3912
        },
        {
            "phrase": "chicago",
            "start": 4652,
            "stop": 5612
        },
        {
            "phrase": "chicago",
            "start": 6012,
            "stop": 6702
        },
        {
            "phrase": "chicago",
            "start": 6822,
            "stop": 7552
        },
        {
            "phrase": "pyramid",
            "start": 8402,
            "stop": 9032
        },
        {
            "phrase": "pyramid",
            "start": 9402,
            "stop": 10042
        },
        {
            "phrase": "pyramid",
            "start": 10382,
            "stop": 11002
        }
    ]


def merge_intervals_with_phrases(vocabulary, repetitions, intervals):

    def _next_word():
        """ a generator that returns a word from vocabulary repeated to given number of repetitions
        """
        i = 0
        while i < len(vocabulary):
            for r in range(repetitions):
                yield vocabulary[i]
            i += 1

    # make the list using the generator: _next_word()
    words_per_interval = list(_next_word())

    try:
        for interval, word in zip(intervals, words_per_interval):
            interval["phrase"] = word
    except ValueError as e:
        print("Unmatched number of intervals vs phrases." + str(e))

    return intervals


def parse_id_from_href(href):
    """ returns the trailing part of a typical 'href' field from knurld API response json
    """

    if href:
        return str(href.split('/')[-1])
    return None


def regx_pattern_id(count=32):
    # pattern that matches both type of tokens (admin/consumer)
    return r'(\w|\.|-){' + str(count) + r'}'


def regx_pattern_url():
    # pattern that matches a typical url returned in the response json
    return r'https:.*'
