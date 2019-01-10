# -*- coding: utf-8 -*-
import datetime
import pytest
from pyramid_oereb.lib.records.law_status import LawStatusRecord

from pyramid_oereb.lib.records.documents import DocumentRecord, ArticleRecord, LegalProvisionRecord
from pyramid_oereb.lib.records.office import OfficeRecord


def test_mandatory_fields():
    with pytest.raises(TypeError):
        DocumentRecord('runningModifications', datetime.date(1985, 8, 29))


def test_init():
    office_record = OfficeRecord({'en': 'name'})
    law_status = LawStatusRecord.from_config(u'inForce')
    record = DocumentRecord('Law', law_status, datetime.date(1985, 8, 29), {'en': 'title'},
                            office_record, {'en': 'http://my.document.com'})
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
    assert record.article_numbers == []
    assert isinstance(record.articles, list)
    assert isinstance(record.references, list)
    assert record.published


def test_invalid_document_type():
    office_record = OfficeRecord({'en': 'name'})
    with pytest.raises(AttributeError):
        DocumentRecord('invalid', 'runningModifications',
                       datetime.date(1985, 8, 29), {'en': 'title'}, office_record)


def test_future_document():
    office_record = OfficeRecord({'en': 'name'})
    law_status = LawStatusRecord.from_config(u'inForce')
    record = DocumentRecord('Hint', law_status,
                            (datetime.datetime.now().date() + datetime.timedelta(days=7)), {'en': 'title'},
                            office_record, {'en': 'http://my.document.com'})
    assert not record.published


def test_init_with_relation():
    office_record = OfficeRecord({'en': 'name'})
    law_status = LawStatusRecord.from_config(u'inForce')
    articles = [ArticleRecord(law_status, datetime.date(1985, 8, 29), '123.4')]
    references = [
        DocumentRecord('Law', law_status, datetime.date(1985, 8, 29), {'de': 'Titel 1'}, office_record,
                       {'en': 'http://my.document.com'})
    ]
    record = DocumentRecord('Hint', law_status, datetime.date(1985, 8, 29), {'de': 'title'},
                            office_record, {'en': 'http://my.document.com'}, articles=articles,
                            references=references, article_numbers=['test'])
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
    assert record.article_numbers == ['test']
    assert isinstance(record.articles, list)
    assert isinstance(record.references, list)


def test_legal_provision():
    office_record = OfficeRecord({'en': 'name'})
    law_status = LawStatusRecord.from_config(u'inForce')
    legal_provision = LegalProvisionRecord(law_status,
                                           datetime.date(1985, 8, 29),
                                           {'de': 'title'},
                                           office_record)
    assert isinstance(legal_provision.document_type, str)
    assert legal_provision.document_type == 'LegalProvision'
