# -*- coding: utf-8 -*-
import datetime
import pytest

from pyramid_oereb.lib.records.documents import DocumentRecord, ArticleRecord
from pyramid_oereb.lib.records.office import OfficeRecord


def test_get_fields():
    expected_fields = [
        'text_at_web',
        'legal_state',
        'published_from',
        'title',
        'official_title',
        'responsible_office',
        'abbreviation',
        'official_number',
        'canton',
        'municipality',
        'article_numbers',
        'file',
        'articles',
        'references'
    ]
    fields = DocumentRecord.get_fields()
    assert fields == expected_fields


def test_mandatory_fields():
    with pytest.raises(TypeError):
        DocumentRecord('runningModifications', datetime.date(1985, 8, 29))


def test_init():
    office_record = OfficeRecord('name')
    record = DocumentRecord('runningModifications', datetime.date(1985, 8, 29), 'title', office_record)
    assert isinstance(record.legal_state, str)
    assert isinstance(record.published_from, datetime.date)
    assert isinstance(record.title, str)
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


def test_init_with_relation():
    office_record = OfficeRecord('name')
    articles = [ArticleRecord('runningModifications', datetime.date(1985, 8, 29), '123.4')]
    references = [
        DocumentRecord('runningModifications', datetime.date(1985, 8, 29), 'Titel 1', office_record)
    ]
    record = DocumentRecord('runningModifications', datetime.date(1985, 8, 29), 'title', office_record,
                            articles=articles, references=references, article_numbers=['test'])
    assert isinstance(record.legal_state, str)
    assert isinstance(record.published_from, datetime.date)
    assert isinstance(record.title, str)
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


def test_to_extract():
    office_record = OfficeRecord('Office')
    articles = [ArticleRecord('runningModifications', datetime.date(1985, 8, 29), '123.4')]
    references = [
        DocumentRecord('runningModifications', datetime.date(1985, 8, 29), 'Reference', office_record)
    ]
    record = DocumentRecord('runningModifications', datetime.date(1985, 8, 29), 'Document', office_record,
                            articles=articles, references=references, article_numbers=['test'])
    assert record.to_extract() == {
        'legal_state': 'runningModifications',
        'title': 'Document',
        'responsible_office': {
            'name': 'Office'
        },
        'article_numbers': ['test'],
        'articles': [
            {
                'legal_state': 'runningModifications',
                'number': '123.4'
            }
        ],
        'references': [
            {
                'legal_state': 'runningModifications',
                'title': 'Reference',
                'responsible_office': {
                    'name': 'Office'
                }
            }
        ]
    }
