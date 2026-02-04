import pytest
from unittest.mock import patch, MagicMock

from datetime import date, timedelta
from sys import float_info as fi

from pyramid.path import DottedNameResolver

from sqlalchemy import create_engine, orm, text
from sqlalchemy.schema import CreateSchema
from sqlalchemy.engine.url import URL

from shapely.geometry import Polygon

from pyramid_oereb.core.records.real_estate import RealEstateRecord
from pyramid_oereb.core.records.municipality import MunicipalityRecord
from pyramid_oereb.core.records.theme import ThemeRecord
from pyramid_oereb.core.records.plr import PlrRecord

from pyramid_oereb.core.processor import Processor
from pyramid_oereb.contrib.data_sources.interlis_2_3.sources.plr import (
    StandardThemeConfigParser
)
from pyramid_oereb.contrib.data_sources.interlis_2_3.sources.plr import DatabaseSource
from pyramid_oereb.core.records.plr import EmptyPlrRecord
from pyramid_oereb.core.views.webservice import Parameter


@pytest.fixture(scope='session')
def interlis_db_engine(base_engine):
    # def test_db_engine(base_engine, test_db_name, config_path):
    # """
    # create a new test DB called test_db_name and its engine
    # """

    test_interlis_db_name = "interlis_test"
    with base_engine.begin() as base_connection:
        # terminate existing connections to be able to DROP the DB
        term_stmt = 'SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity ' \
            f'WHERE pg_stat_activity.datname = \'{test_interlis_db_name}\' AND pid <> pg_backend_pid();'
        base_connection.execute(text(term_stmt))
        # sqlalchemy uses transactions by default, COMMIT ends the current transaction and allows
        # creation and destruction of DB
        base_connection.execute(text('COMMIT'))
        base_connection.execute(text(f"DROP DATABASE if EXISTS {test_interlis_db_name}"))
        base_connection.execute(text('COMMIT'))
        base_connection.execute(text(f"CREATE DATABASE {test_interlis_db_name}"))

    test_db_url = URL.create(
        base_engine.url.get_backend_name(),
        base_engine.url.username,
        base_engine.url.password,
        base_engine.url.host,
        base_engine.url.port,
        database=test_interlis_db_name
    )
    engine = create_engine(test_db_url)
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION POSTGIS"))
    return engine


@pytest.fixture(scope='session')
def interlis_dbsession(interlis_db_engine):
    session = orm.sessionmaker(bind=interlis_db_engine)()
    with patch(
        'pyramid_oereb.core.adapter.DatabaseAdapter.get_session', return_value=session
    ), patch.object(
        session, "close"
    ):
        yield session


@pytest.fixture(scope='session')
def interlis_transact(interlis_dbsession):
    transact = interlis_dbsession.begin_nested()
    yield transact
    transact.rollback()
    interlis_dbsession.expire_all()


@pytest.fixture(scope='session')
def interlis_land_use_plans(pyramid_oereb_test_config,
                            interlis_db_engine, interlis_dbsession, interlis_transact):
    del interlis_transact

    theme_config = pyramid_oereb_test_config.get_theme_config_by_code('ch.Nutzungsplanung')
    theme_config["source"]["class"] = (
        "pyramid_oereb.contrib.data_sources.interlis_2_3.sources.plr.DatabaseSource"
    )
    theme_config["source"]["params"]["model_factory"] = (
        "pyramid_oereb.contrib.data_sources.interlis_2_3.models.theme.model_factory_string_pk"
    )
    theme_config["hooks"]["get_symbol"] = (
        "pyramid_oereb.contrib.data_sources.interlis_2_3.hook_methods.get_symbol"
    )
    config_parser = StandardThemeConfigParser(**theme_config)
    models = config_parser.get_models()

    with interlis_db_engine.begin() as connection:
        connection.execute(CreateSchema('land_use_plans'))
    models.Geometry.metadata.create_all(interlis_db_engine)

    localised_uris = {
        models.LocalisedUri(**{
            't_id': 1,
            'language': 'de',
            'text': 'http://my.wms.com',
            'multilingualuri_id': 1
        })
    }
    interlis_dbsession.add_all(localised_uris)
    uris = {
        models.MultilingualUri(**{
            't_id': 1,
            'view_service_id': 1,
        })
    }
    interlis_dbsession.add_all(uris)
    view_services = {
        models.ViewService(**{
            't_id': 1
        })
    }
    interlis_dbsession.add_all(view_services)
    legend_entries = {
        models.LegendEntry(**{
            't_id': 1,
            'symbol': b"",
            'legend_text_de': 'interlis',
            'type_code': 'type',
            'type_code_list': 'type',
            'theme': 'ch.Nutzungsplanung',
            'view_service_id': 1
        })
    }
    interlis_dbsession.add_all(legend_entries)
    offices = {
        models.Office(**{
            't_id': 1,
            'name_de': 'Amt'
        })
    }
    interlis_dbsession.add_all(offices)
    plrs = {
        models.PublicLawRestriction(**{
            't_id': 1,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'view_service_id': 1,
            'legend_entry_id': 1,
            'office_id': 1
        }),
        models.PublicLawRestriction(**{
            't_id': 2,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'view_service_id': 1,
            'legend_entry_id': 1,
            'office_id': 1
        })
    }
    interlis_dbsession.add_all(plrs)
    geometries = {
        models.Geometry(**{
            't_id': 1,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'geo_metadata': 'Large polygon PLR',
            'public_law_restriction_id': 1,
            'surface': 'SRID=2056;POLYGON((1 -1, 9 -1, 9 7, 1 7, 1 8, 10 8, 10 -2, 1 -2, 1 -1))',
        }),
        models.Geometry(**{
            't_id': 2,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'geo_metadata': 'Line',
            'public_law_restriction_id': 1,
            'line': 'SRID=2056;LINESTRING(1 0.1, 2 0.1)',
        }),
        models.Geometry(**{
            't_id': 3,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'geo_metadata': 'Line',
            'public_law_restriction_id': 2,
            'line': 'SRID=2056;LINESTRING(1 0.1, 2 0.2)',
        }),
        models.Geometry(**{
            't_id': 4,
            'law_status': 'inKraft',
            'published_from': date.today().isoformat(),
            'published_until': (date.today() + timedelta(days=100)).isoformat(),
            'geo_metadata': 'Small polygon PLR',
            'public_law_restriction_id': 1,
            'point': 'SRID=2056;POINT(1 2)',
        })
    }
    interlis_dbsession.add_all(geometries)
    interlis_dbsession.flush()


