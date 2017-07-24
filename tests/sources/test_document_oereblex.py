# -*- coding: utf-8 -*-

import datetime

import pytest
import requests_mock
from geolink_formatter.entity import Document, File

from pyramid_oereb.contrib.sources.document import OEREBlexSource
from pyramid_oereb.lib.records.documents import DocumentRecord, LegalProvisionRecord
from pyramid_oereb.lib.records.office import OfficeRecord


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


@pytest.mark.parametrize('key,multilingual,result', [
    ('official_title', False, None),
    ('municipality', False, 'Liestal'),
    ('municipality', True, {'de': 'Liestal'})
])
def test_get_mapped_value(key, multilingual, result):
    file_ = File('Test', '/api/attachments/1', 'main')
    document = Document('test', 'Test', 'main', 'decree', [file_], datetime.date.today(), subtype='Liestal')
    source = OEREBlexSource(host='http://oereblex.example.com', language='de', canton='BL',
                            mapping={'municipality': 'subtype'})
    assert source._get_mapped_value(document, key, multilingual) == result


@pytest.mark.parametrize('i,document', [
    (1, Document(
        id='doc1',
        title='Document 1',
        category='main',
        doctype='edict',
        files=[File('File 1', '/api/attachments/1', 'main')],
        enactment_date=datetime.date.today()
    )),
    (2, Document(
        id='doc2',
        title='Document 2',
        category='main',
        doctype='decree',
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
        files=[File('File 1', '/api/attachments/1', 'main')],
        enactment_date=datetime.date.today()
    ))
])
def test_get_document_records(i, document):
    source = OEREBlexSource(host='http://oereblex.example.com', language='de', canton='BL')
    references = [
        Document(
            id='ref',
            title='Reference',
            category='related',
            doctype='edict',
            files=[File('Reference file', '/api/attachments/4', 'main')],
            enactment_date=datetime.date.today()
        )
    ]

    if i == 3:
        with pytest.raises(TypeError):
            source._get_document_records(document, references)
    else:
        records = source._get_document_records(document, references)
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
        with open('./tests/resources/geolink.xml', 'rb') as f:
            m.get('http://oereblex.example.com/api/geolinks/100.xml', content=f.read())
        source = OEREBlexSource(host='http://oereblex.example.com', language='de', canton='BL')
        source.read(100)
        assert len(source.records) == 2
        document = source.records[0]
        assert isinstance(document, DocumentRecord)
        assert isinstance(document.responsible_office, OfficeRecord)
        assert document.responsible_office.name == {'de': 'Landeskanzlei'}
        assert document.canton == 'BL'
        assert document.text_at_web == {
            'de': 'http://oereblex.example.com/api/attachments/313'
        }
        assert len(document.references) == 4
