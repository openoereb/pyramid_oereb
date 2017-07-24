# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.records.image import ImageRecord
from pyramid_oereb.lib.records.theme import ThemeRecord
from pyramid_oereb.lib.records.view_service import ViewServiceRecord, LegendEntryRecord


def test_mandatory_fields():
    with pytest.raises(TypeError):
        ViewServiceRecord()


def test_init():
    record = ViewServiceRecord('http://www.test.url.ch', 'http://www.test.url.ch')
    assert isinstance(record.reference_wms, str)
    assert isinstance(record.legend_at_web, str)
    assert isinstance(record.legends, list)


def test_init_with_relation():
    legend_records = [LegendEntryRecord(
        ImageRecord('100'.encode('utf-8')), {'en': 'test'}, 'test_code', 'test',
        ThemeRecord('test', {'de': 'Test'}))]
    record = ViewServiceRecord('http://www.test.url.ch', 'http://www.test.url.ch', legend_records)
    assert isinstance(record.reference_wms, str)
    assert isinstance(record.legend_at_web, str)
    assert isinstance(record.legends, list)
