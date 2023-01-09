# -*- coding: utf-8 -*-
import pytest
import json
import pyaml_env
from io import StringIO
from unittest.mock import patch
from datetime import date, timedelta

from pyramid.testing import testConfig
from sqlalchemy import create_engine, orm, text
from sqlalchemy.engine.url import URL, make_url
from sqlalchemy.exc import OperationalError

import pyramid_oereb
from pyramid_oereb.core import b64
from pyramid_oereb.core.adapter import FileAdapter
from pyramid_oereb.core.config import Config
from pyramid_oereb.core.records.theme import ThemeRecord
from pyramid_oereb.core.records.document_types import DocumentTypeRecord
from pyramid_oereb.core.records.law_status import LawStatusRecord
from pyramid_oereb.core.records.logo import LogoRecord
from pyramid_oereb.contrib.data_sources.create_tables import create_main_schema_from_configuration_, \
    create_tables_from_standard_configuration
from pyramid_oereb.contrib.data_sources.standard.sources.plr import StandardThemeConfigParser

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
        with patch.object(pyramid_oereb, 'route_prefix', 'oereb'):
            pyramid_config.include('pyramid_oereb.core.routes')
            yield pyramid_config


@pytest.fixture
def file_adapter():
    return FileAdapter()


@pytest.fixture(scope='function')
def schema_json_versions():
    with open(SCHEMA_JSON_VERSIONS_PATH) as f:
        return json.load(f)


@pytest.fixture(scope='function')
def schema_json_extract():
    with open(SCHEMA_JSON_EXTRACT_PATH) as f:
        return json.load(f)


@pytest.fixture(scope='function')
def schema_xml_extract():
    return SCHEMA_XML_EXTRACT_PATH


@pytest.fixture(scope='function')
def schema_xml_versions():
    return SCHEMA_XML_VERSIONS_PATH


@pytest.fixture(scope='session')
def theme_test_data():
    with open('tests/resources/sample_data/themes.json') as f:
        return [ThemeRecord(**theme) for theme in json.load(f)]


@pytest.fixture(scope='session')
def law_status_test_data():
    with open('tests/resources/sample_data/law_status.json') as f:
        return [LawStatusRecord(**status) for status in json.load(f)]


@pytest.fixture(scope='session')
def document_type_test_data():
    with open('tests/resources/sample_data/document_type.json') as f:
        return [DocumentTypeRecord(**doc_type) for doc_type in json.load(f)]


@pytest.fixture(scope='session')
def logo_test_data():
    with open('tests/resources/sample_data/logo.json') as f:
        return [LogoRecord(logo['code'], logo['logo']) for logo in json.load(f)]


@pytest.fixture(scope='session')
def base_engine(test_db_url):
    base_db_url = URL.create(
        test_db_url.get_backend_name(),
        test_db_url.username,
        test_db_url.password,
        test_db_url.host,
        test_db_url.port,
        database="postgres"
    )
    engine = create_engine(base_db_url)
    yield engine


@pytest.fixture(scope='session')
def stats_db_url(test_db_url):
    base_db_url = URL.create(
        test_db_url.get_backend_name(),
        test_db_url.username,
        test_db_url.password,
        test_db_url.host,
        test_db_url.port,
        database="oereb_stats_test"
    )
    yield base_db_url


@pytest.fixture(scope='session')
def test_db_name(test_db_url):
    yield test_db_url.database


@pytest.fixture(scope='session')
@pytest.mark.usefixtures('config_path')
def test_db_url(config_path):
    content = pyaml_env.parse_config(config_path)
    yield make_url(content.get('pyramid_oereb').get('app_schema').get('db_connection'))


@pytest.fixture(scope='session')
def clear_stats_db_engine(stats_db_url):
    try:
        stats_connection = create_engine(stats_db_url).connect()
        stats_connection.execute(text('DELETE FROM oereb_logs.logs'))
        stats_connection.execute(text('COMMIT'))
        stats_connection.close()
    except OperationalError:
        pass  # if DB does not exist yet, it shall not be cleared


