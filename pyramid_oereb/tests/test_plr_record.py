# -*- coding: utf-8 -*-
import datetime
import pytest

from pyramid_oereb.lib.records.office import OfficeRecord
from pyramid_oereb.lib.records.plr import PlrRecord
from pyramid_oereb.lib.records.theme import ThemeRecord


def test_mandatory_fields():
    with pytest.raises(TypeError):
        PlrRecord()


def test_init():
    office = OfficeRecord('Office')
    record = PlrRecord(ThemeRecord('code', dict()), 'Content', 'runningModifications',
                       datetime.date(1985, 8, 29), office)
    assert record.content == 'Content'
    assert record.subtopic is None
    assert isinstance(record.geometries, list)
    assert isinstance(record.responsible_office, OfficeRecord)
    assert isinstance(record.theme, ThemeRecord)
