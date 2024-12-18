import pytest
from unittest.mock import patch

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

from pyramid_oereb.core.processor import Processor
from pyramid_oereb.contrib.data_sources.interlis_2_3.sources.plr import (
    StandardThemeConfigParser
)
from pyramid_oereb.contrib.data_sources.interlis_2_3.sources.plr import DatabaseSource


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
        # sqlalchemy uses transactions by default, COMMIT end the current transaction and allows
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


# @pytest.fixture
# def interlis_real_estate():
#     theme = ThemeRecord('code', dict(), 100)
#     geometry_records = [
#         GeometryRecord(law_status, datetime.date.today(), None, LineString(((1, 0.1), (2, 0.2))))
#     ]
#     return PlrRecord(
#         theme,
#         LegendEntryRecord(
#             ImageRecord('1'.encode('utf-8')),
#             {'en': 'Content'},
#             'CodeA',
#             None,
#             theme,
#             view_service_id=1
#         ),
#         law_status,
#         date.today() + timedelta(days=0),
#         date.today() + timedelta(days=2),
#         OfficeRecord({'en': 'Office'}),
#         ImageRecord('1'.encode('utf-8')),
#         ViewServiceRecord({'de': 'http://my.wms.com'}, 1, 1.0, 'de', 2056, None, None),
#         geometry_records,
#         documents=[]
#     )


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
    plr_sources = []
    plr_sources.append(plr_source_class(**plr))

    from pyramid_oereb.core.views.webservice import Parameter
    request_params = Parameter('json', egrid='TEST')
    # municipality = pyramid_oereb_test_config.municipality_by_fosnr(oblique_limit_real_estate_record.fosnr)
    municipality = MunicipalityRecord(1234, 'test', True)

    from pyramid_oereb.core.readers.extract import ExtractReader

    extract_reader = ExtractReader(
        plr_sources,
        plr_cadastre_authority
    )
    extract_raw = extract_reader.read(
        request_params, oblique_limit_real_estate_record, municipality
    )
    # processor = Processor(
    #     real_estate_reader=real_estate_reader,
    #     plr_sources=plr_sources,
    #     extract_reader=extract_reader,
    # )
    processor = Processor(
        real_estate_reader=None,
        plr_sources=plr_sources,
        extract_reader=extract_reader,
    )
    assert len(extract_raw.real_estate.public_law_restrictions) == nb_results
    extract = processor.plr_tolerance_check(extract_raw)
    assert len(extract.real_estate.public_law_restrictions) == nb_results


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