@pytest.fixture(scope='session')
def drop_stats_db_engine(base_engine):
    base_connection = base_engine.connect()
    # terminate existing connections to be able to DROP the DB
    term_stmt = 'SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE ' \
        'pg_stat_activity.datname = \'oereb_stats_test\' AND pid <> pg_backend_pid();'
    base_connection.execute(text(term_stmt))
    # sqlalchemy uses transactions by default, COMMIT end the current transaction and allows
    # creation and destruction of DB
    base_connection.execute(text('COMMIT'))
    base_connection.execute(text("DROP DATABASE if EXISTS oereb_stats_test"))
    base_connection.execute(text('COMMIT'))


@pytest.fixture(scope='session')
def test_db_engine(base_engine, test_db_name, config_path):
    """
    create a new test DB called test_db_name and its engine
    """
    with base_engine.begin() as base_connection:
        # terminate existing connections to be able to DROP the DB
        term_stmt = 'SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE ' \
            f'pg_stat_activity.datname = \'{test_db_name}\' AND pid <> pg_backend_pid();'
        base_connection.execute(text(term_stmt))
        base_connection.execute(text('COMMIT'))
        base_connection.execute(text(f"DROP DATABASE if EXISTS {test_db_name}"))
        base_connection.execute(text('COMMIT'))
        base_connection.execute(text(f"CREATE DATABASE {test_db_name}"))

    test_db_url = URL.create(
        base_engine.url.get_backend_name(),
        base_engine.url.username,
        base_engine.url.password,
        base_engine.url.host,
        base_engine.url.port,
        database=test_db_name
    )
    engine = create_engine(test_db_url)
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION POSTGIS"))

        # initialize the DB with standard tables via a temp string buffer to hold SQL commands

        # create the main schema
        sql_file_main = StringIO()
        create_main_schema_from_configuration_(config_path, sql_file=sql_file_main)
        sql_file_main.seek(0)
        connection.execute(text(sql_file_main.read()))

        # create the schemas for the themes
        sql_file = StringIO()
        standart_table_source = 'pyramid_oereb.contrib.data_sources.standard.sources.plr.DatabaseSource'
        create_tables_from_standard_configuration(config_path, standart_table_source, sql_file=sql_file)
        sql_file.seek(0)
        connection.execute(text(sql_file.read()))

    return engine

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


@pytest.fixture(scope='session')
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
def main_schema(pyramid_oereb_test_config, theme_test_data, law_status_test_data,
                document_type_test_data, logo_test_data):

    with patch.object(
      Config, 'themes', theme_test_data
    ), patch.object(
      Config, 'law_status', law_status_test_data
    ), patch.object(
      Config, 'document_types', document_type_test_data
    ), patch.object(
      Config, 'logos', logo_test_data):
        yield pyramid_oereb_test_config


@pytest.fixture
def DummyRenderInfo():
    class DummyRenderInfo(object):
        name = 'test'
    return DummyRenderInfo


@pytest.fixture
def wms_url_contaminated_sites():
    return {
        'de': 'https://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&STYLES=default&'
              'CRS=EPSG:2056&BBOX=2475000,1065000,2850000,1300000&WIDTH=740&HEIGHT=500&FORMAT=image/png'
              '&LAYERS=ch.bav.kataster-belasteter-standorte-oev.oereb',
        'fr': 'https://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&STYLES=default&'
              'CRS=EPSG:2056&BBOX=2475000,1065000,2850000,1300000&WIDTH=740&HEIGHT=500&FORMAT=image/png'
              '&LAYERS=ch.bav.kataster-belasteter-standorte-oev.oereb'
            }


