# -*- coding: utf-8 -*-
import datetime
import pytest
from pyramid_oereb.core.records.law_status import LawStatusRecord

from pyramid_oereb.core.records.documents import DocumentRecord
from pyramid_oereb.core.records.document_types import DocumentTypeRecord
from pyramid_oereb.core.records.office import OfficeRecord


@pytest.fixture
def law_status_record():
    yield LawStatusRecord(
        'inKraft', {
            "de": "Rechtskräftig",
            "fr": "En vigueur",
            "it": "In vigore",
            "rm": "En vigur",
            "en": "In force"
        }
    )


@pytest.fixture
def document_type_record():
    yield DocumentTypeRecord(
        'GesetzlicheGrundlage',
        {'de': 'Gesetzliche Grundlage'}
    )


@pytest.fixture
def office_record():
    yield OfficeRecord({'en': 'name'})


def test_mandatory_fields():
    with pytest.raises(TypeError):
        DocumentRecord('AenderungMitVorwirkung', datetime.date(1985, 8, 29),)


def test_init(law_status_record, office_record, document_type_record):
    record = DocumentRecord(
        document_type_record,
        1,
        law_status_record,
        {'en': 'title'},
        office_record,
        datetime.date(1985, 8, 29),
        text_at_web={'en': 'http://my.document.com'}
    )
    assert isinstance(record.document_type, DocumentTypeRecord)
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


def test_invalid_document_type(office_record):
    with pytest.raises(AttributeError):
        DocumentRecord(
            'invalid',
            1,
            'AenderungMitVorwirkung',
            {'en': 'title'},
            office_record,
            datetime.date(1985, 8, 29)
        )


@pytest.mark.parametrize(
    'published_from,published_until, result', [
        #  tests based on a date
        #  future document date
        ((datetime.datetime.now().date() + datetime.timedelta(days=7)), None, False),  # noqa: E501
        #  past document date
        ((datetime.datetime.now().date() - datetime.timedelta(days=7)), (datetime.datetime.now().date() - datetime.timedelta(days=6)), False),  # noqa: E501
        #  published document date
        ((datetime.datetime.now().date() - datetime.timedelta(days=7)), None, True),  # noqa: E501
        #  published document date
        ((datetime.datetime.now().date() - datetime.timedelta(days=7)), (datetime.datetime.now().date() + datetime.timedelta(days=6)), True),  # noqa: E501
        #  tests based on a datetime
        #  future document date
        ((datetime.datetime.now() + datetime.timedelta(days=7)), None, False),  # noqa: E501
        #  past document date
        ((datetime.datetime.now() - datetime.timedelta(days=7)), (datetime.datetime.now() - datetime.timedelta(days=6)), False),  # noqa: E501
        #  published document date
        ((datetime.datetime.now() - datetime.timedelta(days=7)), None, True),  # noqa: E501
        #  published document date
        ((datetime.datetime.now() - datetime.timedelta(days=7)), (datetime.datetime.now() + datetime.timedelta(days=6)), True)  # noqa: E501
    ]
)
def test_published(published_from, published_until, result, law_status_record, office_record, document_type_record):  # noqa: E501
    record = DocumentRecord(
        document_type_record,
        1,
        law_status_record,
        {'en': 'title'},
        office_record,
        published_from,
        published_until=published_until,
        text_at_web={'en': 'http://my.document.com'}
    )
    assert record.published == result


def test_legal_provision(law_test_data, law_status_record, office_record, document_type_record):
    legal_provision = DocumentRecord(
        document_type_record,
        1,
        law_status_record,
        {'de': 'title'},
        office_record,
        datetime.date(1985, 8, 29)
    )
    assert isinstance(legal_provision.document_type, DocumentTypeRecord)
    assert legal_provision.document_type.code == 'GesetzlicheGrundlage'


def test_wrong_types(document_type_record):
    with pytest.warns(UserWarning):
        record = DocumentRecord(
            document_type_record,
            'wrong_type',
            'law_status',
            'wrong_title',
            'office_record',
            'date_from',
            'date_until',
            'text_at_web',
            'abbreviation',
            'official_number',
            'only_in_municipality',
            'article_numbers',
            1
        )
    assert isinstance(record.title, str)
    assert isinstance(record.index, str)
    assert isinstance(record.responsible_office, str)
    assert isinstance(record.abbreviation, str)
    assert isinstance(record.official_number, str)
    assert isinstance(record.only_in_municipality, str)
    assert isinstance(record.text_at_web, str)
    assert isinstance(record.law_status, str)
    assert isinstance(record.published_from, str)
    assert isinstance(record.published_until, str)
    assert isinstance(record.article_numbers, list)
    assert isinstance(record.file, int)


def testarticle_numbers_init(law_status_record, office_record, document_type_record):
    record = DocumentRecord(
        document_type_record,
        1,
        law_status_record,
        {'en': 'title'},
        office_record,
        datetime.date(1985, 8, 29),
        text_at_web={'en': 'http://my.document.com'},
        article_numbers=[]
    )
    assert len(record.article_numbers) == 0
    record = DocumentRecord(
        document_type_record,
        1,
        law_status_record,
        {'en': 'title'},
        office_record,
        datetime.date(1985, 8, 29),
        text_at_web={'en': 'http://my.document.com'},
        article_numbers=[1]
    )
    assert len(record.article_numbers) == 1


def test_serialize(law_status_record, office_record, document_type_record):
    record = DocumentRecord(
        document_type_record,
        1,
        law_status_record,
        {'en': 'title'},
        office_record,
        datetime.date(1985, 8, 29),
        text_at_web={'en': 'http://my.document.com'},
        article_numbers=[1]
    )
    assert isinstance(record.__str__(), str)


def test_copy(law_status_record, office_record, document_type_record):
    record = DocumentRecord(
        document_type=document_type_record,
        index=1,
        law_status=law_status_record,
        title={'en': 'title'},
        responsible_office=office_record,
        published_from=datetime.date(1985, 8, 29),
        published_until=datetime.date(2121, 2, 12),
        text_at_web={'en': 'http://my.document.com'},
        abbreviation={'en': 'my abbreviation'},
        official_number={'en': 'some official number'},
        only_in_municipality=4600,
        article_numbers=[1],
        file=bytes(),
        identifier=None
    )
    copy = record.copy()
    assert isinstance(copy.document_type, DocumentTypeRecord)
    assert isinstance(copy.title, dict)
    assert isinstance(copy.index, int)
    assert isinstance(copy.responsible_office, OfficeRecord)
    assert isinstance(copy.abbreviation, dict)
    assert isinstance(copy.official_number, dict)
    assert isinstance(copy.only_in_municipality, int)
    assert isinstance(copy.text_at_web, dict)
    assert isinstance(copy.law_status, LawStatusRecord)
    assert isinstance(copy.published_from, datetime.date)
    assert isinstance(copy.published_until, datetime.date)
    assert isinstance(copy.article_numbers, list)
    assert isinstance(copy.file, bytes)
