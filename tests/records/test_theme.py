# -*- coding: utf-8 -*-
from pyramid_oereb.lib.records.theme import ThemeRecord, EmbeddableThemeRecord


def test_theme_init():
    record = ThemeRecord(u'code', {u'de': u'Beschreibung'})
    assert record.code == u'code'
    assert record.text == {
        u'de': u'Beschreibung'
    }


def test_embeddable_theme_init():
    record = EmbeddableThemeRecord(u'code', {u'de': u'Beschreibung'}, [])
    assert record.code == u'code'
    assert record.text == {
        u'de': u'Beschreibung'
    }
    assert record.sources == []