@pytest.fixture
def real_estate_data(pyramid_oereb_test_config, dbsession, transact):
    del transact

    from pyramid_oereb.contrib.data_sources.standard.models import main

    real_estates = [main.RealEstate(**{
        'id': '1',
        'egrid': u'TEST',
        'number': u'1000',
        'identdn': u'BLTEST',
        'type': u'Liegenschaft',
        'canton': u'BL',
        'municipality': u'Liestal',
        'fosnr': 1234,
        'land_registry_area': 4,
        'limit': 'SRID=2056;MULTIPOLYGON(((0 0, 0 2, 2 2, 2 0, 0 0)))'
    }), main.RealEstate(**{
        'id': '2',
        'egrid': u'TEST2',
        'number': u'9999',
        'identdn': u'BLTEST',
        'type': u'Liegenschaft',
        'canton': u'BL',
        'municipality': u'Liestal',
        'fosnr': 1234,
        'land_registry_area': 9,
        'limit': 'SRID=2056;MULTIPOLYGON(((2 0, 2 3, 5 3, 5 0, 2 0)))'
    })]
    dbsession.add_all(real_estates)


@pytest.fixture
def land_use_plans(pyramid_oereb_test_config, dbsession, transact, wms_url_contaminated_sites, file_adapter):
    del transact

    theme_config = pyramid_oereb_test_config.get_theme_config_by_code('ch.Nutzungsplanung')
    config_parser = StandardThemeConfigParser(**theme_config)
    models = config_parser.get_models()

    view_services = {
        models.ViewService(**{
            'id': 1,
            'reference_wms': wms_url_contaminated_sites,
            'layer_index': 1,
            'layer_opacity': 1.0,
        })
    }
    dbsession.add_all(view_services)

    offices = {
        models.Office(**{
            'id': 1,
            'name': {
               'de': 'Test office'
            }
        })
    }
    dbsession.add_all(offices)

    legend_entries = {
        models.LegendEntry(**{
            'id': 1,
            'symbol': b64.encode(file_adapter.read('tests/resources/symbol.png')),
            'legend_text': {
                'de': u'Test'
            },
            'type_code': u'CodeA',
            'type_code_list': u'type_code_list',
            'theme': 'ch.Nutzungsplanung',
            'sub_theme': None,
            'view_service_id': 1,
        })
    }
    dbsession.add_all(legend_entries)

    plrs = [
        models.PublicLawRestriction(**{
            'id': 1,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'view_service_id': 1,
            'legend_entry_id': 1,
            'office_id': 1,
        }),
        models.PublicLawRestriction(**{
            'id': 2,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=00)).isoformat(),
            'view_service_id': 1,
            'legend_entry_id': 1,
            'office_id': 1,
        }),
        models.PublicLawRestriction(**{
            'id': 3,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'view_service_id': 1,
            'legend_entry_id': 1,
            'office_id': 1,
        }),
        models.PublicLawRestriction(**{
            'id': 4,
            'law_status': 'inKraft',
            'published_from': (date.today() + timedelta(days=7)).isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'view_service_id': 1,
            'legend_entry_id': 1,
            'office_id': 1,
        }),
        ]
    dbsession.add_all(plrs)

    geometries = {
        models.Geometry(**{
            'id': 1,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'geo_metadata': 'Large polygon PLR',
            'public_law_restriction_id': 1,
            'geom': 'SRID=2056;GEOMETRYCOLLECTION('
                    'POLYGON((1 -1, 9 -1, 9 7, 1 7, 1 8, 10 8, 10 -2, 1 -2, 1 -1)))',
        }),
        models.Geometry(**{
            'id': 2,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'geo_metadata': 'Small polygon PLR',
            'public_law_restriction_id': 1,
            'geom': 'SRID=2056;GEOMETRYCOLLECTION(POLYGON((0 0, 0 1.5, 1.5 1.5, 1.5 0, 0 0)))',
        }),
        models.Geometry(**{
            'id': 3,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'geo_metadata': 'Double intersection polygon PLR',
            'public_law_restriction_id': 1,
            'geom': 'SRID=2056;GEOMETRYCOLLECTION('
                    'POLYGON((3 2.5, 3 5, 7 5, 7 0, 3 0, 3 1, 6 1, 6 4, 4 2.5, 3 2.5)))'
        }),
        models.Geometry(**{
            'id': 4,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'geo_metadata': 'Future PLR',
            'public_law_restriction_id': 1,
            'geom': 'SRID=2056;GEOMETRYCOLLECTION(POLYGON((1.5 1.5, 1.5 2, 2 2, 2 1.5, 1.5 1.5)))',
        }),
        models.Geometry(**{
            'id': 5,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'geo_metadata': 'Future PLR',
            'public_law_restriction_id': 1,
            'geom': 'SRID=2056;GEOMETRYCOLLECTION(POINT(1 2))',
        }),
    }
    dbsession.add_all(geometries)

    documents = {
        models.Document(**{
            'id': 1,
            'document_type': 'GesetzlicheGrundlage',
            'index': 1,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'title': {'de': 'First level document'},
            'office_id': 1,
            'text_at_web': {'de': 'http://www.admin.ch/ch/d/sr/c814_01.html'},
            'abbreviation': {'de': 'USG', 'fr': 'LPE', 'it': 'LPAmb', 'en': 'EPA'},
            'official_number': {'de': 'SR 814.01'},
        }),
        models.Document(**{
            'id': 2,
            'document_type': 'GesetzlicheGrundlage',
            'index': 1,
            'law_status': 'inKraft',
            'published_from': (date.today() + timedelta(days=7)).isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'title': {'de': 'First level document'},
            'office_id': 1,
            'text_at_web': {'de': 'http://www.admin.ch/ch/d/sr/c814_01.html'},
            'abbreviation': {'de': 'USG', 'fr': 'LPE', 'it': 'LPAmb', 'en': 'EPA'},
            'official_number': {'de': 'SR 814.01'},
        }),
        models.Document(**{
            'id': 3,
            'document_type': 'GesetzlicheGrundlage',
            'index': 1,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'title': {'de': 'First level document'},
            'office_id': 1,
            'text_at_web': {'de': 'http://www.admin.ch/ch/d/sr/c814_01.html'},
            'abbreviation': {'de': 'USG', 'fr': 'LPE', 'it': 'LPAmb', 'en': 'EPA'},
            'official_number': {'de': 'SR 814.01'},
            'only_in_municipality': 1234
        }),
        models.Document(**{
            'id': 4,
            'document_type': 'GesetzlicheGrundlage',
            'index': 1,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'title': {'de': 'First level document'},
            'office_id': 1,
            'text_at_web': {'de': 'http://www.admin.ch/ch/d/sr/c814_01.html'},
            'abbreviation': {'de': 'USG', 'fr': 'LPE', 'it': 'LPAmb', 'en': 'EPA'},
            'official_number': {'de': 'SR 814.01'},
            'only_in_municipality': 1235
        })
    }
    dbsession.add_all(documents)

    plr_documents = {
        models.PublicLawRestrictionDocument(**{
            'id': 1,
            'public_law_restriction_id': 1,
            'document_id': 1,
        }),
        models.PublicLawRestrictionDocument(**{
            'id': 2,
            'public_law_restriction_id': 1,
            'document_id': 2,
        }),
        models.PublicLawRestrictionDocument(**{
            'id': 3,
            'public_law_restriction_id': 1,
            'document_id': 3,
        }),
        models.PublicLawRestrictionDocument(**{
            'id': 4,
            'public_law_restriction_id': 1,
            'document_id': 4,
        })
    }
    dbsession.add_all(plr_documents)
    dbsession.flush()


