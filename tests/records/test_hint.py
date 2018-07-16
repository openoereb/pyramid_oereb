# -*- coding: utf-8 -*-
import datetime
import pytest
from pyramid_oereb.lib.records.law_status import LawStatusRecord

from pyramid_oereb.lib.records.documents import HintRecord
from pyramid_oereb.lib.records.office import OfficeRecord


def test_mandatory_fields():
    with pytest.raises(TypeError):
        HintRecord()


def test_init(law_status):
    office_record = OfficeRecord({'en': 'name'})
    record = HintRecord(law_status, datetime.date(1985, 8, 29), {'en': 'title'},
                        office_record, {'en': 'http://my.legal-provision.com'})
    assert isinstance(record.document_type, str)
    assert isinstance(record.law_status, LawStatusRecord)
    assert isinstance(record.published_from, datetime.date)
    assert isinstance(record.title, dict)
    assert isinstance(record.responsible_office, OfficeRecord)
    assert isinstance(record.text_at_web, dict)
    assert record.abbreviation is None
    assert record.official_number is None
    assert record.official_title is None
    assert record.canton is None
    assert record.municipality is None
    assert isinstance(record.articles, list)
    assert isinstance(record.references, list)
