# -*- coding: utf-8 -*-

import pytest
import datetime

from shapely.wkt import loads
from unittest.mock import patch

from pyramid.httpexceptions import HTTPNotFound
from pyramid.testing import DummyRequest

from pyramid_oereb.core import b64
from pyramid_oereb.core.adapter import FileAdapter
from pyramid_oereb.core.records.image import ImageRecord
from pyramid_oereb.core.records.theme import ThemeRecord
from pyramid_oereb.core.records.view_service import LegendEntryRecord
from pyramid_oereb.core.records.real_estate import RealEstateRecord
from pyramid_oereb.contrib.data_sources.standard.hook_methods import get_symbol, get_symbol_ref, \
    get_surveying_data_update_date
from pyramid_oereb.contrib.data_sources.standard.sources.plr import StandardThemeConfigParser
import pyramid_oereb.contrib.data_sources.standard.hook_methods

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


@pytest.fixture
def legend_entry_data(pyramid_oereb_test_config, dbsession, transact, file_adapter):
    del transact
    theme_config = pyramid_oereb_test_config.get_theme_config_by_code('ch.BelasteteStandorte')
    config_parser = StandardThemeConfigParser(**theme_config)
    models = config_parser.get_models()

    view_services = {
        models.ViewService(**{
            'id': 1,
            'reference_wms': 'http://www.example.com',
            'layer_index': 1,
            'layer_opacity': 1.0,
        })
    }
    dbsession.add_all(view_services)

    legend_entries = [
        models.LegendEntry(**{
            'id': '1',
            'symbol': b64.encode(file_adapter.read('tests/resources/symbol.png')),
            'legend_text': 'Test',
            'type_code': 'CodeA',
            'type_code_list': 'type_code_list',
            'theme': 'ch.BelasteteStandorte',
            'view_service_id': '1'
        })
    ]
    dbsession.add_all(legend_entries)
    dbsession.flush()

    yield legend_entries


def test_get_symbol_invalid_theme_code(pyramid_oereb_test_config):
    request = DummyRequest()
    request.matchdict.update({
        'theme_code': 'InvalidThemeCode',
        'view_service_id': '1',
        'type_code': 'CodeA'
    })
    with pytest.raises(HTTPNotFound):
        get_symbol(request)


def test_get_symbol_not_found(pyramid_oereb_test_config):
    request = DummyRequest()
    request.matchdict.update({
        'theme_code': 'ch.BelasteteStandorte',
        'view_service_id': '1',
        'type_code': 'missing'
    })
    with pytest.raises(HTTPNotFound):
        get_symbol(request)


def test_get_symbol(pyramid_oereb_test_config, legend_entry_data):
    request = DummyRequest()
    request.matchdict.update({
        'theme_code': 'ch.BelasteteStandorte',
        'view_service_id': '1',
        'type_code': 'CodeA'
    })
    response = get_symbol(request)
    assert response.body == FileAdapter().read('tests/resources/symbol.png')


@patch.object(pyramid_oereb.contrib.data_sources.standard.hook_methods, 'route_prefix', 'oereb')
def test_get_symbol_ref(pyramid_test_config):
    record = LegendEntryRecord(
        ImageRecord(FileAdapter().read('tests/resources/logo_canton.png')),
        {'de': 'Test'},
        'CodeA',
        'http://my.codelist.com/test.xml',
        ThemeRecord('ch.BelasteteStandorte', {'de': 'Belastete Standorte'}, 410),
        view_service_id='1'
    )
    request = DummyRequest()
    url = urlparse(get_symbol_ref(request, record))
    assert url.path == '/image/symbol/ch.BelasteteStandorte/1/CodeA.png'


def test_get_surveying_data_date():
    real_estate = RealEstateRecord('test_type', 'BL', 'Nusshof', 1, 100,
                                   loads('POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))'))
    update_date_os = get_surveying_data_update_date(real_estate)
    assert isinstance(update_date_os, datetime.datetime)
