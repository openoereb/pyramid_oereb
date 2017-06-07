# -*- coding: utf-8 -*-
import datetime
import pytest

from pyramid_oereb.lib.records.documents import LegalProvisionRecord
from pyramid_oereb.lib.records.office import OfficeRecord


def test_mandatory_fields():
    with pytest.raises(TypeError):
        LegalProvisionRecord()


def test_init():
    office_record = OfficeRecord({'en': 'name'})
    record = LegalProvisionRecord("runningModifications", datetime.date(1985, 8, 29), {'en': 'title'},
                                  office_record)
    assert isinstance(record.legal_state, str)
    assert isinstance(record.published_from, datetime.date)
    assert isinstance(record.title, dict)
    assert isinstance(record.responsible_office, OfficeRecord)
    assert record.text_at_web is None
    assert record.abbreviation is None
    assert record.official_number is None
    assert record.official_title is None
    assert record.canton is None
    assert record.municipality is None
    assert isinstance(record.articles, list)
    assert isinstance(record.references, list)
