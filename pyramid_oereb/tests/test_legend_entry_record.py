# -*- coding: utf-8 -*-
import pytest
from pyramid_oereb.lib.records.view_service import LegendEntryRecord


def test_get_fields():
    expected_fields = [
        'symbol',
        'legend_text',
        'type_code',
        'type_code_list',
        'theme',
        'sub_theme',
        'additional_theme'
    ]
    fields = LegendEntryRecord.get_fields()
    assert fields == expected_fields


def test_mandatory_fields():
    with pytest.raises(TypeError):
        LegendEntryRecord()


def test_init():
    record = LegendEntryRecord(bin(100), 'test', 'test_code', 'test', 'test')
    assert isinstance(record.symbol, str)
    assert isinstance(record.legend_text, str)
    assert isinstance(record.type_code, str)
    assert isinstance(record.type_code_list, str)
    assert isinstance(record.theme, str)
    assert record.sub_theme is None
    assert record.additional_theme is None


def test_to_extract():
    assert LegendEntryRecord(
        bin(100),
        'test',
        'test_code',
        'test',
        'test',
        sub_theme='test',
        additional_theme='test'
    ).to_extract() == {
        'symbol': bin(100),
        'legend_text': 'test',
        'type_code': 'test_code',
        'type_code_list': 'test',
        'theme': 'test',
        'sub_theme': 'test',
        'additional_theme': 'test'
    }