@pytest.fixture
def oblique_limit_real_estate_record():
    return RealEstateRecord(
        'test_type', 'BL', 'Nusshof', 1234, land_registry_area=3.2,
        limit=Polygon(((0, 0), (3, 0), (3, 0.3)))
    )


@pytest.fixture
def plr_source_params(db_connection):
    yield {
        "source": {
            "class": "pyramid_oereb.contrib.data_sources.interlis_2_3.sources.plr.DatabaseSource",
            "params": {
                "db_connection": db_connection,
                "model_factory": "pyramid_oereb.contrib.data_sources.interlis_2_3."
                                 "models.theme.model_factory_integer_pk",
                "schema_name": "land_use_plans"
            }
        }
    }


@pytest.fixture
def processor_data(pyramid_oereb_test_config, main_schema):
    with patch(
            'pyramid_oereb.core.config.Config.municipalities',
            [MunicipalityRecord(1234, 'test', True)]
        ), patch(
            'pyramid_oereb.core.config.Config.themes',
            [ThemeRecord('ch.Nutzungsplanung', dict(), 100, document_records=[])]
    ):
        yield pyramid_oereb_test_config


@pytest.mark.parametrize('with_tolerance, nb_results', [(False, 1), (True, 2)])
def test_related_geometries(processor_data, pyramid_oereb_test_config, interlis_land_use_plans,
                            oblique_limit_real_estate_record, with_tolerance, nb_results):
    plr_cadastre_authority = pyramid_oereb_test_config.get_plr_cadastre_authority()
    plr = pyramid_oereb_test_config.get_theme_config_by_code('ch.Nutzungsplanung')
    if with_tolerance:
        plr["tolerances"] = {'Point': 0.2, 'LineString': 0.5, 'Polygon': fi.epsilon}
    plr_source_class = DottedNameResolver().maybe_resolve(plr.get('source').get('class'))
    plr_sources = [plr_source_class(**plr)]

    from pyramid_oereb.core.views.webservice import Parameter
    request_params = Parameter('json', egrid='TEST')
    municipality = MunicipalityRecord(1234, 'test', True)

    from pyramid_oereb.core.readers.extract import ExtractReader

    extract_reader = ExtractReader(
        plr_sources,
        plr_cadastre_authority
    )
    extract_raw = extract_reader.read(
        request_params, oblique_limit_real_estate_record, municipality
    )
    processor = Processor(
        real_estate_reader=None,
        plr_sources=plr_sources,
        extract_reader=extract_reader,
    )
    assert len(extract_raw.real_estate.public_law_restrictions) == nb_results
    extract = processor.plr_tolerance_check(extract_raw)
    plrs = [plr for plr in extract.real_estate.public_law_restrictions if isinstance(plr, PlrRecord)]
    assert len(plrs) == nb_results


