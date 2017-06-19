# -*- coding: utf-8 -*-
from pyramid_oereb.lib.records.theme import ThemeRecord


def test_init():
    record = ThemeRecord('code', {'de': 'Beschreibung'})
    assert record.code == 'code'
    assert record.text == {
        'de': 'Beschreibung'
    }
