# -*- coding: utf-8 -*-

import pytest
import datetime

from pyramid.httpexceptions import HTTPServerError
from pyramid.response import Response
from pyramid.testing import DummyRequest

from pyramid_oereb.lib.config import Config
from pyramid_oereb.lib.records.image import ImageRecord
from pyramid_oereb.lib.records.theme import ThemeRecord
from pyramid_oereb.lib.records.view_service import LegendEntryRecord
from pyramid_oereb.lib.renderer import Base
from pyramid_oereb.lib.renderer.extract.json_ import Renderer
from tests import pyramid_oereb_test_config
from tests.mockrequest import MockRequest
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


def test_get_localized_text_from_string():
    renderer = Renderer(DummyRenderInfo())
    localized_text = renderer.get_localized_text('Test')
    assert isinstance(localized_text, dict)
    assert localized_text.get('Text') == 'Test'
    assert localized_text.get('Language') == Config.get('default_language')


@pytest.mark.parametrize('language,result', [
    ('de', u'Dies ist ein Test'),
    ('en', u'This is a test'),
    ('fr', u'Dies ist ein Test')  # fr not available; use default language (de)
])
def test_get_localized_text_from_dict(language, result):
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
def test_get_multilingual_text_from_dict(language, result):
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


def test_sort_by_localized_text():
    renderer = Renderer(DummyRenderInfo())
    renderer._language = 'de'
    # Elements like in the glossary
    multilingual_elements = [{
        'title': {
            'fr': u'RDPPF',
            'de': u'\xd6REB',
        },
        'content': {
            'fr': u'Content-RDPPF',
            'de': u'Content-\xd6REB',
        },
    }, {
        'title': {
            'fr': u'No OFS',
            'de': u'BFS-Nr.',
        },
        'content': {
            'fr': u'Content-No OFS',
            'de': u'Content-BFS-Nr.',
        },
    }, {
        'title': {
            'fr': u'Ofo',
            'de': u'WaV',
        },
        'content': {
            'fr': u'Content-Ofo',
            'de': u'Content-WaV',
        },
    }]
    sorted_multilingual_elements = renderer.sort_by_localized_text(
            multilingual_elements,
            lambda element: element['title']
    )
    assert isinstance(sorted_multilingual_elements, list)
    assert len(sorted_multilingual_elements) == 3
    # Elements sorted by 'de' title:
    assert sorted_multilingual_elements[0]['title']['de'] == u'BFS-Nr.'
    assert sorted_multilingual_elements[1]['title']['de'] == u'\xd6REB'
    assert sorted_multilingual_elements[2]['title']['de'] == u'WaV'
    assert sorted_multilingual_elements[0]['content']['de'] == u'Content-BFS-Nr.'
    assert sorted_multilingual_elements[1]['content']['de'] == u'Content-\xd6REB'
    assert sorted_multilingual_elements[2]['content']['de'] == u'Content-WaV'
    # Still sorted with 'de' language, effect on 'fr' elements:
    assert sorted_multilingual_elements[0]['title']['fr'] == u'No OFS'
    assert sorted_multilingual_elements[1]['title']['fr'] == u'RDPPF'
    assert sorted_multilingual_elements[2]['title']['fr'] == u'Ofo'
    assert sorted_multilingual_elements[0]['content']['fr'] == u'Content-No OFS'
    assert sorted_multilingual_elements[1]['content']['fr'] == u'Content-RDPPF'
    assert sorted_multilingual_elements[2]['content']['fr'] == u'Content-Ofo'


@pytest.mark.parametrize('theme_code', [
    u'ContaminatedSites',
    u'NotExistingTheme',
])
def test_get_symbol_ref(theme_code):
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