def mock_session_object_query_geometries(items_list):
    class PublicLawRestrictionTest():
        def __init__(self, law_status, legend_entry_id):
            self.law_status = law_status
            self.legend_entry_id = legend_entry_id

    class GeometryTest():
        def __init__(self, public_law_restriction):
            self.public_law_restriction = public_law_restriction

    geometries = []
    for item in items_list:
        geometries.append(GeometryTest(PublicLawRestrictionTest(item[0], item[1])))

    class AllTest():
        def all():
            return iter(geometries)

    class DistinctTest():
        def __init__(self):
            pass

        def options(arg2):
            return AllTest

    class FilterTest():
        def __init__(self):
            pass

        def distinct(arg2):
            return DistinctTest

    class QueryTest():
        def __init__(self):
            pass

        def filter(arg3):
            return FilterTest

    class SessionTest():
        def __init__(self):
            pass

        def query(arg1):
            return QueryTest

    return SessionTest


def get_return_vals_of_get_legend_entries_from_db(arg1, arg2, list_of_ids):
    return_value = []
    for id in list_of_ids:
        return_value.append((id, ))
    return return_value


@pytest.mark.parametrize('idx,items_list', [
    (0, [
        ["inForce", 1],
        ["changeWithoutPreEffect", 1],
        ["changeWithoutPreEffect", 2],
        ["inForce", 3],
        ["inForce", 4],
        ["inForce", 3],
        ["changeWithoutPreEffect", 6],
        ["inForce", 7],
        ["changeWithoutPreEffect", 2],
        ["inForce", 9],
        ["changeWithoutPreEffect", 7]
    ]),
    (1, [
        ["inForce", 1],
        ["inForce", 3],
        ["inForce", 4],
        ["inForce", 3],
        ["inForce", 7],
        ["inForce", 9],
    ])
])
def test_collect_legend_entries_by_bbox(idx, items_list, plr_source_params):
    with (
        patch.object(
            DatabaseSource,
            'get_legend_entries_from_db',
            get_return_vals_of_get_legend_entries_from_db
        )
    ):
        source = DatabaseSource(**plr_source_params)
        result = source.collect_legend_entries_by_bbox(
            mock_session_object_query_geometries(items_list),
            Polygon(((0., 0.), (0., 1.), (1., 1.), (1., 0.), (0., 0.))))

    if idx == 0:
        assert len(result) == 2
        assert sorted([x[0] for x in result if x[1] == 'inForce'][0]) == \
            [(1, ), (3, ), (4, ), (7, ), (9, )]
        assert sorted([x[0] for x in result if x[1] == 'changeWithoutPreEffect'][0]) == \
            [(1, ), (2, ), (6, ), (7, )]
    if idx == 1:
        assert len(result) == 1
        assert sorted([x[0] for x in result if x[1] == 'inForce'][0]) == \
            [(1, ), (3, ), (4, ), (7, ), (9, )]


@pytest.fixture
def mock_config():
    with patch('pyramid_oereb.core.config.Config') as mock:
        mock.get.return_value = 2056
        mock.availabilities = []
        mock.extract_module_function.side_effect = lambda x: {
            'module_path': '.'.join(x.split('.')[:-1]),
            'function_name': x.split('.')[-1]
        }
        yield mock


@pytest.fixture
def mock_adapter():
    with patch('pyramid_oereb.database_adapter') as mock:
        yield mock


def test_read_not_available(mock_config, mock_adapter):
    with patch('pyramid_oereb.contrib.data_sources.interlis_2_3.sources.plr.Config') as mock_plr_config:
        mock_plr_config.availability_by_theme_code_municipality_fosnr.return_value = False
        mock_plr_config.extract_module_function.side_effect = lambda x: {
            'module_path': '.'.join(x.split('.')[:-1]),
            'function_name': x.split('.')[-1]
        }
        source = DatabaseSource(**{
            'code': 'test_code',
            'geometry_type': 'Polygon',
            'source': {
                'params': {
                    'db_connection': 'postgresql://user:pass@host:5432/db',
                    'model_factory':
                        'pyramid_oereb.contrib.data_sources'
                        '.interlis_2_3.models.theme.model_factory_integer_pk',
                    'schema_name': 'schema'
                }
            }
        })
        real_estate = MagicMock(spec=RealEstateRecord)
        real_estate.fosnr = 1234

        records = source.read(None, real_estate, None)

    assert len(records) == 1
    assert isinstance(records[0], EmptyPlrRecord)
    assert records[0].has_data is False


