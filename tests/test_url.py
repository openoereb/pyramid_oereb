# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.url import uri_validator


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
