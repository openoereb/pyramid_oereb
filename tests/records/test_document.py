# -*- coding: utf-8 -*-
import datetime
import pytest
from pyramid_oereb.lib.records.law_status import LawStatusRecord

from pyramid_oereb.lib.records.documents import DocumentRecord
from pyramid_oereb.lib.records.office import OfficeRecord
from pyramid_oereb.lib.config import Config


def test_mandatory_fields():
    with pytest.raises(TypeError):
        DocumentRecord('AenderungMitVorwirkung', datetime.date(1985, 8, 29))


def test_init():
    office_record = OfficeRecord({'en': 'name'})
    law_status = Config.get_law_status_by_law_status_code(u'inKraft')
    record = DocumentRecord('GesetzlicheGrundlage', 1, law_status, {'en': 'title'}, office_record,
                            datetime.date(1985, 8, 29), text_at_web={'en': 'http://my.document.com'})
    assert isinstance(record.document_type, str)
    assert isinstance(record.index, int)
    assert isinstance(record.law_status, LawStatusRecord)
    assert isinstance(record.published_from, datetime.date)
    assert isinstance(record.title, dict)
    assert isinstance(record.responsible_office, OfficeRecord)
    assert isinstance(record.text_at_web, dict)
    assert record.published_until is None
    assert record.abbreviation is None
    assert record.official_number is None
    assert record.only_in_municipality is None
    assert record.article_numbers == []
    assert record.published


def test_invalid_document_type():
    office_record = OfficeRecord({'en': 'name'})
    with pytest.raises(AttributeError):
        DocumentRecord('invalid', 1, 'AenderungMitVorwirkung', {'en': 'title'}, office_record,
                       datetime.date(1985, 8, 29))


def test_future_document():
    office_record = OfficeRecord({'en': 'name'})
    law_status = Config.get_law_status_by_law_status_code(u'inKraft')
    record = DocumentRecord('Hinweis', 1, law_status, {'en': 'title'}, office_record,
                            (datetime.datetime.now().date() + datetime.timedelta(days=7)),
                            text_at_web={'en': 'http://my.document.com'})
    assert not record.published


def test_past_document():
    office_record = OfficeRecord({'en': 'name'})
    law_status = Config.get_law_status_by_law_status_code(u'inKraft')
    record = DocumentRecord('Hinweis', 1, law_status, {'en': 'title'}, office_record,
                            (datetime.datetime.now().date() - datetime.timedelta(days=7)),
                            published_until=(datetime.datetime.now().date() - datetime.timedelta(days=6)),
                            text_at_web={'en': 'http://my.document.com'})
    assert not record.published


def test_legal_provision():
    office_record = OfficeRecord({'en': 'name'})
    law_status = Config.get_law_status_by_law_status_code(u'inKraft')
    legal_provision = DocumentRecord('Rechtsvorschrift', 1, law_status, {'de': 'title'},
                                     office_record, datetime.date(1985, 8, 29))
    assert isinstance(legal_provision.document_type, str)
    assert legal_provision.document_type == 'Rechtsvorschrift'
