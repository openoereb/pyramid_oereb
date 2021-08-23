# -*- coding: utf-8 -*-

import datetime

import pytest
import requests_mock
from geolink_formatter.entity import Document, File
from requests.auth import HTTPBasicAuth

from pyramid_oereb.contrib.sources.document import OEREBlexSource
from pyramid_oereb.lib.records.documents import DocumentRecord
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
    }),
    (True, {
        'host': 'http://oereblex.example.com',
        'language': 'de',
        'canton': 'BL',
        'url_param_config': [{'code': 'ForestPerimeters', 'url_param': 'oereb_id=5'},
                             {'code': 'LandUsePlans', 'url_param': 'oereb_id=15'}]
    }),
    (False, {
        'host': 'http://oereblex.example.com',
        'language': 'de',
        'canton': 'BL',
        'url_param_config': {'code': 'ForestPerimeters', 'url_param': 'oereb_id=5'}
    }),
    (False, {
        'host': 'http://oereblex.example.com',
        'language': 'de',
        'canton': 'BL',
        'url_param_config': ['oereb_id=5', 'oereb_id=15']
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
        files=[File(href='/api/attachments/1', category='main')],
        enactment_date=datetime.date.today()
    )),
    (2, Document(
        id='doc2',
        title='Document 2',
        category='main',
        doctype='decree',
        authority='Office',
        files=[
            File(href='/api/attachments/2', category='main'),
            File(href='/api/attachments/3', category='additional')
        ],
        enactment_date=datetime.date.today()
    )),
    (3, Document(
        id='doc1',
        title='Document 1',
        category='main',
        doctype='invalid',
        authority='Office',
        files=[File(href='/api/attachments/1', category='main')],
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

    if i == 3:
        with pytest.raises(TypeError):
            source._get_document_records(document, language)
    elif i == 4:
        assert source._get_document_records(document, language) == []
    else:
        records = source._get_document_records(document, language)
        assert len(records) == i
        for idx, record in enumerate(records):
            assert isinstance(record, DocumentRecord)
            if i == 1:
                record.document_type == 'GesetzlicheGrundlage'
            elif i == 2:
                record.document_type == 'Rechtsvorschrift'
            assert record.title == {'de': 'Document {0}'.format(i)}
            assert record.published_from == datetime.date.today()
            assert record.text_at_web == {'de': '/api/attachments/{fid}'.format(fid=i + idx)}


def test_read():
    with requests_mock.mock() as m:
        with open('./tests/resources/geolink_v1.2.1.xml', 'rb') as f:
            m.get('http://oereblex.example.com/api/geolinks/100.xml', content=f.read())
        source = OEREBlexSource(
            host='http://oereblex.example.com',
            language='de',
            canton='BL',
            version='1.2.1'
        )
        source.read(MockParameter(), 100)
        assert len(source.records) == 9
        document = source.records[0]
        assert isinstance(document, DocumentRecord)
        assert isinstance(document.responsible_office, OfficeRecord)
        assert document.responsible_office.name == {'de': 'Bauverwaltung Gemeinde'}
        assert document.text_at_web == {
            'de': 'http://oereblex.example.com/api/attachments/4735'
        }


def test_read_related_decree_as_main():
    with requests_mock.mock() as m:
        with open('./tests/resources/geolink_v1.2.1.xml', 'rb') as f:
            m.get('http://oereblex.example.com/api/geolinks/100.xml', content=f.read())
        source = OEREBlexSource(
            host='http://oereblex.example.com',
            language='de',
            canton='BL',
            version='1.2.1',
            related_decree_as_main=True
        )
        source.read(MockParameter(), 100)
        assert len(source.records) == 9
        document = source.records[0]
        assert isinstance(document, DocumentRecord)
        assert isinstance(document.responsible_office, OfficeRecord)
        assert document.responsible_office.name == {'de': 'Bauverwaltung Gemeinde'}
        assert document.text_at_web == {
            'de': 'http://oereblex.example.com/api/attachments/4735'
        }


def test_read_related_notice_as_main():
    with requests_mock.mock() as m:
        with open('./tests/resources/geolink_v1.2.1.xml', 'rb') as f:
            m.get('http://oereblex.example.com/api/geolinks/100.xml', content=f.read())
        source = OEREBlexSource(
            host='http://oereblex.example.com',
            language='de',
            canton='BL',
            version='1.2.1',
            related_notice_as_main=True
        )
        source.read(MockParameter(), 100)
        assert len(source.records) == 9
        document = source.records[8]
        assert isinstance(document, DocumentRecord)
        assert document.document_type == 'Hinweis'
        assert isinstance(document.responsible_office, OfficeRecord)
        assert document.responsible_office.name == {'de': '-'}
        assert document.responsible_office.office_at_web is None
        assert document.published_from == datetime.date(1970, 1, 1)


def test_read_with_version_in_url():
    with requests_mock.mock() as m:
        with open('./tests/resources/geolink_v1.2.1.xml', 'rb') as f:
            m.get('http://oereblex.example.com/api/1.2.1/geolinks/100.xml', content=f.read())
        source = OEREBlexSource(
            host='http://oereblex.example.com',
            language='de',
            canton='BL',
            version='1.2.1',
            pass_version=True
        )
        source.read(MockParameter(), 100)
        assert len(source.records) == 9


def test_read_with_specified_version():
    with requests_mock.mock() as m:
        with open('./tests/resources/geolink_v1.2.1.xml', 'rb') as f:
            m.get('http://oereblex.example.com/api/1.2.1/geolinks/100.xml', content=f.read())
        source = OEREBlexSource(
            host='http://oereblex.example.com',
            language='de',
            canton='BL',
            version='1.2.1',
            pass_version=True
        )
        source.read(MockParameter(), 100)
        assert len(source.records) == 9


def test_read_with_specified_language():
    with requests_mock.mock() as m:
        with open('./tests/resources/geolink_v1.2.1.xml', 'rb') as f:
            m.get('http://oereblex.example.com/api/geolinks/100.xml?locale=fr', content=f.read())
        source = OEREBlexSource(
            host='http://oereblex.example.com',
            language='de',
            canton='BL',
            version='1.2.1'
        )
        params = MockParameter()
        params.set_language('fr')
        source.read(params, 100)
        assert len(source.records) == 9
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


def test_get_multilingual():
    document = Document([], id='1', title='Test')
    result = {'de': 'Test'}
    assert OEREBlexSource._get_multilingual(document.title, 'de') == result
    assert OEREBlexSource._get_multilingual(None, 'de') is None
