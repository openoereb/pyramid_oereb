# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.records.image import ImageRecord
from pyramid_oereb.lib.records.theme import ThemeRecord
from pyramid_oereb.lib.records.view_service import ViewServiceRecord, LegendEntryRecord


def test_mandatory_fields():
    with pytest.raises(TypeError):
        ViewServiceRecord()


def test_init():
    # todo add min/max_NS attributes
    record = ViewServiceRecord('http://www.test.url.ch',
                               1,
                               1.0,
                               'http://www.test.url.ch')
    assert isinstance(record.reference_wms, str)
    assert isinstance(record.layer_index, int)
    assert isinstance(record.layer_opacity, float)
    assert isinstance(record.legend_at_web, str)
    assert isinstance(record.legends, list)


def test_init_with_relation():
    # todo add min/max_NS attributes
    legend_records = [LegendEntryRecord(
        ImageRecord('100'.encode('utf-8')),
        {'en': 'test'},
        'test_code',
        'test',
        ThemeRecord('test', {'de': 'Test'}),
        view_service_id=1
    )]
    record = ViewServiceRecord('http://www.test.url.ch',
                               1,
                               1.0,
                               'http://www.test.url.ch',
                               legend_records)
    assert isinstance(record.reference_wms, str)
    assert isinstance(record.layer_index, int)
    assert isinstance(record.layer_opacity, float)
    assert isinstance(record.legend_at_web, str)
    assert isinstance(record.legends, list)


def test_invalid_layer_index_arguments():
    with pytest.raises(AttributeError):
        ViewServiceRecord(reference_wms='http://example.com',
                          layer_index=-1001,
                          layer_opacity=1)
    with pytest.raises(AttributeError):
        ViewServiceRecord(reference_wms='http://example.com',
                          layer_index=1001,
                          layer_opacity=1)


def test_invalid_layer_layer_opacity():
    with pytest.raises(AttributeError):
        ViewServiceRecord(reference_wms='http://example.com',
                          layer_index=1,
                          layer_opacity=2.0)
    with pytest.raises(AttributeError):
        ViewServiceRecord(reference_wms='http://example.com',
                          layer_index=1,
                          layer_opacity=-1.1)

# todo add min/max_NS attributes tests
