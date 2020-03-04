# -*- coding: utf-8 -*-

import datetime

import pytest
import requests_mock
from geolink_formatter.entity import Document, File
from requests.auth import HTTPBasicAuth

from pyramid_oereb.contrib.sources.document import OEREBlexSource
from pyramid_oereb.lib.records.documents import DocumentRecord, LegalProvisionRecord, HintRecord
from pyramid_oereb.lib.records.office import OfficeRecord
from tests.mockrequest import MockParameter


@pytest.mark.parametrize('valid,cfg', [
    (True, {
        'host': 'http://oereblex.example.com',
        'language': 'de',
        'canton': 'BL'
    }),
    (False, {
        'language': 'de',
        'canton': 'BL'
    }),
    (False, {
        'host': 'http://oereblex.example.com',
        'language': 'german',
        'canton': 'BL'
    }),
    (False, {
        'host': 'http://oereblex.example.com',
        'language': 'de'
    })
])
def test_init(valid, cfg):
    if valid:
        assert isinstance(OEREBlexSource(**cfg), OEREBlexSource)
    else:
        with pytest.raises(AssertionError):
            OEREBlexSource(**cfg)


@pytest.mark.parametrize('key,language,result', [
    ('official_title', None, None),
    ('municipality', None, 'Liestal'),
    ('municipality', 'de', {'de': 'Liestal'})
])
def test_get_mapped_value(key, language, result):
    file_ = File('Test', '/api/attachments/1', 'main')
    document = Document(id='test', title='Test', category='main', doctype='decree', files=[file_],
                        enactment_date=datetime.date.today(), subtype='Liestal', authority='Office')
    source = OEREBlexSource(host='http://oereblex.example.com', language='de', canton='BL',
                            mapping={'municipality': 'subtype'})
    assert source._get_mapped_value(document, key, language=language) == result


@pytest.mark.parametrize('i,document', [
    (1, Document(
        id='doc1',
        title='Document 1',
        category='main',
        doctype='edict',
        authority='Office',
        files=[File('File 1', '/api/attachments/1', 'main')],
        enactment_date=datetime.date.today()
    )),
    (2, Document(
        id='doc2',
        title='Document 2',
        category='main',
        doctype='decree',
        authority='Office',
        files=[
            File('File 2', '/api/attachments/2', 'main'),
            File('File 3', '/api/attachments/3', 'additional')
        ],
        enactment_date=datetime.date.today()
    )),
    (3, Document(
        id='doc1',
        title='Document 1',
        category='main',
        doctype='invalid',
        authority='Office',
        files=[File('File 1', '/api/attachments/1', 'main')],
        enactment_date=datetime.date.today()
    )),
    (4, Document(
        id='doc1',
        title='Document 1',
        category='main',
        doctype='decree',
        authority='Office',
        files=[],
        enactment_date=datetime.date.today()
    ))
])
def test_get_document_records(i, document):
    language = 'de'
    source = OEREBlexSource(host='http://oereblex.example.com', language='de', canton='BL')
    references = [
        Document(
            id='ref',
            title='Reference',
            category='related',
            doctype='edict',
            authority='Office',
            files=[File('Reference file', '/api/attachments/4', 'main')],
            enactment_date=datetime.date.today()
        )
    ]

    if i == 3:
        with pytest.raises(TypeError):
            source._get_document_records(document, language, references)
    elif i == 4:
        assert source._get_document_records(document, language, references) == []
    else:
        records = source._get_document_records(document, language, references)
        assert len(records) == i
        for idx, record in enumerate(records):
            if i == 1:
                assert isinstance(record, DocumentRecord)
            elif i == 2:
                assert isinstance(record, LegalProvisionRecord)
            assert record.title == {'de': 'Document {0}'.format(i)}
            assert record.published_from == datetime.date.today()
            assert record.canton == 'BL'
            assert record.text_at_web == {'de': '/api/attachments/{fid}'.format(fid=i + idx)}
            assert len(record.references) == 1
            reference = record.references[0]
            assert isinstance(reference, DocumentRecord)
            assert reference.title == {'de': 'Reference'}
            assert reference.canton == 'BL'
            assert reference.text_at_web == {'de': '/api/attachments/4'}


