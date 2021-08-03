# -*- coding: utf-8 -*-

from pyramid_oereb.lib.records.law_status import LawStatusRecord


def test_law_status_init():
    record = LawStatusRecord(u'inKraft', {u'de': u'Rechtskräftig'})
    assert record.code == u'inKraft'
    assert isinstance(record.text, dict)
    assert record.text == {
        u'de': u'Rechtskräftig'
    }
