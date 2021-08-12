# -*- coding: utf-8 -*-
from pyramid_oereb.lib.records.logo import LogoRecord


def test_logo_init():
    record = LogoRecord(u'ch.1234', {
        'de': 'iVBORw0KGgoAAAANSUhEUgAAAWIAAACaCAIAAAAggg=='
        })
    assert record.code == u'ch.1234'
    assert record.image_dict == {
        'de': 'iVBORw0KGgoAAAANSUhEUgAAAWIAAACaCAIAAAAggg=='
    }
    assert isinstance(record.logo['de'], bytes)
