# -*- coding: utf-8 -*-
import datetime
import pytest

from pyramid_oereb.lib.records.documents import DocumentRecord, ArticleRecord
from pyramid_oereb.lib.records.office import OfficeRecord


def test_mandatory_fields():
    with pytest.raises(TypeError):
        DocumentRecord('runningModifications', datetime.date(1985, 8, 29))


def test_init():
    office_record = OfficeRecord({'en': 'name'})
    record = DocumentRecord('runningModifications', datetime.date(1985, 8, 29), {'en': 'title'},
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
    assert record.article_numbers == []
    assert isinstance(record.articles, list)
    assert isinstance(record.references, list)
    assert record.published


def test_future_document():
    office_record = OfficeRecord({'en': 'name'})
    record = DocumentRecord('runningModifications',
                            (datetime.datetime.now().date() + datetime.timedelta(days=7)), {'en': 'title'},
                            office_record)
    assert not record.published


def test_init_with_relation():
    office_record = OfficeRecord({'en': 'name'})
    articles = [ArticleRecord('runningModifications', datetime.date(1985, 8, 29), '123.4')]
    references = [
        DocumentRecord('runningModifications', datetime.date(1985, 8, 29), {'de': 'Titel 1'}, office_record)
    ]
    record = DocumentRecord('runningModifications', datetime.date(1985, 8, 29), {'de': 'title'},
                            office_record, articles=articles, references=references, article_numbers=['test'])
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
    assert record.article_numbers == ['test']
    assert isinstance(record.articles, list)
    assert isinstance(record.references, list)
