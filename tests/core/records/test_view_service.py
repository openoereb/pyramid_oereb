# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.core.records.image import ImageRecord
from pyramid_oereb.core.records.theme import ThemeRecord
from pyramid_oereb.core.records.view_service import ViewServiceRecord, LegendEntryRecord
from shapely.geometry.point import Point


def test_mandatory_fields():
    with pytest.raises(TypeError):
        ViewServiceRecord()


def test_init():
    record = ViewServiceRecord(
        {'de': 'http://www.test.url.ch'},
        1,
        1.0,
        'de',
        2056,
        None,
        None
    )
    assert isinstance(record.reference_wms, dict)
    assert isinstance(record.layer_index, int)
    assert isinstance(record.layer_opacity, float)
    assert isinstance(record.legends, list)
    assert record.default_language == 'de'
    assert record.srid == 2056
    assert record.proxies is None
    assert len(record.legends) == 0


def test_init_with_relation(pyramid_oereb_test_config):
    legend_entry_record = LegendEntryRecord(
        ImageRecord('100'.encode('utf-8')),
        {'en': 'test'},
        'test_code',
        'test',
        ThemeRecord('test', {'de': 'Test'}, 100),
        view_service_id=1
    )
    legend_records = [legend_entry_record]
    record = ViewServiceRecord(
        {'de': 'http://www.test.url.ch'},
        1,
        1.0,
        'de',
        2056,
        None,
        legend_records
    )
    assert isinstance(record.reference_wms, dict)
    assert isinstance(record.layer_index, int)
    assert isinstance(record.layer_opacity, float)
    assert record.default_language == 'de'
    assert record.srid == 2056
    assert record.proxies is None
    assert len(record.legends) == 1
    assert record.legends[0] == legend_entry_record


def test_invalid_layer_index_arguments(pyramid_oereb_test_config):
    with pytest.raises(AttributeError):
        ViewServiceRecord({'de': 'http://example.com'}, -1001, 1, 'de', 2056, None, None)
    with pytest.raises(AttributeError):
        ViewServiceRecord({'de': 'http://example.com'}, 1001, 1, 'de', 2056, None, None)
    with pytest.warns(UserWarning, match='Type of "layer_index" should be "int"'):
        ViewServiceRecord({'de': 'http://example.com'}, 1.0, 1, 'de', 2056, None, None)


def test_invalid_layer_layer_opacity(pyramid_oereb_test_config):
    with pytest.raises(AttributeError):
        ViewServiceRecord({'de': 'http://example.com'}, 1, 2.0, 'de', 2056, None, None)
    with pytest.raises(AttributeError):
        ViewServiceRecord({'de': 'http://example.com'}, 1, -1.1, 'de', 2056, None, None)
    with pytest.warns(UserWarning, match='Type of "layer_opacity" should be "float"'):
        ViewServiceRecord({'de': 'http://example.com'}, 1, 1, 'de', 2056, None, None)


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


def test_view_service_correct_init_ns(pyramid_oereb_test_config):
    with_bbox = {'de': 'https://host/?&SRS=EPSG:2056&BBOX=2475000,1065000,2850000,1300000&'
                 'WIDTH=493&HEIGHT=280&FORMAT=image/png'}
    test_view_service = ViewServiceRecord(with_bbox, 1, 1.0, 'de', 2056, None, None)
    assert isinstance(test_view_service.min, Point)
    assert test_view_service.min.x == 2475000.0
    assert test_view_service.min.y == 1065000.0
    assert isinstance(test_view_service.max, Point)
    assert test_view_service.max.x == 2850000.0
    assert test_view_service.max.y == 1300000.0

    no_bbox = {'de': 'https://host/?&SRS=EPSG:2056WIDTH=493&HEIGHT=280&FORMAT=image/png'}
    test_view_service_no_bbox = ViewServiceRecord(no_bbox, 1, 1.0, 'de', 2056, None, None)
    assert test_view_service_no_bbox.min is None
    assert test_view_service_no_bbox.max is None


def get_width_from_bbox(bbox):
    return bbox[2] - bbox[0]


def get_height_from_bbox(bbox):
    return bbox[3] - bbox[1]
