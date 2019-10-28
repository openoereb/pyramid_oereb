# -*- coding: utf-8 -*-

import pytest

from pyramid.httpexceptions import HTTPNotFound
from pyramid.testing import DummyRequest

from pyramid_oereb.lib.adapter import FileAdapter
from pyramid_oereb.lib.records.image import ImageRecord
from pyramid_oereb.lib.records.theme import ThemeRecord
from pyramid_oereb.lib.records.view_service import LegendEntryRecord
from pyramid_oereb.standard.hook_methods import get_symbol, get_symbol_ref
from tests import pyramid_oereb_test_config

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


def test_get_symbol_invalid_theme_code():
    request = DummyRequest()
    request.matchdict.update({
        'theme_code': 'InvalidThemeCode',
        'view_service_id': '1',
        'type_code': 'CodeA'
    })
    with pytest.raises(HTTPNotFound):
        get_symbol(request)


def test_get_symbol_not_found():
    request = DummyRequest()
    request.matchdict.update({
        'theme_code': 'ContaminatedSites',
        'view_service_id': '1',
        'type_code': 'missing'
    })
    with pytest.raises(HTTPNotFound):
        get_symbol(request)


def test_get_symbol():
    request = DummyRequest()
    request.matchdict.update({
        'theme_code': 'ContaminatedSites',
        'view_service_id': '1',
        'type_code': 'CodeA'
    })
    response = get_symbol(request)
    assert response.body == FileAdapter().read('tests/resources/symbol.png')


def test_get_symbol_ref():
    record = LegendEntryRecord(
        ImageRecord(FileAdapter().read('tests/resources/logo_canton.png')),
        {'de': 'Test'},
        'CodeA',
        'http://my.codelist.com/test.xml',
        ThemeRecord('ContaminatedSites', {'de': 'Belastete Standorte'}),
        view_service_id='1'
    )
    with pyramid_oereb_test_config():
        request = DummyRequest()
        url = urlparse(get_symbol_ref(request, record))
        assert url.path == '/image/symbol/ContaminatedSites/1/CodeA.png'
