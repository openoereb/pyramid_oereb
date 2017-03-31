# -*- coding: utf-8 -*-
from pyramid_oereb.lib.records import BaseRecord


def test_init():
    record = BaseRecord()
    assert isinstance(record, BaseRecord)


def test_read():
    record = BaseRecord()
    assert isinstance(record.get_fields(), list)