@pytest.fixture
def contaminated_sites(pyramid_oereb_test_config, dbsession, transact, wms_url_contaminated_sites,
                       file_adapter):
    del transact

    theme_config = pyramid_oereb_test_config.get_theme_config_by_code('ch.BelasteteStandorte')
    config_parser = StandardThemeConfigParser(**theme_config)
    models = config_parser.get_models()

    view_services = {
        models.ViewService(**{
            'id': 1,
            'reference_wms': wms_url_contaminated_sites,
            'layer_index': 1,
            'layer_opacity': .75,
        })
        }
    dbsession.add_all(view_services)

    offices = {
        'office1': models.Office(**{
            'id': 1,
            'name': {
               'de': 'Test office'
            }
        })
        }
    dbsession.add_all(offices.values())

    legend_entries = {
        'legend_entry1': models.LegendEntry(**{
            'id': 1,
            'symbol': b64.encode(file_adapter.read('tests/resources/symbol.png')),
            'legend_text': {'de': 'Test'},
            'type_code': 'StaoTyp1',
            'type_code_list': 'https://models.geo.admin.ch/BAFU/KbS_Codetexte_V1_4.xml',
            'theme': 'ch.BelasteteStandorte',
            'view_service_id': 1,
        })
        }
    dbsession.add_all(legend_entries.values())

    plrs = {
        'plr1': models.PublicLawRestriction(**{
            'id': 1,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'view_service_id': 1,
            'legend_entry_id': 1,
            'office_id': 1,
        }),
        'plr2': models.PublicLawRestriction(**{
            'id': 2,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'view_service_id': 1,
            'legend_entry_id': 1,
            'office_id': 1,
        }),
        'plr3': models.PublicLawRestriction(**{
            'id': 3,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'view_service_id': 1,
            'legend_entry_id': 1,
            'office_id': 1,
        }),
        'plr4': models.PublicLawRestriction(**{
            'id': 4,
            'law_status': 'inKraft',
            'published_from': (date.today() + timedelta(days=7)).isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'view_service_id': 1,
            'legend_entry_id': 1,
            'office_id': 1,
        }),
        }
    dbsession.add_all(plrs.values())

    geometries = {
        models.Geometry(**{
            'id': 1,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'geo_metadata': 'Large polygon PLR',
            'public_law_restriction_id': 1,
            'geom': 'SRID=2056;GEOMETRYCOLLECTION(POLYGON((0 0, 0 1.5, 1.5 1.5, 1.5 0, 0 0)))',
        }),
        models.Geometry(**{
            'id': 2,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'geo_metadata': 'Small polygon PLR',
            'public_law_restriction_id': 2,
            'geom': 'SRID=2056;GEOMETRYCOLLECTION(POLYGON((1.5 1.5, 1.5 2, 2 2, 2 1.5, 1.5 1.5)))',
        }),
        models.Geometry(**{
            'id': 3,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'geo_metadata': 'Double intersection polygon PLR',
            'public_law_restriction_id': 3,
            'geom': 'SRID=2056;GEOMETRYCOLLECTION('
                    'POLYGON((3 2.5, 3 5, 7 5, 7 0, 3 0, 3 1, 6 1, 6 4, 4 2.5, 3 2.5)))'
        }),
        models.Geometry(**{
            'id': 4,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'geo_metadata': 'Future PLR',
            'public_law_restriction_id': 4,
            'geom': 'SRID=2056;GEOMETRYCOLLECTION(POLYGON((0 0, 0 2, 2 2, 2 0, 0 0)))',
        }),
        }
    dbsession.add_all(geometries)
    dbsession.flush()


@pytest.fixture
def general_information(pyramid_oereb_test_config, dbsession, transact):
    del transact

    from pyramid_oereb.contrib.data_sources.standard.models.main import GeneralInformation
    general_information = [
        GeneralInformation(
            id='2be3cd8e-b218-49f8-9e4c-c07e8f9a2326',
            title={"de": "Allgemeine Information",
                   "fr": "Informations générales",
                   "it": "Informazioni generali",
                   "rm": "Infurmaziun generala"},
            content={"de": "Der Inhalt des ÖREB-Katasters wird als bekannt vorausgesetzt.",
                     "fr": "Le contenu du cadastre RD"}
        )
    ]
    dbsession.add_all(general_information)

    dbsession.flush()


@pytest.fixture(autouse=True)
def set_route_prefix():
    with patch('pyramid_oereb.core.hook_methods.route_prefix', 'oereb'):
        yield
