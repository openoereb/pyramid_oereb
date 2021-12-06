# -*- coding: utf-8 -*-
from pyramid_oereb.core.records.theme import ThemeRecord


def test_theme_init():
    record = ThemeRecord(u'code', {u'de': u'Beschreibung'}, 100)
    assert record.code == u'code'
    assert record.title == {
        u'de': u'Beschreibung'
    }
