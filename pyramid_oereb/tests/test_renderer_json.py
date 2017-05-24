# -*- coding: utf-8 -*-
from pyramid_oereb.lib.records.office import OfficeRecord
from pyramid_oereb.lib.renderer.json_ import Extract
from pyramid_oereb.tests.conftest import MockRequest
from pyramid_oereb.tests.test_renderer_base import DummyRenderInfo


def test_get_localized_text():
    renderer = Extract(DummyRenderInfo())
    MockRequest()
    assert renderer.get_localized_text('test') == [
        {
            'Language': 'de',
            'Text': 'test'
        }
    ]


def test_format_office():
    office = OfficeRecord('Test', uid='test_uid', office_at_web='http://test.example.com', line1='test_line1',
                          line2='test_line2', street='test_street', number='test_number',
                          postal_code='test_postal_code', city='test_city')
    renderer = Extract(DummyRenderInfo())
    MockRequest()
    assert renderer.format_office(office) == {
        'Name': renderer.get_localized_text('Test'),
        'UID': 'test_uid',
        'OfficeAtWeb': 'http://test.example.com',
        'Line1': 'test_line1',
        'Line2': 'test_line2',
        'Street': 'test_street',
        'Number': 'test_number',
        'PostalCode': 'test_postal_code',
        'City': 'test_city'
    }
