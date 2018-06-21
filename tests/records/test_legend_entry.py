# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.records.image import ImageRecord
from pyramid_oereb.lib.records.theme import ThemeRecord
from pyramid_oereb.lib.records.view_service import LegendEntryRecord


def test_mandatory_fields():
    with pytest.raises(TypeError):
        LegendEntryRecord()


def test_init():
    record = LegendEntryRecord(
        ImageRecord('100'.encode('utf-8')),
        {'de': 'test'},
        'test_code',
        'test',
        ThemeRecord('test', {'de': 'Test'}),
        view_service_id=1
    )
    assert isinstance(record.symbol, ImageRecord)
    assert isinstance(record.legend_text, dict)
    assert isinstance(record.type_code, str)
    assert isinstance(record.type_code_list, str)
    assert isinstance(record.theme, ThemeRecord)
    assert record.sub_theme is None
    assert record.other_theme is None
    assert record.legend_text == {'de': 'test'}
