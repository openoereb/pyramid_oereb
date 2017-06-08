# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.records.office import OfficeRecord
from pyramid_oereb.lib.renderer.extract.json_ import Renderer
from pyramid_oereb.tests.test_renderer_base import DummyRenderInfo


def test_get_localized_text_from_str(config):
    assert isinstance(config._config, dict)
    renderer = Renderer(DummyRenderInfo())
    renderer._language_ = 'de'
    assert renderer.get_localized_text('test') == [
        {
            'Language': 'de',
            'Text': 'test'
        }
    ]


@pytest.mark.parametrize('language,result', [
    ('de', 'Dies ist ein Test'),
    ('en', 'This is a test'),
    ('fr', 'Dies ist ein Test')  # fr not available; use default language (de)
])
def test_get_localized_text_from_dict(config, language, result):
    assert isinstance(config._config, dict)
    renderer = Renderer(DummyRenderInfo())
    renderer._language_ = language
    multilingual_text = {
        'de': 'Dies ist ein Test',
        'en': 'This is a test'
    }
    localized_text = renderer.get_localized_text(multilingual_text)
    assert isinstance(localized_text, list)
    assert len(localized_text) == 1
    assert localized_text[0]['Text'] == result


def test_format_office(config):
    assert isinstance(config._config, dict)
    office = OfficeRecord({'de': 'Test'}, uid='test_uid', office_at_web='http://test.example.com',
                          line1='test_line1', line2='test_line2', street='test_street', number='test_number',
                          postal_code=1234, city='test_city')
    renderer = Renderer(DummyRenderInfo())
    renderer._language_ = 'de'
    assert renderer.format_office(office) == {
        'Name': renderer.get_localized_text('Test'),
        'UID': 'test_uid',
        'OfficeAtWeb': 'http://test.example.com',
        'Line1': 'test_line1',
        'Line2': 'test_line2',
        'Street': 'test_street',
        'Number': 'test_number',
        'PostalCode': 1234,
        'City': 'test_city'
    }


# TODO: Add tests for remaining format methods.
