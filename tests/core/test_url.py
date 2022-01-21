# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.core.url import uri_validator, parse_url


@pytest.mark.parametrize('uri', [
    'https://geoview.bl.ch',
    'http://geoview.bl.ch',
    'https://google.ch'
])
def test_uri_validator_correct_uris(uri):
    assert uri_validator(uri)


@pytest.mark.parametrize('uri', [
    'geoview',
    'google.de'
])
def test_uri_validator_incorrect_uris(uri):
    assert not uri_validator(uri)


@pytest.fixture
def url_sample():
    return ("https://my.test.address.ch/entry_point?lowercase_param=foo"
            "&mixedCaseParam=bar"
            "&UPPER_CASE_PARAM=bla"
            "&encoded_param=specials%3A+%2F-%3B")


@pytest.fixture
def expected_url_param_dict():
    return {
        "lowercase_param": ["foo"],
        "mixedCaseParam": ["bar"],
        "UPPER_CASE_PARAM": ["bla"],
        "encoded_param": ["specials: /-;"]
    }


def test_parse_url(url_sample, expected_url_param_dict):
    url, params = parse_url(url_sample, force_uppercase_keys=False)
    assert params == expected_url_param_dict


def test_parse_url_uppercase(url_sample, expected_url_param_dict):
    url, params = parse_url(url_sample)
    for k, v in expected_url_param_dict.items():
        assert params[k.upper()] == v
