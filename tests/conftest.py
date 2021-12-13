# -*- coding: utf-8 -*-
import pytest
import json
import yaml
from io import StringIO
from urllib.parse import urlsplit, urlunsplit
from unittest.mock import patch

from pyramid.testing import testConfig
from pyramid.path import DottedNameResolver
from shapely.geometry import MultiPolygon, Polygon
from sqlalchemy import create_engine, orm

from pyramid_oereb.core.config import Config
from pyramid_oereb.core.records.disclaimer import DisclaimerRecord
from pyramid_oereb.core.records.extract import ExtractRecord
from pyramid_oereb.core.records.glossary import GlossaryRecord
from pyramid_oereb.core.records.office import OfficeRecord
from pyramid_oereb.core.records.real_estate import RealEstateRecord
from pyramid_oereb.core.records.view_service import ViewServiceRecord
from pyramid_oereb.contrib.data_sources.create_tables import create_tables_from_standard_configuration

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
def base_engine(test_db_url):
    split_url = urlsplit(test_db_url)
    base_db_url = urlunsplit(
        (split_url.scheme, split_url.netloc, "template1", split_url.query, split_url.fragment)
    )
    engine = create_engine(base_db_url)
    yield engine


@pytest.fixture(scope='session')
def test_db_name(test_db_url):
    split_url = urlsplit(test_db_url)
    yield split_url.path.strip('/')


@pytest.fixture(scope='session')
def test_db_url(config_path):
    with open(config_path, encoding='utf-8') as f:
        content = yaml.safe_load(f.read())
    yield content.get('pyramid_oereb').get('app_schema').get('db_connection')


@pytest.fixture(scope='session')
def test_db_engine(base_engine, test_db_name, test_db_url, config_path):
    """
    create a new test DB called test_db_name and its engine
    """

    base_connection = base_engine.connect()
    # terminate existing connections to be able to DROP the DB
    base_connection.execute('SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE '
                            f'pg_stat_activity.datname = \'{test_db_name}\' AND pid <> pg_backend_pid();')
    # sqlalchemy uses transactions by default, COMMIT end the current transaction and allows
    # creation and destruction of DB
    base_connection.execute('COMMIT')
    base_connection.execute(f"DROP DATABASE if EXISTS {test_db_name}")
    base_connection.execute('COMMIT')
    base_connection.execute(f"CREATE DATABASE {test_db_name}")

    engine = create_engine(test_db_url)
    engine.execute("CREATE EXTENSION POSTGIS")

    # initialize the DB with standard tables via a temp string buffer to hold SQL commands
    sql_file = StringIO()
    create_tables_from_standard_configuration(config_path, sql_file=sql_file)
    sql_file.seek(0)
    engine.execute(sql_file.read())

    yield engine

    # currently there is a problem with teardown of the DB and sessions:
    # DROP DATABASE may be called while a connection is still alive, this may lead to error messages
    # therefore, the DB will temporarily be dropped at the beginning of the test instead of a final
    # cleanup (see above)
    # # do cleanup: disconnect users and DROP DB
    # base_connection.execute('SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE '
    #                         f'pg_stat_activity.datname = \'{test_db_name}\' AND pid <> pg_backend_pid();')
    # base_connection.execute('COMMIT')
    # base_connection.execute(f"DROP DATABASE if EXISTS {test_db_name}")


@pytest.fixture(scope='session')
@pytest.mark.usefixtures('config_path')
def pyramid_oereb_test_config(config_path, dbsession):
    del dbsession
    # Reload the standard test configuration and now initialize it
    Config._config = None  # needed to force reload due to internal assertion
    Config.init(config_path, configsection='pyramid_oereb', init_data=True)
    return Config


@pytest.fixture
def dbsession(test_db_engine):
    session = orm.sessionmaker(bind=test_db_engine)()
    with patch(
        'pyramid_oereb.core.adapter.DatabaseAdapter.get_session', return_value=session
    ), patch.object(
        session, "close"
    ):
        yield session


@pytest.fixture
def transact(dbsession):
    transact = dbsession.begin_nested()
    yield transact
    transact.rollback()
    dbsession.expire_all()


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
