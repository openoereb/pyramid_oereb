# -*- coding: utf-8 -*-
import pytest
from pyramid_oereb.lib.records.view_service import ViewServiceRecord, LegendEntryRecord


def test_get_fields():
    expected_fields = [
        'link_wms',
        'legend_web',
        'legends'
    ]
    fields = ViewServiceRecord.get_fields()
    assert fields == expected_fields


def test_mandatory_fields():
    with pytest.raises(TypeError):
        ViewServiceRecord()


def test_init():
    record = ViewServiceRecord('http://www.test.url.ch', 'http://www.test.url.ch')
    assert isinstance(record.link_wms, str)
    assert isinstance(record.legend_web, str)
    assert isinstance(record.legends, list)


def test_init_with_relation():
    legend_records = [LegendEntryRecord(bin(100), 'test', 'test_code', 'test', 'test')]
    record = ViewServiceRecord('http://www.test.url.ch', 'http://www.test.url.ch', legend_records)
    assert isinstance(record.link_wms, str)
    assert isinstance(record.legend_web, str)
    assert isinstance(record.legends, list)


def test_to_extract():
    legend_records = [LegendEntryRecord(bin(100), 'test', 'test_code', 'test', 'test')]
    record = ViewServiceRecord('http://www.test.url.ch', 'http://www.test.url.ch', legend_records)
    assert record.to_extract() == {
        'link_wms': 'http://www.test.url.ch',
        'legend_web': 'http://www.test.url.ch',
        'legends': [
            {
                'symbol': bin(100),
                'legend_text': 'test',
                'type_code': 'test_code',
                'type_code_list': 'test',
                'theme': 'test'
            }
        ]
    }


def test_to_extract_filtered():
    legend_records = [
        LegendEntryRecord(bin(100), 'test1', 'test1_code', 'test1', 'test1'),
        LegendEntryRecord(bin(100), 'test2', 'test2_code', 'test2', 'test2')
    ]
    record = ViewServiceRecord('http://www.test.url.ch', 'http://www.test.url.ch', legend_records)
    assert record.to_extract(type_code='test2_code') == {
        'link_wms': 'http://www.test.url.ch',
        'legend_web': 'http://www.test.url.ch',
        'legends': [
            {
                'symbol': bin(100),
                'legend_text': 'test2',
                'type_code': 'test2_code',
                'type_code_list': 'test2',
                'theme': 'test2'
            }
        ]
    }
