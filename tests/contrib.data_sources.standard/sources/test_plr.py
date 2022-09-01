import pytest
from unittest.mock import patch

from sqlalchemy import String
from sqlalchemy.orm import declarative_base

from shapely.geometry import Polygon, GeometryCollection

from pyramid_oereb.contrib.data_sources.standard.models import get_view_service, get_legend_entry
from pyramid_oereb.contrib.data_sources.standard.sources.plr import DatabaseSource
from pyramid_oereb.core import b64
from pyramid_oereb.core.records.theme import ThemeRecord
from pyramid_oereb.core.records.view_service import LegendEntryRecord


@pytest.fixture
def source_params(db_connection):
    yield {
        "code": "ch.Nutzungsplanung",
        "geometry_type": "GEOMETRYCOLLECTION",
        "thresholds": {
            "length": {
                "limit": 1.0,
                "unit": 'm',
                "precision": 2
            },
            "area": {
                "limit": 1.0,
                "unit": 'm²',
                "precision": 2
            },
            "percentage": {
                "precision": 1
            }
        },
        "language": "de",
        "federal": False,
        "standard": True,
        "view_service": {
            "layer_index": 1,
            "layer_opacity": 1.0
        },
        "source": {
            "class": "pyramid_oereb.contrib.data_sources.standard.sources.plr.DatabaseSource",
            "params": {
                "db_connection": db_connection,
                "model_factory": "pyramid_oereb.contrib.data_sources.standard.models.theme.model_factory_string_pk",  # noqa: E501
                "schema_name": "land_use_plans"
            }
        },
        "hooks": {
            "get_symbol": "pyramid_oereb.contrib.data_sources.standard.hook_methods.get_symbol",
            "get_symbol_ref": "pyramid_oereb.core.hook_methods.get_symbol_ref"
        },
        "law_status_lookup": [{
            "data_code": "inKraft",
            "transfer_code": "inKraft",
            "extract_code": "inForce"
        }, {
            "data_code": "AenderungMitVorwirkung",
            "transfer_code": "AenderungMitVorwirkung",
            "extract_code": "changeWithPreEffect"
        }, {
            "data_code": "AenderungOhneVorwirkung",
            "transfer_code": "AenderungOhneVorwirkung",
            "extract_code": "changeWithoutPreEffect"
        }],
        "document_types_lookup": [{
            "data_code": "Rechtsvorschrift",
            "transfer_code": "Rechtsvorschrift",
            "extract_code": "LegalProvision"
        }, {
            "data_code": "GesetzlicheGrundlage",
            "transfer_code": "GesetzlicheGrundlage",
            "extract_code": "Law"
        }, {
            "data_code": "Hinweis",
            "transfer_code": "Hinweis",
            "extract_code": "Hint"
        }]
    }


@pytest.fixture(autouse=True)
def config(app_config):
    themes = [
        ThemeRecord(
            "ch.Nutzungsplanung",
            {"de": "Nutzungsplanung (kantonal/kommunal)"},
            20
        ), ThemeRecord(
            "ch.Nutzungsplanung",
            {"de": "Nutzungsplanung (kantonal/kommunal)"},
            20,
            "ch.Subcode"
        )
    ]
    with patch(
            'pyramid_oereb.core.config.Config.themes', themes
    ), patch(
        'pyramid_oereb.core.config.Config._config', app_config
    ):
        yield


@pytest.fixture
def all_result_session(session, query):

    class Query(query):

        def all(self):
            return []

        def filter(self, clause):
            self.received_clause = clause
            return self

    class Session(session):

        def query(self, term):
            return Query()

    yield Session


@pytest.fixture
def legend_entry_model_class():
    Base = declarative_base()
    ViewService = get_view_service(Base, 'test', String)
    yield get_legend_entry(Base, 'test', String, ViewService)


@pytest.mark.parametrize('legend_entry_params', [{
        'id': '1',
        'legend_text': {'de': 'testlegende'},
        'type_code': 'testCode',
        'type_code_list': 'testCode,testCode2,testCode3',
        'theme': 'ch.Nutzungsplanung',
        'sub_theme': None,
        'view_service_id': '1'
    }, {
        'id': '1',
        'legend_text': {'de': 'testlegende'},
        'type_code': 'testCode',
        'type_code_list': 'testCode,testCode2,testCode3',
        'theme': 'ch.Nutzungsplanung',
        'sub_theme': "ch.Subcode",
        'view_service_id': '1'
    }])
def test_from_db_to_legend_entry_record(source_params, all_result_session, legend_entry_model_class, png_binary, legend_entry_params):  # noqa: E501
    legend_entry_params.update({'symbol': b64.encode(png_binary)})
    legend_entry_from_db = legend_entry_model_class(**legend_entry_params)
    with patch('pyramid_oereb.core.adapter.DatabaseAdapter.get_session', return_value=all_result_session()):
        source = DatabaseSource(**source_params)
        legend_entry_record = source.from_db_to_legend_entry_record(legend_entry_from_db)
        assert isinstance(legend_entry_record, LegendEntryRecord)
        assert legend_entry_record.theme.code == 'ch.Nutzungsplanung'


@pytest.mark.parametrize('tolerances', [None, 0.1, {'ALL': 0.1},
                                        {'Point': 0.2, 'LineString': 0.5, 'Polygon': 0.1}])
@pytest.mark.parametrize('with_collection', [False, True])
def test_handle_collection(tolerances, with_collection, config, source_params, all_result_session):
    with patch(
        'pyramid_oereb.core.adapter.DatabaseAdapter.get_session',
        return_value=all_result_session()
    ):
        if tolerances:
            if isinstance(tolerances, float):
                source_params["tolerance"] = tolerances
                source_params.pop("tolerances", None)
            else:
                source_params["tolerances"] = tolerances
        else:
            source_params.pop("tolerance", None)
            source_params.pop("tolerances", None)
        geom = Polygon(((0, 0), (0, 1), (1, 1)))
        if with_collection:
            geom = GeometryCollection([geom])
            source_params["geometry_type"] = "GEOMETRYCOLLECTION"
        else:
            source_params["geometry_type"] = "POLYGON"

        source = DatabaseSource(**source_params)
        query = source.handle_collection(all_result_session(), geom)

        # check results for 8 combinations of with_collection + tolerances
        from sqlalchemy.sql.annotation import AnnotatedColumn
        from sqlalchemy.sql.elements import BinaryExpression, BooleanClauseList, TextClause
        from geoalchemy2.functions import ST_Intersects, ST_Distance, ST_GeomFromWKB
        if with_collection:
            assert type(query.received_clause) is BooleanClauseList
            for clause in query.received_clause.clauses:
                assert type(clause) is TextClause
                if tolerances:
                    assert 'ST_Distance' in clause.text
                else:
                    assert 'ST_Intersects' in clause.text
        else:
            if tolerances:
                assert type(query.received_clause) is BinaryExpression
                test_clause = query.received_clause.left
                assert type(test_clause) is ST_Distance
                query.received_clause.right.value == 0.1
            else:
                test_clause = query.received_clause
                assert type(test_clause) is ST_Intersects
            assert {
                type(el) for el in test_clause.clause_expr.element.clauses
            } == {AnnotatedColumn, ST_GeomFromWKB}
