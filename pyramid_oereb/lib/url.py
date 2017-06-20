# -*- coding: utf-8 -*-
from urllib import urlencode
from urlparse import urlsplit, urlunsplit, parse_qs, urlparse


def parse_url(url):
    """
    Parse an URL

    Args:
        url (str): The URL

    Returns:
        (urlparse.SplitResult,dict): the parsed URL (SplitResult, params)
    """
    url = urlsplit(url)
    params = parse_qs(url.query)
    return url, params


def add_url_params(url, params):
    """
    Add some parameter to an URL.

    Args:
        url (str): The base URL
        params (dict): The parameters to add

    Returns:
        str: The new URL
    """
    if len(params.items()) == 0:
        return url
    return add_split_url_params(parse_url(url), params)


def add_split_url_params(parsed_url, new_params):
    split_url, params = parsed_url
    query = {}
    query.update(params)
    for key, value in new_params.items():
        if isinstance(key, unicode):
            query[key] = value.encode("utf-8")
        else:
            query[key] = value

    return urlunsplit((
        split_url.scheme, split_url.netloc, split_url.path,
        urlencode(query, doseq=True), split_url.fragment))


def uri_validator(url):
    """
    A simple validator for URL's.
    :param url: The url which should be checked to be valid.
    :type url: str
    :return: The state of the validation.
    :rtype: bool
    """
    result = urlparse(url)
    return True if result.scheme and result.netloc else False
