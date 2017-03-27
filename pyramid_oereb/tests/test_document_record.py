# -*- coding: utf-8 -*-
import datetime
import pytest

from pyramid_oereb.lib.records.documents import DocumentRecord
from pyramid_oereb.lib.records.office import OfficeRecord


def test_get_fields():
    expected_fields = [
        'text_at_web',
        'law_status',
        'published_from',
        'title',
        'responsible_office',
        'abbrevation',
        'official_number',
        'canton',
        'municipality',
        'file',
        'articles',
        'references'
    ]
    fields = DocumentRecord.get_fields()
    assert fields == expected_fields


def test_mandatory_fields():
    with pytest.raises(TypeError):
        DocumentRecord()


def test_init():
    office_record = OfficeRecord('name')
    record = DocumentRecord("runningModifications", datetime.date(1985, 8, 29), 'title', office_record)
    assert isinstance(record.law_status, str)
    assert isinstance(record.published_from, datetime.date)
    assert isinstance(record.title, str)
    assert isinstance(record.responsible_office, OfficeRecord)
    assert record.text_at_web is None
    assert record.abbrevation is None
    assert record.official_number is None
    assert record.canton is None
    assert record.municipality is None
    assert isinstance(record.articles, list)
    assert isinstance(record.references, list)
