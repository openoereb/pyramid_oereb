# -*- coding: utf-8 -*-
from pyramid_oereb.lib.records.logo import LogoRecord


def test_logo_init():
    record = LogoRecord(u'ch.1234', {u'de': u'Gesetzliche Grundlage'})
    assert record.code == u'ch.1234'
    assert record.logo == {
        u'de': u'Gesetzliche Grundlage'
    }
    assert isinstance(record.logo['de'], bytes)
