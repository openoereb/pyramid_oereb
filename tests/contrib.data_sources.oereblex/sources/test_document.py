# -*- coding: utf-8 -*-

import datetime
from pyramid_oereb.core.records.law_status import LawStatusRecord

import pytest
import yaml
import requests_mock
from unittest.mock import patch
from geolink_formatter.entity import Document, File
from requests.auth import HTTPBasicAuth

from pyramid_oereb.contrib.data_sources.oereblex.sources.document import OEREBlexSource
from pyramid_oereb.core.records.document_types import DocumentTypeRecord
from pyramid_oereb.core.records.documents import DocumentRecord
from pyramid_oereb.core.records.office import OfficeRecord
from pyramid_oereb.core.config import Config
from tests.mockrequest import MockParameter


@pytest.fixture
def forest_perimeters_config():
    yield yaml.safe_load('''
      code: ch.Waldabstandslinien
      source:
        class: pyramid_oereb.contrib.data_sources.oereblex.sources.plr_oereblex.DatabaseOEREBlexSource
        params:
          db_connection: main_db_connection
          model_factory: pyramid_oereb.contrib.data_sources.oereblex.models.theme.model_factory_string_pk
          schema_name: forest_perimeters
      document_types_lookup:
        - data_code: decree
          transfer_code: Rechtsvorschrift
          extract_code: LegalProvision
        - data_code: edict
          transfer_code: GesetzlicheGrundlage
          extract_code: Law
        - data_code: notice
          transfer_code: Hinweis
          extract_code: Hint
      law_status_lookup:
        - data_code: inKraft
          transfer_code: inKraft
          extract_code: inForce
        - data_code: AenderungMitVorwirkung
          transfer_code: AenderungMitVorwirkung
          extract_code: changeWithPreEffect
        - data_code: AenderungOhneVorwirkung
          transfer_code: AenderungOhneVorwirkung
          extract_code: changeWithoutPreEffect
          ''')


@pytest.fixture
def oereblex_test_config(pyramid_oereb_test_config, law_status_test_data, document_type_test_data,
                         forest_perimeters_config):
    with patch(
        'pyramid_oereb.core.config.Config.get_theme_config_by_code', return_value=forest_perimeters_config
    ), patch.object(
      Config, 'law_status', law_status_test_data
    ), patch.object(
      Config, 'document_types', document_type_test_data):
        yield pyramid_oereb_test_config


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
        'url_param_config': [{'code': 'ch.StatischeWaldgrenzen', 'url_param': 'oereb_id=5'},
                             {'code': 'ch.Nutzungsplanung', 'url_param': 'oereb_id=15'}]
    }),
    (False, {
        'host': 'http://oereblex.example.com',
        'language': 'de',
        'canton': 'BL',
        'url_param_config': {'code': 'ch.StatischeWaldgrenzen', 'url_param': 'oereb_id=5'}
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
        enactment_date=datetime.date.today(),
        index=1
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
        enactment_date=datetime.date.today(),
        index=2
    )),
    (3, Document(
        id='doc3',
        title='Document 3',
        category='main',
        doctype='prepublication',
        authority='Office',
        files=[File(href='/api/attachments/3', category='main')],
        status_start_date=datetime.date.today(),
        index=1
    )),
    (4, Document(
        id='doc4',
        title='Document 4',
        category='main',
        doctype='decree',
        authority='Office',
        files=[],
        enactment_date=datetime.date.today()
    )),
    (5, Document(
        id='doc5',
        title='Document 5',
        category='main',
        doctype='invalid',
        authority='Office',
        files=[File(href='/api/attachments/1', category='main')],
        enactment_date=datetime.date.today()
    ))
])
def test_get_document_records(oereblex_test_config, i, document):
    del oereblex_test_config

    language = 'de'
    source = OEREBlexSource(host='http://oereblex.example.com', language='de', canton='BL',
                            code='ch.Waldabstandslinien')

    if i == 5:
        with pytest.raises(RuntimeError):
            source._get_document_records(document, language)
    elif i == 4:
        assert source._get_document_records(document, language) == []
    else:
        records = source._get_document_records(document, language)
        if i == 1:
            assert len(records) == 1
        elif i == 2:
            assert len(records) == 2
        elif i == 3:
            assert len(records) == 1
        for idx, record in enumerate(records):
            assert isinstance(record, DocumentRecord)
            if i == 1:
                record.document_type == 'GesetzlicheGrundlage'
                assert record.index == 1
            elif i == 2:
                record.document_type == 'Rechtsvorschrift'
                assert record.index == 2
            elif i == 3:
                record.document_type == 'Rechtsvorschrift'
                assert record.index == 1
            else:
                assert record.index is None
            assert record.title == {'de': 'Document {0}'.format(i)}
            assert record.published_from == datetime.date.today()
            assert record.text_at_web == {'de': '/api/attachments/{fid}'.format(fid=i + idx)}


@pytest.mark.parametrize('law_status,service', [
    (LawStatusRecord('inForce', {'de': 'Rechtskräftig'}), 'geolinks'),
    (LawStatusRecord('changeWithPreEffect', {'de': 'Änderung mit Vorwirkung'}), 'prepubs')
])
def test_read(law_status, service, oereblex_test_config):
    del oereblex_test_config

    with requests_mock.mock() as m:
        with open('./tests/resources/geolink_v1.2.2.xml', 'rb') as f:
            m.get(
                'http://oereblex.example.com/api/{0}/100.xml'.format(service),
                content=f.read()
            )
        source = OEREBlexSource(
            host='http://oereblex.example.com',
            language='de',
            canton='BL',
            version='1.2.2',
            code='ch.Waldabstandslinien',
            use_prepubs=True
        )
        source.read(MockParameter(), 100, law_status)
        assert len(source.records) == 9
        document = source.records[0]
        assert isinstance(document, DocumentRecord)
        assert isinstance(document.responsible_office, OfficeRecord)
        assert document.responsible_office.name == {'de': 'Bauverwaltung Gemeinde'}
        assert document.text_at_web == {
            'de': 'http://oereblex.example.com/api/attachments/4735'
        }
        assert document.index == 30