def test_read():
    with requests_mock.mock() as m:
        with open('./tests/resources/geolink_v1.2.0.xml', 'rb') as f:
            m.get('http://oereblex.example.com/api/geolinks/100.xml', content=f.read())
        source = OEREBlexSource(host='http://oereblex.example.com', language='de', canton='BL')
        source.read(MockParameter(), 100)
        assert len(source.records) == 5
        document = source.records[0]
        assert isinstance(document, DocumentRecord)
        assert isinstance(document.responsible_office, OfficeRecord)
        assert document.responsible_office.name == {'de': 'Bauverwaltung Gemeinde'}
        assert document.canton == 'BL'
        assert document.text_at_web == {
            'de': 'http://oereblex.example.com/api/attachments/4735'
        }
        assert len(document.references) == 4


def test_read_related_decree_as_main():
    with requests_mock.mock() as m:
        with open('./tests/resources/geolink_v1.2.0.xml', 'rb') as f:
            m.get('http://oereblex.example.com/api/geolinks/100.xml', content=f.read())
        source = OEREBlexSource(host='http://oereblex.example.com', language='de', canton='BL',
                                related_decree_as_main=True)
        source.read(MockParameter(), 100)
        assert len(source.records) == 5
        document = source.records[0]
        assert isinstance(document, DocumentRecord)
        assert isinstance(document.responsible_office, OfficeRecord)
        assert document.responsible_office.name == {'de': 'Bauverwaltung Gemeinde'}
        assert document.canton == 'BL'
        assert document.text_at_web == {
            'de': 'http://oereblex.example.com/api/attachments/4735'
        }
        assert len(document.references) == 4


def test_read_related_notice_as_main():
    with requests_mock.mock() as m:
        with open('./tests/resources/geolink_v1.2.0.xml', 'rb') as f:
            m.get('http://oereblex.example.com/api/geolinks/100.xml', content=f.read())
        source = OEREBlexSource(host='http://oereblex.example.com', language='de', canton='BL',
                                related_notice_as_main=True)
        source.read(MockParameter(), 100)
        assert len(source.records) == 6
        document = source.records[5]
        assert isinstance(document, HintRecord)
        assert isinstance(document.responsible_office, OfficeRecord)
        assert document.responsible_office.name == {'de': '-'}
        assert document.responsible_office.office_at_web is None
        assert document.published_from == datetime.date(1970, 1, 1)
        assert len(document.references) == 3


def test_read_with_version_in_url():
    with requests_mock.mock() as m:
        with open('./tests/resources/geolink_v1.2.0.xml', 'rb') as f:
            m.get('http://oereblex.example.com/api/1.2.0/geolinks/100.xml', content=f.read())
        source = OEREBlexSource(host='http://oereblex.example.com', language='de', canton='BL',
                                pass_version=True)
        source.read(MockParameter(), 100)
        assert len(source.records) == 5


def test_read_with_specified_version():
    with requests_mock.mock() as m:
        with open('./tests/resources/geolink_v1.0.0.xml', 'rb') as f:
            m.get('http://oereblex.example.com/api/1.0.0/geolinks/100.xml', content=f.read())
        source = OEREBlexSource(host='http://oereblex.example.com', language='de', canton='BL',
                                pass_version=True, version='1.0.0')
        source.read(MockParameter(), 100)
        assert len(source.records) == 2


def test_read_with_specified_language():
    with requests_mock.mock() as m:
        with open('./tests/resources/geolink_v1.2.0.xml', 'rb') as f:
            m.get('http://oereblex.example.com/api/geolinks/100.xml?locale=fr', content=f.read())
        source = OEREBlexSource(host='http://oereblex.example.com', language='de', canton='BL')
        params = MockParameter()
        params.set_language('fr')
        source.read(params, 100)
        assert len(source.records) == 5
        document = source.records[0]
        assert document.responsible_office.name == {'fr': 'Bauverwaltung Gemeinde'}
        assert document.text_at_web == {
            'fr': 'http://oereblex.example.com/api/attachments/4735'
        }


def test_authentication():
    auth = {
        'username': 'test',
        'password': 'test'
    }
    source = OEREBlexSource(host='http://oereblex.example.com', language='de', canton='BL', auth=auth)
    assert isinstance(source._auth, HTTPBasicAuth)


def test_get_document_title():
    document = Document([], id='1', title='Test')
    result = {'de': 'Test'}
    assert OEREBlexSource._get_document_title(document, File(), 'de') == result
