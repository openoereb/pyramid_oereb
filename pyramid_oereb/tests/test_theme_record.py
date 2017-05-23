# -*- coding: utf-8 -*-
from pyramid_oereb.lib.records.theme import ThemeRecord


def test_init():
    record = ThemeRecord('code', {'de': 'Beschreibung'})
    assert record.code == 'code'
    assert record.text == {
        'de': 'Beschreibung'
    }


def test_get_fields():
    assert ThemeRecord.get_fields() == [
        'code',
        'text'
    ]


def test_to_extract():
    record = ThemeRecord('code', {'de': 'Beschreibung'})
    assert record.to_extract() == {
        'code': 'code',
        'text': [
            {
                'language': 'de',
                'text': 'Beschreibung'
            }
        ]
    }
