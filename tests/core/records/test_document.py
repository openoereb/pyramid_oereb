# -*- coding: utf-8 -*-
import datetime
import pytest
from pyramid_oereb.core.records.law_status import LawStatusRecord

from pyramid_oereb.core.records.documents import DocumentRecord
from pyramid_oereb.core.records.document_types import DocumentTypeRecord
from pyramid_oereb.core.records.office import OfficeRecord


def test_mandatory_fields():
    with pytest.raises(TypeError):
        DocumentRecord('AenderungMitVorwirkung', datetime.date(1985, 8, 29),)


def test_init(law_test_data, pyramid_oereb_test_config):
    office_record = OfficeRecord({'en': 'name'})
    law_status = LawStatusRecord(
        'inKraft', {
            "de": "Rechtskräftig",
            "fr": "En vigueur",
            "it": "In vigore",
            "rm": "En vigur",
            "en": "In force"
        }
    )
    record = DocumentRecord(
        DocumentTypeRecord('GesetzlicheGrundlage', {'de': 'Gesetzliche Grundlage'}),
        1, law_status, {'en': 'title'},
        office_record, datetime.date(1985, 8, 29),
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


def test_invalid_document_type():
    office_record = OfficeRecord({'en': 'name'})
    with pytest.raises(AttributeError):
        DocumentRecord('invalid', 1, 'AenderungMitVorwirkung', {'en': 'title'}, office_record,
                       datetime.date(1985, 8, 29))


@pytest.mark.parametrize(
    'published_from,published_until, result',[
        # tests based on a date
        ((datetime.datetime.now().date() + datetime.timedelta(days=7)), None, False), # future document date
        ((datetime.datetime.now().date() - datetime.timedelta(days=7)), (datetime.datetime.now().date() - datetime.timedelta(days=6)), False), # past document date
        ((datetime.datetime.now().date() - datetime.timedelta(days=7)), None, True), # published document date
        ((datetime.datetime.now().date() - datetime.timedelta(days=7)), (datetime.datetime.now().date() + datetime.timedelta(days=6)), True), # published document date
        # tests based on a datetime
        ((datetime.datetime.now() + datetime.timedelta(days=7)), None, False), # future document date
        ((datetime.datetime.now() - datetime.timedelta(days=7)), (datetime.datetime.now() - datetime.timedelta(days=6)), False), # past document date
        ((datetime.datetime.now() - datetime.timedelta(days=7)), None, True), # published document date
        ((datetime.datetime.now() - datetime.timedelta(days=7)), (datetime.datetime.now() + datetime.timedelta(days=6)), True), # published document date
    ]
)
def test_published(published_from, published_until, result):
    office_record = OfficeRecord({'en': 'name'})
    law_status = LawStatusRecord(
        'inKraft', {
            "de": "Rechtskräftig",
            "fr": "En vigueur",
            "it": "In vigore",
            "rm": "En vigur",
            "en": "In force"
        }
    )
    record = DocumentRecord(
        DocumentTypeRecord('Hinweis',{'de': 'Hinweis'}),
        1, law_status, {'en': 'title'}, office_record,
        published_from,
        published_until=published_until,
        text_at_web={'en': 'http://my.document.com'}
    )
    assert record.published == result


def test_legal_provision(law_test_data):
    office_record = OfficeRecord({'en': 'name'})
    law_status = LawStatusRecord(
        'inKraft', {
            "de": "Rechtskräftig",
            "fr": "En vigueur",
            "it": "In vigore",
            "rm": "En vigur",
            "en": "In force"
        }
    )
    legal_provision = DocumentRecord(
        DocumentTypeRecord('Rechtsvorschrift', {'de': 'Rechtsvorschrift'}),
        1, law_status, {'de': 'title'},
        office_record, datetime.date(1985, 8, 29)
    )
    assert isinstance(legal_provision.document_type, DocumentTypeRecord)
    assert legal_provision.document_type.code == 'Rechtsvorschrift'

def test_wrong_types():
    record = DocumentRecord(
        DocumentTypeRecord('Rechtsvorschrift', {'de': 'Rechtsvorschrift'}),
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


def testarticle_numbers_init():
    record = DocumentRecord(
        DocumentTypeRecord('Rechtsvorschrift', {'de': 'Rechtsvorschrift'}),
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
    assert len(record.article_numbers) == 0
    record = DocumentRecord(
        DocumentTypeRecord('Rechtsvorschrift', {'de': 'Rechtsvorschrift'}),
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
        [1],
        1
    )
    assert len(record.article_numbers) == 1

def test_serialize():
    record = DocumentRecord(
        DocumentTypeRecord('Rechtsvorschrift', {'de': 'Rechtsvorschrift'}),
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
    assert isinstance(record.__str__(), str)

def test_copy():
    record = DocumentRecord(
        DocumentTypeRecord('Rechtsvorschrift', {'de': 'Rechtsvorschrift'}),
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
    copy = record.copy()
    assert isinstance(copy.document_type, DocumentTypeRecord)
    assert isinstance(copy.title, str)
    assert isinstance(copy.index, str)
    assert isinstance(copy.responsible_office, str)
    assert isinstance(copy.abbreviation, str)
    assert isinstance(copy.official_number, str)
    assert isinstance(copy.only_in_municipality, str)
    assert isinstance(copy.text_at_web, str)
    assert isinstance(copy.law_status, str)
    assert isinstance(copy.published_from, str)
    assert isinstance(copy.published_until, str)
    assert isinstance(copy.article_numbers, list)
    assert isinstance(copy.file, int)