def test_read_empty_db(mock_config, mock_adapter):
    with patch('pyramid_oereb.contrib.data_sources.interlis_2_3.sources.plr.Config') as mock_plr_config:
        mock_plr_config.availability_by_theme_code_municipality_fosnr.return_value = True
        mock_plr_config.get_theme_by_code_sub_code.return_value = MagicMock()
        mock_plr_config.extract_module_function.side_effect = lambda x: {
            'module_path': '.'.join(x.split('.')[:-1]),
            'function_name': x.split('.')[-1]
        }

        mock_session = MagicMock()
        source = DatabaseSource(**{
            'code': 'test_code',
            'geometry_type': 'Polygon',
            'source': {
                'params': {
                    'db_connection': 'postgresql://user:pass@host:5432/db',
                    'model_factory':
                        'pyramid_oereb.contrib.data_sources'
                        '.interlis_2_3.models.theme.model_factory_integer_pk',
                    'schema_name': 'schema'
                }
            }
        })
        source._adapter_ = MagicMock()
        source._adapter_.get_session.return_value = mock_session
        mock_session.query.return_value.count.return_value = 0

        real_estate = MagicMock(spec=RealEstateRecord)
        real_estate.fosnr = 1234

        records = source.read(None, real_estate, None)

    assert len(records) == 1
    assert isinstance(records[0], EmptyPlrRecord)
    mock_session.close.assert_called_once()


def test_read_no_related_geometries(mock_config, mock_adapter):
    with patch('pyramid_oereb.contrib.data_sources.interlis_2_3.sources.plr.Config') as mock_plr_config:
        mock_plr_config.availability_by_theme_code_municipality_fosnr.return_value = True
        mock_plr_config.get_theme_by_code_sub_code.return_value = MagicMock()
        mock_plr_config.extract_module_function.side_effect = lambda x: {
            'module_path': '.'.join(x.split('.')[:-1]),
            'function_name': x.split('.')[-1]
        }

        mock_session = MagicMock()
        source = DatabaseSource(**{
            'code': 'test_code',
            'geometry_type': 'Polygon',
            'source': {
                'params': {
                    'db_connection': 'postgresql://user:pass@host:5432/db',
                    'model_factory':
                        'pyramid_oereb.contrib.data_sources'
                        '.interlis_2_3.models.theme.model_factory_integer_pk',
                    'schema_name': 'schema'
                }
            }
        })
        source._adapter_ = MagicMock()
        source._adapter_.get_session.return_value = mock_session
        mock_session.query.return_value.count.return_value = 10  # Not empty

        with patch.object(DatabaseSource, 'collect_related_geometries_by_real_estate', return_value=[]):
            real_estate = MagicMock(spec=RealEstateRecord)
            real_estate.fosnr = 1234
            records = source.read(None, real_estate, None)

    assert len(records) == 1
    assert isinstance(records[0], EmptyPlrRecord)
    mock_session.close.assert_called_once()


def test_read_with_geometries(mock_config, mock_adapter):
    with patch('pyramid_oereb.contrib.data_sources.interlis_2_3.sources.plr.Config') as mock_plr_config:
        mock_plr_config.availability_by_theme_code_municipality_fosnr.return_value = True
        mock_plr_config.get_theme_by_code_sub_code.return_value = MagicMock()
        mock_plr_config.extract_module_function.side_effect = lambda x: {
            'module_path': '.'.join(x.split('.')[:-1]),
            'function_name': x.split('.')[-1]
        }

        mock_session = MagicMock()
        source = DatabaseSource(**{
            'code': 'test_code',
            'geometry_type': 'Polygon',
            'source': {
                'params': {
                    'db_connection': 'postgresql://user:pass@host:5432/db',
                    'model_factory':
                        'pyramid_oereb.contrib.data_sources'
                        '.interlis_2_3.models.theme.model_factory_integer_pk',
                    'schema_name': 'schema'
                }
            }
        })
        source._adapter_ = MagicMock()
        source._adapter_.get_session.return_value = mock_session
        mock_session.query.return_value.count.return_value = 10

        mock_geom_result = MagicMock()
        mock_geom_result.public_law_restriction.law_status = 'inForce'

        mock_legend_entry = MagicMock()
        legend_entries_from_db = [[[mock_legend_entry], 'inForce']]

        with patch.object(
                DatabaseSource, 'collect_related_geometries_by_real_estate', return_value=[mock_geom_result]
        ):
            with patch.object(
                    DatabaseSource, 'collect_legend_entries_by_bbox', return_value=legend_entries_from_db
            ):
                with patch.object(
                        DatabaseSource, 'from_db_to_plr_record', return_value=MagicMock()
                ) as mock_from_db:
                    real_estate = MagicMock(spec=RealEstateRecord)
                    real_estate.fosnr = 1234
                    params = MagicMock(spec=Parameter)
                    records = source.read(params, real_estate, MagicMock(spec=Polygon))

                    assert len(records) == 1
                    mock_from_db.assert_called_once_with(params, mock_geom_result.public_law_restriction,
                                                         [mock_legend_entry])