def test_read_related_decree_as_main(oereblex_test_config):
    del oereblex_test_config

    with requests_mock.mock() as m:
        with open('./tests/resources/geolink_v1.2.2.xml', 'rb') as f:
            m.get('http://oereblex.example.com/api/geolinks/100.xml', content=f.read())
        source = OEREBlexSource(
            host='http://oereblex.example.com',
            language='de',
            canton='BL',
            version='1.2.2',
            related_decree_as_main=True,
            code='ch.Waldabstandslinien',
        )
        source.read(MockParameter(), 100, LawStatusRecord('inForce', {'de': 'Rechtskräftig'}))
        assert len(source.records) == 9
        document = source.records[0]
        assert isinstance(document, DocumentRecord)
        assert isinstance(document.responsible_office, OfficeRecord)
        assert document.responsible_office.name == {'de': 'Bauverwaltung Gemeinde'}
        assert document.text_at_web == {
            'de': 'http://oereblex.example.com/api/attachments/4735'
        }
        assert document.index == 30


def test_read_related_notice_as_main(oereblex_test_config):
    del oereblex_test_config

    with requests_mock.mock() as m:
        with open('./tests/resources/geolink_v1.2.2.xml', 'rb') as f:
            m.get('http://oereblex.example.com/api/geolinks/100.xml', content=f.read())
        source = OEREBlexSource(
            host='http://oereblex.example.com',
            language='de',
            canton='BL',
            version='1.2.2',
            related_notice_as_main=True,
            code='ch.Waldabstandslinien',
        )
        source.read(MockParameter(), 100, LawStatusRecord('inForce', {'de': 'Rechtskräftig'}))
        assert len(source.records) == 9
        document = source.records[8]
        assert isinstance(document, DocumentRecord)
        assert isinstance(document.document_type, DocumentTypeRecord)
        assert document.document_type.code == 'Hint'
        assert isinstance(document.responsible_office, OfficeRecord)
        assert document.responsible_office.name == {'de': '-'}
        assert document.responsible_office.office_at_web is None
        assert source.records[0].responsible_office.office_at_web == {
            'de': "http%3A%2F%2Fwww.zihlschlacht-sitterdorf.ch"
        }
        assert document.published_from == datetime.date(1970, 1, 1)
        assert document.index == 40


def test_read_with_version_in_url(oereblex_test_config):
    del oereblex_test_config

    with requests_mock.mock() as m:
        with open('./tests/resources/geolink_v1.2.2.xml', 'rb') as f:
            m.get('http://oereblex.example.com/api/1.2.2/geolinks/100.xml', content=f.read())
        source = OEREBlexSource(
            host='http://oereblex.example.com',
            language='de',
            canton='BL',
            version='1.2.2',
            pass_version=True,
            code='ch.Waldabstandslinien',
        )
        source.read(MockParameter(), 100, LawStatusRecord('inForce', {'de': 'Rechtskräftig'}))
        assert len(source.records) == 9


def test_read_with_specified_version(oereblex_test_config):
    del oereblex_test_config

    with requests_mock.mock() as m:
        with open('./tests/resources/geolink_v1.2.2.xml', 'rb') as f:
            m.get('http://oereblex.example.com/api/1.2.2/geolinks/100.xml', content=f.read())
        source = OEREBlexSource(
            host='http://oereblex.example.com',
            language='de',
            canton='BL',
            version='1.2.2',
            pass_version=True,
            code='ch.Waldabstandslinien',
        )
        source.read(MockParameter(), 100, LawStatusRecord('inForce', {'de': 'Rechtskräftig'}))
        assert len(source.records) == 9


def test_read_with_specified_language(oereblex_test_config):
    with requests_mock.mock() as m:
        with open('./tests/resources/geolink_v1.2.2.xml', 'rb') as f:
            m.get('http://oereblex.example.com/api/geolinks/100.xml?locale=fr', content=f.read())
        source = OEREBlexSource(
            host='http://oereblex.example.com',
            language='de',
            canton='BL',
            version='1.2.2',
            code='ch.Waldabstandslinien',
        )
        params = MockParameter()
        params.set_language('fr')
        source.read(params, 100, LawStatusRecord('inForce', {'de': 'Rechtskräftig'}))
        assert len(source.records) == 9
        document = source.records[0]
        assert document.responsible_office.name == {'fr': 'Bauverwaltung Gemeinde'}
        assert document.text_at_web == {
            'fr': 'http://oereblex.example.com/api/attachments/4735'
        }
        assert document.index == 30


def test_authentication():
    auth = {
        'username': 'test',
        'password': 'test'
    }
    source = OEREBlexSource(host='http://oereblex.example.com', language='de', canton='BL', auth=auth,
                            code='ch.Waldabstandslinien')
    assert isinstance(source._auth, HTTPBasicAuth)


def test_get_multilingual():
    document = Document([], id='1', title='Test')
    result = {'de': 'Test'}
    assert OEREBlexSource._get_multilingual(document.title, 'de') == result
    assert OEREBlexSource._get_multilingual(None, 'de') is None
