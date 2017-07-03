# -*- coding: utf-8 -*-
import base64
from urllib import urlencode
from urllib2 import urlopen, URLError
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

    Args:
        url (str): The url which should be checked to be valid.

    Returns:
        bool: The state of the validation.
    """
    result = urlparse(url)
    return True if result.scheme and result.netloc else False


def url_to_base64(url):
    """
    Request the document at the given url and return it as a base64 document.

    Args:
        url (str): url to request and deliver as base64 document.

    Returns:
        base64 or str: the document as base64 string or None on errors
    """
    response = None
    if url:
        try:
            response = urlopen(url)
        except URLError as e:
            raise LookupError(e)

    return None if response is None else base64.b64encode(response.read())
