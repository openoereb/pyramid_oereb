# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.records.image import ImageRecord
from pyramid_oereb.lib.records.theme import ThemeRecord
from pyramid_oereb.lib.records.view_service import ViewServiceRecord, LegendEntryRecord
from shapely.geometry.point import Point


def test_mandatory_fields():
    with pytest.raises(TypeError):
        ViewServiceRecord()


def test_init():
    record = ViewServiceRecord('http://www.test.url.ch',
                               1,
                               1.0,
                               'http://www.test.url.ch',
                               None,
                               Point(2608000, 1261000),
                               Point(2609000, 1262000),
                               Point(2608000, 1261000),
                               Point(2609000, 1262000))
    assert isinstance(record.reference_wms, str)
    assert isinstance(record.layer_index, int)
    assert isinstance(record.layer_opacity, float)
    assert isinstance(record.legend_at_web, str)
    assert isinstance(record.legends, list)
    assert isinstance(record.min_NS03, Point)
    assert isinstance(record.max_NS03, Point)
    assert isinstance(record.min_NS95, Point)
    assert isinstance(record.max_NS95, Point)


def test_init_with_relation():
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
                               legend_records,
                               Point(2608000, 1261000),
                               Point(2609000, 1262000),
                               Point(2608000, 1261000),
                               Point(2609000, 1262000))
    assert isinstance(record.reference_wms, str)
    assert isinstance(record.layer_index, int)
    assert isinstance(record.layer_opacity, float)
    assert isinstance(record.legend_at_web, str)
    assert isinstance(record.legends, list)
    assert isinstance(record.min_NS03, Point)
    assert isinstance(record.max_NS03, Point)
    assert isinstance(record.min_NS95, Point)
    assert isinstance(record.max_NS95, Point)


def test_invalid_layer_index_arguments():
    with pytest.raises(AttributeError):
        ViewServiceRecord('http://example.com', -1001, 1)
    with pytest.raises(AttributeError):
        ViewServiceRecord('http://example.com', 1001, 1)
    with pytest.warns(UserWarning, match='Type of "layer_index" should be "int"'):
        ViewServiceRecord('http://example.com', 1.0, 1)


def test_invalid_layer_layer_opacity():
    with pytest.raises(AttributeError):
        ViewServiceRecord('http://example.com', 1, 2.0)
    with pytest.raises(AttributeError):
        ViewServiceRecord('http://example.com', 1, -1.1)
    with pytest.warns(UserWarning, match='Type of "layer_opacity" should be "float"'):
        ViewServiceRecord('http://example.com', 1, 1)


def test_min_max_attributes():
    min_val = Point(1, 1)
    max_val = Point(2, 2)

    # test None values, expect no error
    ViewServiceRecord('http://www.test.url.ch',
                      1,
                      1.0,
                      'http://www.test.url.ch',
                      None,
                      None,
                      None,
                      None,
                      None)

    # combinations of value + None
    with pytest.raises(AttributeError):
        ViewServiceRecord('http://www.test.url.ch',
                          1,
                          1.0,
                          'http://www.test.url.ch',
                          None,
                          min_val,
                          None,
                          None,
                          None)

    with pytest.raises(AttributeError):
        ViewServiceRecord('http://www.test.url.ch',
                          1,
                          1.0,
                          'http://www.test.url.ch',
                          None,
                          None,
                          min_val,
                          None,
                          None)

    with pytest.raises(AttributeError):
        ViewServiceRecord('http://www.test.url.ch',
                          1,
                          1.0,
                          'http://www.test.url.ch',
                          None,
                          None,
                          None,
                          min_val,
                          None)

    with pytest.raises(AttributeError):
        ViewServiceRecord('http://www.test.url.ch',
                          1,
                          1.0,
                          'http://www.test.url.ch',
                          None,
                          None,
                          None,
                          None,
                          min_val)

    # type error
    with pytest.raises(AttributeError):
        ViewServiceRecord('http://www.test.url.ch',
                          1,
                          1.0,
                          'http://www.test.url.ch',
                          None,
                          1,
                          2,
                          3,
                          4)

    # inverted values
    with pytest.raises(AttributeError):
        ViewServiceRecord('http://www.test.url.ch',
                          1,
                          1.0,
                          'http://www.test.url.ch',
                          None,
                          max_val,
                          min_val,
                          max_val,
                          min_val)
