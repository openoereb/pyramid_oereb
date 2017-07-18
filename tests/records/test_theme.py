# -*- coding: utf-8 -*-
from pyramid_oereb.lib.records.theme import ThemeRecord


def test_theme_init():
    record = ThemeRecord(u'code', {u'de': u'Beschreibung'})
    assert record.code == u'code'
    assert record.text == {
        u'de': u'Beschreibung'
    }
