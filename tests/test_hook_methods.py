# -*- coding: utf-8 -*-

import pytest
import datetime

from shapely.wkt import loads

from pyramid.httpexceptions import HTTPNotFound
from pyramid.testing import DummyRequest

from pyramid_oereb.lib.adapter import FileAdapter
from pyramid_oereb.lib.records.image import ImageRecord
from pyramid_oereb.lib.records.theme import ThemeRecord
from pyramid_oereb.lib.records.view_service import LegendEntryRecord
from pyramid_oereb.lib.records.real_estate import RealEstateRecord
from pyramid_oereb.standard.hook_methods import get_symbol, get_symbol_ref, get_surveying_data_update_date
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
        'theme_code': 'ch.BelasteteStandorte',
        'view_service_id': '1',
        'type_code': 'missing'
    })
    with pytest.raises(HTTPNotFound):
        get_symbol(request)


def test_get_symbol():
    request = DummyRequest()
    request.matchdict.update({
        'theme_code': 'ch.BelasteteStandorte',
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
        ThemeRecord('ch.BelasteteStandorte', {'de': 'Belastete Standorte'}, 410),
        view_service_id='1'
    )
    with pyramid_oereb_test_config():
        request = DummyRequest()
        url = urlparse(get_symbol_ref(request, record))
        assert url.path == '/image/symbol/ch.BelasteteStandorte/1/CodeA.png'


def test_get_surveying_data_date():
    real_estate = RealEstateRecord('test_type', 'BL', 'Nusshof', 1, 100,
                                   loads('POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))'))
    with pyramid_oereb_test_config():
        update_date_os = get_surveying_data_update_date(real_estate)
        assert isinstance(update_date_os, datetime.datetime)
