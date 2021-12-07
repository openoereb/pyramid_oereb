# -*- coding: utf-8 -*-
import pytest
import json

from pyramid.testing import testConfig
from pyramid.path import DottedNameResolver
from shapely.geometry import MultiPolygon, Polygon

from pyramid_oereb.core.config import Config
from pyramid_oereb.core.adapter import DatabaseAdapter
from pyramid_oereb.core.records.disclaimer import DisclaimerRecord
from pyramid_oereb.core.records.extract import ExtractRecord
from pyramid_oereb.core.records.glossary import GlossaryRecord
from pyramid_oereb.core.records.office import OfficeRecord
from pyramid_oereb.core.records.real_estate import RealEstateRecord
from pyramid_oereb.core.records.view_service import ViewServiceRecord

SCHEMA_JSON_EXTRACT_PATH = './tests/resources/schema/20210415/extract.json'
SCHEMA_JSON_VERSIONS_PATH = './tests/resources/schema/20210415/versioning.json'
SCHEMA_JSON_EXTRACT_DATA = './tests/resources/schema/20210415/extractdata.json'
SCHEMA_XML_VERSIONS_PATH = './tests/resources/schema/20210415/Versioning.xsd'
SCHEMA_XML_EXTRACT_PATH = './tests/resources/schema/20210415/Extract.xsd'
SCHEMA_XML_EXTRACT_DATA = './tests/resources/schema/20210415/ExtractData.xsd'


@pytest.fixture(scope='session')
def config_path():
    return 'tests/resources/test_config.yml'


@pytest.fixture(scope='session')
def pyramid_test_config():
    with testConfig() as pyramid_config:
        pyramid_config.include('pyramid_oereb.routes')
        return pyramid_config


@pytest.fixture(scope='session')
@pytest.mark.usefixtures('config_path')
def pyramid_oereb_test_config(config_path):
    # Load the standard test configuration
    Config.init(config_path, configsection='pyramid_oereb', init_data=True)
    return Config


@pytest.fixture(scope='function')
def schema_json_extract():
    with open(SCHEMA_JSON_EXTRACT_PATH) as f:
        return json.load(f)


@pytest.fixture(scope='function')
def schema_xml_extract():
    with open(SCHEMA_XML_EXTRACT_PATH) as f:
        return json.load(f)


@pytest.fixture(scope='function')
def schema_xml_versions():
    with open(SCHEMA_XML_VERSIONS_PATH) as f:
        return json.load(f)


@pytest.fixture(scope='session')
@pytest.mark.usefixtures('pyramid_oereb_test_config')
def dbsession(pyramid_oereb_test_config):
    db_url = pyramid_oereb_test_config.get('app_schema').get('db_connection')
    adapter = DatabaseAdapter()
    adapter.add_connection(db_url)
    return adapter.get_session(db_url)


@pytest.fixture
def DummyRenderInfo():
    class DummyRenderInfo(object):
        name = 'test'
    return DummyRenderInfo


@pytest.fixture
@pytest.mark.usefixture('pyramid_oereb_test_config')
def _get_test_extract(pyramid_oereb_test_config, glossary):
    with pyramid_oereb_test_config():
        view_service = ViewServiceRecord({'de': u'http://geowms.bl.ch'},
                                         1,
                                         1.0,
                                         None)
        real_estate = RealEstateRecord(u'Liegenschaft', u'BL', u'Liestal', 2829, 11395,
                                       MultiPolygon([Polygon([(0, 0), (1, 1), (1, 0)])]),
                                       u'http://www.geocat.ch', u'1000', u'BL0200002829', u'CH775979211712')
        real_estate.set_view_service(view_service)
        real_estate.set_main_page_view_service(view_service)
        office_record = OfficeRecord({'de': u'AGI'}, office_at_web={
            'de': 'https://www.bav.admin.ch/bav/de/home.html'
        })
        resolver = DottedNameResolver()
        date_method_string = (pyramid_oereb_test_config
                              .get('extract')
                              .get('base_data')
                              .get('methods')
                              .get('date'))
        date_method = resolver.resolve(date_method_string)
        update_date_os = date_method(real_estate)
        extract = ExtractRecord(
            real_estate,
            pyramid_oereb_test_config.get_oereb_logo(),
            pyramid_oereb_test_config.get_conferderation_logo(),
            pyramid_oereb_test_config.get_canton_logo(),
            pyramid_oereb_test_config.get_municipality_logo(1234),
            office_record,
            update_date_os,
            disclaimers=[
                DisclaimerRecord({'de': u'Haftungsausschluss'}, {'de': u'Test'})
            ],
            glossaries=glossary,
            general_information=pyramid_oereb_test_config.get_general_information()
        )
        # extract.qr_code = 'VGhpcyBpcyBub3QgYSBRUiBjb2Rl'.encode('utf-8') TODO:
        #    qr_code Must be an image ('base64Binary'), but even with images xml validation
        #    fails on it.
        # extract.electronic_signature = 'Signature'  # TODO: fix signature rendering first
        return extract


@pytest.fixture
@pytest.mark.usefixtures('_get_test_extract')
def get_default_extract(_get_test_extract):
    glossary = [GlossaryRecord({'de': u'Glossar'}, {'de': u'Test'})]
    return _get_test_extract(glossary)


@pytest.fixture
def get_empty_glossary_extract():
    return _get_test_extract([])


@pytest.fixture
def get_none_glossary_extract():
    return _get_test_extract(None)
