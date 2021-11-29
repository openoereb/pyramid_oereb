# -*- coding: utf-8 -*-

from pyramid_oereb.core.records.law_status import LawStatusRecord


def test_law_status_init():
    record = LawStatusRecord(u'inKraft', {u'de': u'Rechtskräftig'})
    assert record.code == u'inKraft'
    assert isinstance(record.title, dict)
    assert record.title == {
        u'de': u'Rechtskräftig'
    }
