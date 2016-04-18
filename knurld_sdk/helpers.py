# -*- coding: utf-8 -*-

import json


class DummyData(object):
    enrollment_wav = 'https://www.dropbox.com/s/yk8fuesv3dyrk07/_standalone_4d6713e1-0588-11e6-8a73-f45c89aa5c97enrollment.wav?dl=1'
    invalid_enrollment_wav = 'http://www.dropbox.com/s/33k10x2vuhhlutt/enrollment_test_solo.wav?dl=0'
    # make sure that the start and stop time intervals are at least 600 milliseconds apart
    intervals = [
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

    incorrect_intervals = [
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


def parse_id_from_href(href):
    """ returns the trailing part of a typical 'href' field from knurld API response json
    """

    if href:
        return str(href.split('/')[-1])
    return None


def parse_response(response, get_field=None):
    """ convert response to JSON format parse requested fields from the response object
     received from calls to various APIs
    :param response: dict
    :param get_field: a specific field from the json object
    """

    try:
        # jsonify the response object
        response = json.loads(response)

        # if there is ont=ly one item in the response
        href = response.get('href')
        if get_field == 'href':
            return href

    except (ValueError, AttributeError) as e:
        print('Could not parse from the given response object: ' + str(e))

    return None


def regx_pattern_id(count=32):
    # pattern that matches both type of tokens (admin/consumer)
    return r'(\w|\.|-){' + str(count) + r'}'


def regx_pattern_url():
    # pattern that matches a typical url returned in the response json
    return r'https:.*'
