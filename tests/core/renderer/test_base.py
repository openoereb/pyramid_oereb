# -*- coding: utf-8 -*-

import io
from urllib.parse import urlparse
import pytest
from unittest.mock import patch
import datetime
from PIL import Image

from pyramid.httpexceptions import HTTPServerError, HTTPInternalServerError
from pyramid.response import Response
from pyramid.testing import DummyRequest

from pyramid_oereb.core.adapter import FileAdapter
from pyramid_oereb.core.config import Config
from pyramid_oereb.core.records.image import ImageRecord
from pyramid_oereb.core.records.theme import ThemeRecord
from pyramid_oereb.core.records.view_service import LegendEntryRecord
from pyramid_oereb.core.renderer import Base
from pyramid_oereb.core.renderer.extract.json_ import Renderer
import pyramid_oereb.core.hook_methods
from tests.mockrequest import MockRequest


@pytest.fixture
def png_image():
    yield Image.new("RGB", (72, 36), (128, 128, 128))


@pytest.fixture
def png_binary(png_image):
    output = io.BytesIO()
    png_image.save(output, format='PNG')
    yield output.getvalue()


def test_call(DummyRenderInfo, pyramid_oereb_test_config):
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


def test_get_localized_text_from_string(DummyRenderInfo):
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
def test_get_localized_text_from_dict(DummyRenderInfo, language, result, pyramid_oereb_test_config):
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


@pytest.mark.parametrize('language,result,disallowNull', [
    ('de', u'Error', True),  # default_language not available!
    ('en', u'This is a test', True),
    ('it', u'Questo è un test', True),
    ('fr', u'Error', True),  # fr not available!
    ('de', None, False),  # allow null value if lang & default is not available
    ('fr', None, False)  # allow null value if lang & default is not available
])
def test_get_localized_text_from_dict_no_default(DummyRenderInfo, language, result, disallowNull):
    renderer = Renderer(DummyRenderInfo())
    renderer._language = language
    multilingual_text = {
        'en': u'This is a test',
        'it': u'Questo è un test'
    }

    if language in ['en', 'it'] or not disallowNull:
        localized_text = renderer.get_localized_text(multilingual_text, disallowNull)
        assert isinstance(localized_text, dict)
        assert localized_text.get('Language') in ['de', 'it', 'en']
        assert localized_text.get('Text') == result
    else:
        with pytest.raises(HTTPInternalServerError):
            localized_text = renderer.get_localized_text(multilingual_text, disallowNull)


@pytest.mark.parametrize('language,result', [
    ('de', u'Dies ist ein Test'),
    ('en', u'This is a test'),
    ('fr', u'Dies ist ein Test')  # fr not available; use default language (de)
])
def test_get_multilingual_text_from_dict(DummyRenderInfo, language, result, pyramid_oereb_test_config):
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


def test_sort_by_localized_text(DummyRenderInfo):
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


@patch.object(pyramid_oereb.core.hook_methods, 'route_prefix', 'oereb')
@pytest.mark.parametrize('theme_code', [
    u'ch.BelasteteStandorte',
    u'NotExistingTheme',
])
def test_get_symbol_ref(theme_code, pyramid_test_config, pyramid_oereb_test_config):
    request = MockRequest()
    record = LegendEntryRecord(
        ImageRecord(FileAdapter().read('tests/resources/python.svg')),
        {'de': 'Test'},
        u'test',
        u'test',
        ThemeRecord(theme_code, {'de': 'Test'}, 100),
        view_service_id=1,
        identifier="1"
    )
    if theme_code == u'NotExistingTheme':
        with pytest.raises(HTTPServerError):
            Base.get_symbol_ref(request, record)
    else:
        ref = Base.get_symbol_ref(request, record)
        assert ref == 'http://example.com/image/symbol/{}/legend_entry.svg?identifier=1'.format(
            theme_code
        )


@pytest.mark.parametrize('test_value, expected_results', [
    ({
        'logo_code': 'ch',
        'language': 'de',
    }, '/image/logo/ch/de.png'),
    ({
        'logo_code': 'bs',
        'language': 'fr',
    }, '/image/logo/bs/fr.png')
    ])
def test_get_logo_ref(test_value, expected_results, png_binary):
    with patch.object(Config, 'get_logo_hooks',
                      return_value={"get_logo_ref": "pyramid_oereb.core.hook_methods.get_logo_ref"}):
        request = DummyRequest()
        url = urlparse(Base.get_logo_ref(request,
                       test_value.get('logo_code'),
                       test_value.get('language'),
                       {test_value.get('language'): ImageRecord(png_binary)}))
        assert url.path == expected_results


@pytest.mark.parametrize('test_value, expected_results', [
    ({
        'logo_code': 'ch',
        'language': 'de',
    }, '/image/logo/ch/de.png'),
    ({
        'logo_code': 'bs',
        'language': 'fr',
    }, '/image/logo/bs/fr.png')
    ])
def test_get_logo_ref_no_method(test_value, expected_results, png_binary):
    with patch.object(Config, 'get_logo_hooks',
                      return_value={"get_logo_ref": "pyramid_oereb.core.hook_methods.get_logo_ref"}):
        with patch.object(pyramid_oereb.core.hook_methods, 'get_logo_ref', {}):
            with pytest.raises(HTTPServerError):
                Base.get_logo_ref(DummyRequest(),
                                  test_value.get('logo_code'),
                                  test_value.get('language'),
                                  {test_value.get('language'): ImageRecord(png_binary)})


@pytest.mark.parametrize('test_value, expected_results', [
    ('', ''),
    (None, None)
    ])
def test_get_qr_code_ref(test_value, expected_results):
    with patch.object(Config, 'get_logo_hooks',
                      return_value={"get_qr_code_ref": "pyramid_oereb.core.hook_methods.get_qr_code_ref"}):
        request = DummyRequest()
        assert Base.get_qr_code_ref(request, test_value) == expected_results


@pytest.mark.parametrize('test_value, expected_results', [
    ('', '')
    ])
def test_get_qr_code_ref_no_method(test_value, expected_results):
    with patch.object(Config, 'get_logo_hooks',
                      return_value={
                          "get_qr_code_ref": "pyramid_oereb.core.hook_methods.get_qr_code_ref"
                          }):
        with patch.object(pyramid_oereb.core.hook_methods, 'get_qr_code_ref', {}):
            with pytest.raises(HTTPServerError):
                Base.get_qr_code_ref(DummyRequest(), test_value)
