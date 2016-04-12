# -*- coding: utf-8 -*-

import json


def get_response_content(response):
    """ otherwise a boilerplate code that checks if the response has content and returns it
    """
    if response and response.content:
        return response.content

    return None


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
