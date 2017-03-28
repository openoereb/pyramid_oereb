# -*- coding: utf-8 -*-
import pytest
from pyramid_oereb.lib.records.view_service import ViewServiceRecord, LegendEntryRecord

__author__ = 'Clemens Rudert'
__create_date__ = '28.03.17'


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
