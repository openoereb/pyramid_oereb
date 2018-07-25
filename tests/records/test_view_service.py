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
                               None)
    assert isinstance(record.reference_wms, str)
    assert isinstance(record.layer_index, int)
    assert isinstance(record.layer_opacity, float)
    assert isinstance(record.legend_at_web, str)
    assert isinstance(record.legends, list)


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
                               legend_records)
    assert isinstance(record.reference_wms, str)
    assert isinstance(record.layer_index, int)
    assert isinstance(record.layer_opacity, float)
    assert isinstance(record.legend_at_web, str)
    assert isinstance(record.legends, list)


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


def test_check_min_max_attributes():
    min_val = Point(1, 1)
    max_val = Point(2, 2)

    # test None values, expect no error
    ViewServiceRecord.check_min_max_attributes(None, 'test1', None, 'test2')

    # combinations of value + None
    with pytest.raises(AttributeError):
        ViewServiceRecord.check_min_max_attributes(min_val, 'test1', None, 'test2')
    with pytest.raises(AttributeError):
        ViewServiceRecord.check_min_max_attributes(None, 'test1', min_val, 'test2')

    # type error
    with pytest.raises(AttributeError):
        ViewServiceRecord.check_min_max_attributes(1, 'test1', 2, 'test2')

    # inverted values
    with pytest.raises(AttributeError):
        ViewServiceRecord.check_min_max_attributes(max_val, 'test1', min_val, 'test2')


def test_get_bbox_from_url():
    with_bbox = 'https://host/?&SRS=EPSG:2056&BBOX=2475000,1065000,2850000,1300000&' \
                'WIDTH=493&HEIGHT=280&FORMAT=image/png'
    p1, p2 = ViewServiceRecord.get_bbox_from_url(with_bbox)
    assert isinstance(p1, Point)
    assert p1.x == 2475000.0
    assert p1.y == 1065000.0
    assert isinstance(p2, Point)
    assert p2.x == 2850000.0
    assert p2.y == 1300000.0

    no_bbox = 'https://host/?&SRS=EPSG:2056WIDTH=493&HEIGHT=280&FORMAT=image/png'
    p3, p4 = ViewServiceRecord.get_bbox_from_url(no_bbox)
    assert p3 is None
    assert p4 is None


def test_view_service_correct_init_ns(config):
    with_bbox = 'https://host/?&SRS=EPSG:2056&BBOX=2475000,1065000,2850000,1300000&' \
                'WIDTH=493&HEIGHT=280&FORMAT=image/png'
    test_view_service = ViewServiceRecord(with_bbox, 1, 1.0, 'http://www.test.url.ch', None)
    assert isinstance(test_view_service.min_NS95, Point)
    assert test_view_service.min_NS95.x == 2475000.0
    assert test_view_service.min_NS95.y == 1065000.0
    assert isinstance(test_view_service.max_NS95, Point)
    assert test_view_service.max_NS95.x == 2850000.0
    assert test_view_service.max_NS95.y == 1300000.0

    no_bbox = 'https://host/?&SRS=EPSG:2056WIDTH=493&HEIGHT=280&FORMAT=image/png'
    test_view_service_no_bbox = ViewServiceRecord(no_bbox, 1, 1.0, 'http://www.test.url.ch', None)
    assert test_view_service_no_bbox.min_NS95 is None
    assert test_view_service_no_bbox.max_NS95 is None
