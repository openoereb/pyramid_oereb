# -*- coding: utf-8 -*-

import pytest

from pyramid.httpexceptions import HTTPNotFound
from pyramid.testing import DummyRequest
from pyramid_oereb.lib.records.image import ImageRecord
from pyramid_oereb.lib.records.theme import ThemeRecord
from pyramid_oereb.lib.records.view_service import LegendEntryRecord
from pyramid_oereb.standard.hook_methods import get_symbol, get_symbol_ref
from tests.conftest import pyramid_oereb_test_config

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


def test_get_symbol_invalid_theme_code(config):
    assert isinstance(config._config, dict)
    request = DummyRequest()
    request.matchdict.update({
        'theme_code': 'InvalidThemeCode',
        'type_code': 'test'
    })
    with pytest.raises(HTTPNotFound):
        get_symbol(request)


def test_get_symbol_not_found(config):
    assert isinstance(config._config, dict)
    request = DummyRequest()
    request.matchdict.update({
        'theme_code': 'ContaminatedSites',
        'type_code': 'missing'
    })
    with pytest.raises(HTTPNotFound):
        get_symbol(request)


def test_get_symbol(config):
    assert isinstance(config._config, dict)
    request = DummyRequest()
    request.matchdict.update({
        'theme_code': 'ContaminatedSites',
        'type_code': 'test'
    })
    response = get_symbol(request)
    assert response.body.decode('utf-8') == '1'


def test_get_symbol_ref(config):
    assert isinstance(config._config, dict)
    record = LegendEntryRecord(
        ImageRecord('1'.encode('utf-8')),
        {'de': 'Test'},
        'test',
        'http://my.codelist.com/test.xml',
        ThemeRecord('ContaminatedSites', {'de': 'Belastete Standorte'})
    )
    with pyramid_oereb_test_config():
        request = DummyRequest()
        url = urlparse(get_symbol_ref(request, record))
        assert url.path == '/image/symbol/ContaminatedSites/test'
