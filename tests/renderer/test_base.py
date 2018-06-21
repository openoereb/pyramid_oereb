# -*- coding: utf-8 -*-

import pytest
import datetime

from pyramid.httpexceptions import HTTPServerError
from pyramid.response import Response
from pyramid.testing import DummyRequest

from pyramid_oereb.lib.records.image import ImageRecord
from pyramid_oereb.lib.records.theme import ThemeRecord
from pyramid_oereb.lib.records.view_service import LegendEntryRecord
from pyramid_oereb.lib.renderer import Base
from pyramid_oereb.lib.renderer.extract.json_ import Renderer
from tests.conftest import MockRequest, pyramid_oereb_test_config
from tests.renderer import DummyRenderInfo


def test_call():
    renderer = Base(DummyRenderInfo())
    assert isinstance(renderer.info, DummyRenderInfo)
    assert renderer.info.name == 'test'


@pytest.mark.parametrize('input,result', [
    (datetime.date.today(), datetime.date.today().strftime('%Y-%m-%dT%H:%M:%S')),
    ('test', 'test')
])
def test_date_time(input, result):
    assert Base.date_time(input) == result


def test_get_request():
    request = Base.get_request({
        'request': DummyRequest()
    })
    assert isinstance(request, DummyRequest)


def test_get_missing_request():
    request = Base.get_request({})
    assert request is None


def test_get_response():
    response = Base.get_response({
        'request': DummyRequest()
    })
    assert isinstance(response, Response)


def test_get_missing_response():
    response = Base.get_response({})
    assert response is None


def test_get_localized_text_from_string(config):
    assert isinstance(config._config, dict)
    renderer = Renderer(DummyRenderInfo())
    localized_text = renderer.get_localized_text('Test')
    assert isinstance(localized_text, dict)
    assert localized_text.get('Text') == 'Test'
    assert localized_text.get('Language') == config.get('default_language')


@pytest.mark.parametrize('language,result', [
    ('de', u'Dies ist ein Test'),
    ('en', u'This is a test'),
    ('fr', u'Dies ist ein Test')  # fr not available; use default language (de)
])
def test_get_localized_text_from_dict(config, language, result):
    assert isinstance(config._config, dict)
    renderer = Renderer(DummyRenderInfo())
    renderer._language = language
    multilingual_text = {
        'de': u'Dies ist ein Test',
        'en': u'This is a test'
    }
    localized_text = renderer.get_localized_text(multilingual_text)
    assert isinstance(localized_text, dict)
    assert localized_text.get('Language') in ['de', 'en']
    assert localized_text.get('Text') == result


@pytest.mark.parametrize('language,result', [
    ('de', u'Dies ist ein Test'),
    ('en', u'This is a test'),
    ('fr', u'Dies ist ein Test')  # fr not available; use default language (de)
])
def test_get_multilingual_text_from_dict(config, language, result):
    assert isinstance(config._config, dict)
    renderer = Renderer(DummyRenderInfo())
    renderer._language = language
    multilingual_text = {
        'de': u'Dies ist ein Test',
        'en': u'This is a test'
    }
    ml_text = renderer.get_multilingual_text(multilingual_text)
    assert isinstance(ml_text, list)
    assert len(ml_text) == 1
    assert ml_text[0].get('Language') in ['de', 'en']
    assert ml_text[0].get('Text') == result


@pytest.mark.parametrize('theme_code', [
    u'ContaminatedSites',
    u'NotExistingTheme',
])
def test_get_symbol_ref(config, theme_code):
    assert isinstance(config._config, dict)
    with pyramid_oereb_test_config():
        request = MockRequest()
        record = LegendEntryRecord(
            ImageRecord('1'.encode('utf-8')),
            {'de': 'Test'},
            u'test',
            u'test',
            ThemeRecord(theme_code, {'de': 'Test'}),
            view_service_id=1
        )
        if theme_code == u'NotExistingTheme':
            with pytest.raises(HTTPServerError):
                Base.get_symbol_ref(request, record)
        else:
            ref = Base.get_symbol_ref(request, record)
            assert ref == 'http://example.com/image/symbol/{}/{}/{}'.format(
                theme_code,
                record.view_service_id,
                record.type_code
            )
