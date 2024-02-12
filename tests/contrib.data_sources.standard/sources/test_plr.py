import datetime
import math

import pytest
from unittest.mock import patch

from geoalchemy2 import WKTElement
from shapely.geometry import Polygon, Point, LineString, GeometryCollection
from shapely.wkt import loads
from sqlalchemy import String, text, create_engine, orm
from sqlalchemy.orm import declarative_base

from pyramid_oereb.core.config import Config
from pyramid_oereb.core.records.documents import DocumentRecord
from pyramid_oereb.core.records.geometry import GeometryRecord
from pyramid_oereb.core.records.law_status import LawStatusRecord
from pyramid_oereb.core.records.plr import PlrRecord
from pyramid_oereb.core.views.webservice import Parameter
from pyramid_oereb.contrib.data_sources.standard.models import get_view_service, get_legend_entry, \
    get_public_law_restriction, get_geometry, get_public_law_restriction_document
from pyramid_oereb.contrib.data_sources.standard.sources.plr import DatabaseSource
from pyramid_oereb.core import b64
from pyramid_oereb.core.records.document_types import DocumentTypeRecord
from pyramid_oereb.core.records.image import ImageRecord
from pyramid_oereb.core.records.office import OfficeRecord
from pyramid_oereb.core.records.theme import ThemeRecord
from pyramid_oereb.core.records.view_service import LegendEntryRecord, ViewServiceRecord


@pytest.fixture
def date_today():
    yield datetime.date.today()


@pytest.fixture
def yesterday(date_today):
    yield date_today - datetime.timedelta(days=1)


@pytest.fixture
def tomorrow(date_today):
    yield date_today + datetime.timedelta(days=1)


@pytest.fixture
def real_estate_wkt():
    yield 'MULTIPOLYGON (' \
          '((40 40, 20 45, 45 30, 40 40)),' \
          '((20 35, 10 30, 10 10, 30 5, 45 20, 20 35),' \
          '(30 20, 20 15, 20 25, 30 20))'\
          ')'


@pytest.fixture
def real_estate_shapely_geom(real_estate_wkt):
    yield loads(real_estate_wkt)


@pytest.fixture
def plr_source_params(db_connection):
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
                "model_factory": "pyramid_oereb.contrib.data_sources.standard."
                                 "models.theme.model_factory_string_pk",
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
def config_themes(app_config):
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


@pytest.fixture(autouse=True)
def config_config(app_config):
    mock_config = {
        'default_language': 'de',
        'srid': 2056,
        'geometry_types': {
            'point': {
                'types': {
                    'Point',
                    'MultiPoint'
                }
            },
            'line': {
                'types': {
                    'LineString',
                    'LinearRing',
                    'MultiLineString'
                }
            },
            'polygon': {
                'types': {
                    'Polygon',
                    'MultiPolygon'
                }
            },
            'collection': {
                'types': {
                    'GeometryCollection'
                }
            }
        }
    }
    with patch('pyramid_oereb.core.config.Config._config', mock_config):
        yield


@pytest.fixture
def all_plr_result_session(session, query):
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
def base():
    yield declarative_base()


@pytest.fixture
def view_service_model_class(base):
    yield get_view_service(
        base,
        'test',
        String
    )


@pytest.fixture
def legend_entry_model_class(view_service_model_class, base):
    yield get_legend_entry(
        base,
        'test',
        String,
        view_service_model_class
    )


@pytest.fixture
def public_law_restriction_document_model_class(base, plr_model_class, document_model_class):
    yield get_public_law_restriction_document(
        base,
        'test',
        String,
        plr_model_class,
        document_model_class
    )


@pytest.fixture
def legend_entries_from_db(legend_entry_model_class, png_binary):
    yield [legend_entry_model_class(**{
        'id': '1',
        'legend_text': {'de': 'testlegende without sub theme'},
        'type_code': 'testCode',
        'type_code_list': 'testCode,testCode2,testCode3',
        'theme': 'ch.Nutzungsplanung',
        'sub_theme': None,
        'view_service_id': '1',
        'symbol': b64.encode(png_binary)
    }), legend_entry_model_class(**{
        'id': '2',
        'legend_text': {'de': 'testlegende with sub theme'},
        'type_code': 'testCode',
        'type_code_list': 'testCode,testCode2,testCode3',
        'theme': 'ch.Nutzungsplanung',
        'sub_theme': "ch.Subcode",
        'view_service_id': '1',
        'symbol': b64.encode(png_binary)
    })]


@pytest.fixture
def view_service_from_db(view_service_model_class):
    yield view_service_model_class(**{
        'id': '1',
        'reference_wms': {'de': 'https://geowms.bl.ch/?'
                                'SERVICE=WMS&'
                                'version=1.1.1&'
                                'REQUEST=GetMap&'
                                'layers=grundkarte_farbig_group&'
                                'bbox=2614821,1259276,2618821,1263276&'
                                'width=600&'
                                'height=600&'
                                'srs=EPSG:2056&'
                                'format=image/png'},
        'layer_index': 1,
        'layer_opacity': 1.0
    })


@pytest.fixture
def legend_entry_records(png_binary):
    yield [
        LegendEntryRecord(
            ImageRecord(png_binary),
            {'de': 'plr_legend_entry text'},
            'testCode3',
            'testCode,testCode2,testCode3',
            Config.themes[0],
            1,
            Config.themes[1]
        ),
        LegendEntryRecord(
            ImageRecord(png_binary),
            {'de': 'plr_legend_entry text'},
            'testCode3',
            'testCode,testCode2,testCode3',
            Config.themes[0],
            1
        )
    ]


@pytest.fixture
def document_type_record():
    yield DocumentTypeRecord(
            "Rechtsvorschrift",
            {
                "de": "Rechtsvorschrift",
                "fr": "Disposition juridique",
                "it": "Prescrizione legale",
                "rm": "Prescripziun giuridica",
                "en": "Legal provision"
            }
        )


@pytest.fixture
def document_records(document_type_record, law_status_records, yesterday, office_records):
    yield [
        DocumentRecord(
            document_type=document_type_record,
            index=2,
            law_status=law_status_records[0],
            title={'de': 'Test Rechtsvorschrift'},
            published_from=yesterday,
            responsible_office=office_records[0],
            text_at_web={'de': 'http://meine.rechtsvorschrift.ch'},
            official_number={'de': 'rv.test.1'},
            abbreviation={'de': 'Test'},
            article_numbers=['Art.1', 'Art.2', 'Art.3']
        )
    ]


@pytest.fixture
def office_records():
    yield [
        OfficeRecord(
            {'de': 'Office1'},
            'abcde',
            {'de': 'https://office1.url'},
            'entrance 1',
            'building 1',
            'Office1 street',
            '1a',
            4444,
            'Office1 City'
        )
    ]


@pytest.fixture
def view_service_record():
    yield ViewServiceRecord(
        {'de': 'http://my.wms.com'},
        1,
        1.0,
        'de',
        2056,
        None,
        None
    )


@pytest.fixture
def geometry_records(law_status_records):
    yield [
        GeometryRecord(
            law_status_records[0],
            datetime.date.today(),
            None,
            Point(0.5, 0.5)
        ),
        GeometryRecord(
            law_status_records[0],
            datetime.date.today(),
            None,
            LineString([(0, 0), (0, 1)])
        ),
        GeometryRecord(
            law_status_records[0],
            datetime.date.today(),
            None,
            Polygon([(0, 0), (1, 1), (1, 0)])
        )
    ]


@pytest.fixture
def patch_config_get_law_status_by_data_code(law_status_records):
    def get_law_status_by_data_code(code, law_status):
        return law_status_records[0]

    with patch('pyramid_oereb.core.config.Config.get_law_status_by_data_code', get_law_status_by_data_code):
        yield


@pytest.fixture
def patch_get_document_type_by_data_code(document_type_record):
    def get_document_type_by_data_code(code, document_type):
        return document_type_record

    with patch(
            'pyramid_oereb.core.config.Config.get_document_type_by_data_code',
            get_document_type_by_data_code):
        yield


@pytest.fixture
def patch_unwrap_multi_geometry():
    def mock_unwrap_multi_geometry(obj, law_status, published_from, published_until, geometry, geo_metadata):
        return [obj, law_status, published_from, published_until, geometry, geo_metadata]

    with patch(
            'pyramid_oereb.contrib.data_sources.standard.sources.plr.DatabaseSource.unwrap_multi_geometry_',
            mock_unwrap_multi_geometry):
        yield


@pytest.fixture
def patch_unwrap_geometry_collection():
    def unwrap_geometry_collection(obj, law_status, published_from, published_until, geometry, geo_metadata):
        return [obj, law_status, published_from, published_until, geometry, geo_metadata]

    with patch(
            'pyramid_oereb.contrib.data_sources.standard.sources.plr.'
            'DatabaseSource.unwrap_geometry_collection_',
            unwrap_geometry_collection):
        yield


@pytest.fixture
def patch_create_geometry_records():
    def create_geometry_records(obj, law_status, published_from, published_until, geometry, geo_metadata):
        return [obj, law_status, published_from, published_until, geometry, geo_metadata]

    with patch(
            'pyramid_oereb.contrib.data_sources.standard.sources.plr.DatabaseSource.create_geometry_records_',
            create_geometry_records):
        yield


@pytest.fixture
def patch_from_db_to_office_record(office_records):
    def from_db_to_office_record(obj, office_from_db):
        return office_records[0]
    with patch(
            'pyramid_oereb.contrib.data_sources.standard.sources.plr.DatabaseSource.from_db_to_office_record',
            from_db_to_office_record):
        yield


@pytest.fixture
def patch_from_db_to_legend_entry_record(legend_entry_records):
    def from_db_to_legend_entry_record(obj, legend_entry_from_db):
        return legend_entry_records[0]
    with patch(
            'pyramid_oereb.contrib.data_sources.standard.sources.plr.DatabaseSource'
            '.from_db_to_legend_entry_record',
            from_db_to_legend_entry_record):
        yield


@pytest.fixture
def patch_from_db_to_legend_entry_records(legend_entry_records):
    def from_db_to_legend_entry_records(obj, legend_entries_from_db, legend_entry_record):
        return legend_entry_records
    with patch(
            'pyramid_oereb.contrib.data_sources.standard.sources.plr.DatabaseSource.'
            'from_db_to_legend_entry_records',
            from_db_to_legend_entry_records):
        yield


@pytest.fixture
def patch_from_db_to_view_service_record(view_service_record):
    def from_db_to_view_service_record(obj, public_law_restriction_from_db, legend_entry_records):
        return view_service_record
    with patch(
            'pyramid_oereb.contrib.data_sources.standard.sources.plr.DatabaseSource.'
            'from_db_to_view_service_record',
            from_db_to_view_service_record):
        yield


@pytest.fixture
def patch_from_db_to_geometry_records(geometry_records):
    def from_db_to_geometry_records(obj, public_law_restriction_from_db):
        return geometry_records
    with patch(
            'pyramid_oereb.contrib.data_sources.standard.sources.plr.DatabaseSource.'
            'from_db_to_geometry_records',
            from_db_to_geometry_records):
        yield


@pytest.fixture
def patch_from_db_to_document_records(document_records):
    def from_db_to_document_records(obj, documents_from_db):
        return document_records
    with patch(
            'pyramid_oereb.contrib.data_sources.standard.sources.plr.DatabaseSource.'
            'from_db_to_document_records',
            from_db_to_document_records):
        yield


@pytest.fixture
def patch_config_get_document_types_lookups(plr_source_params):
    def get_document_types_lookups(theme_code):
        return plr_source_params['document_types_lookup']
    with patch(
            'pyramid_oereb.core.config.Config.get_document_types_lookups',
            get_document_types_lookups):
        yield


@pytest.fixture
def patch_config_get_document_type_by_data_code(document_type_record):
    def get_document_type_by_data_code(theme_code, data_code):
        return document_type_record
    with patch(
            'pyramid_oereb.core.config.Config.get_document_type_by_data_code',
            get_document_type_by_data_code):
        yield


@pytest.fixture
def office_model_class(base):
    from pyramid_oereb.contrib.data_sources.standard.models.main import get_office
    Office = get_office(base, 'test', String)
    yield Office


@pytest.fixture
def office_from_db(office_model_class):
    yield [
        office_model_class(**{
            'id': "1",
            'name': {'de': 'Office1'},
            'office_at_web': {'de': 'https://office1.url'},
            'uid': 'abcde',
            'line1': 'entrance 1',
            'line2': 'building 1',
            'street': 'Office1 street',
            'number': '1a',
            'postal_code': 4444,
            'city': 'Office1 City'
        }),
        office_model_class(**{
            'id': "2",
            'name': {'de': 'Office2'},
            'office_at_web': {'de': 'https://office2.url'},
            'uid': 'fghij',
            'line1': 'entrance 2',
            'line2': 'building 2',
            'street': 'Office2 street',
            'number': '2a',
            'postal_code': 5555,
            'city': 'Office2 City'
        })
    ]


@pytest.fixture
def document_db_values(png_binary, yesterday, tomorrow):
    yield [{
        'id': "1",
        'document_type': 'Hinweis',
        'index': 1,
        'law_status': 'inKraft',
        'title': {'de': 'Titel1'},
        'office_id': 1,
        'published_from': yesterday,
        'published_until': tomorrow,
        'text_at_web': {'de': 'https://test1.abcd'},
        'abbreviation': {'de': 'abkrz'},
        'official_number': {'de': 'ch.abc.d123'},
        'only_in_municipality': 1234,
        'file': png_binary
    }, {
        'id': "2",
        'document_type': 'Gesetz',
        'index': 2,
        'law_status': 'inKraft',
        'title': {'de': 'Titel2'},
        'office_id': 1,
        'published_from': yesterday,
        'published_until': tomorrow,
        'text_at_web': {'de': 'https://test2.abcd'},
        'abbreviation': {'de': 'abkrz'},
        'official_number': {'de': 'ch.abc.d321'},
        'only_in_municipality': 4567,
        'file': png_binary
    }]


@pytest.fixture
def document_model_class(base, office_model_class):
    from pyramid_oereb.contrib.data_sources.standard.models.main import get_document
    document_model = get_document(base, 'test', String, office_model_class)
    yield document_model


@pytest.fixture
def documents_from_db(document_model_class, document_db_values):
    yield [
        document_model_class(**document_db_values[0]),
        document_model_class(**document_db_values[1])
    ]


@pytest.fixture
def plr_model_class(base, view_service_model_class, legend_entry_model_class, office_model_class):
    plr_model = get_public_law_restriction(
        base,
        'test',
        String,
        office_model_class,
        view_service_model_class,
        legend_entry_model_class
    )
    yield plr_model


@pytest.fixture
def public_law_restriction_document_db(public_law_restriction_document_model_class, documents_from_db):
    yield [
        public_law_restriction_document_model_class(**{
            'document': documents_from_db[0],
            'document_id': documents_from_db[0].id,
            'public_law_restriction_id': '1'
        }),
        public_law_restriction_document_model_class(**{
            'document': documents_from_db[1],
            'document_id': documents_from_db[1].id,
            'public_law_restriction_id': '1'
        })
    ]


@pytest.fixture
def plrs_from_db(plr_model_class, yesterday, tomorrow, view_service_from_db,
                 office_from_db, legend_entries_from_db, public_law_restriction_document_db,
                 public_law_restriction_document_model_class, geometries_from_db):
    geometries_from_db[0].public_law_restriction_id = '1'
    plr_from_db_1 = plr_model_class(**{
        'id': "1",
        'law_status': 'inKraft',
        'published_from': yesterday,
        'published_until': tomorrow,
        'view_service_id': view_service_from_db.id,
        'view_service': view_service_from_db,
        'office_id': office_from_db[0].id,
        'legend_entry_id': legend_entries_from_db[0].id,
        'legend_entry': legend_entries_from_db[0],
        'geometries': [geometries_from_db[0]],
    })
    plr_from_db_1.legal_provisions = public_law_restriction_document_db
    yield [
        plr_from_db_1
    ]


@pytest.fixture
def wkb_geom():
    yield [WKTElement(
        "SRID=2056;POLYGON(("
        "2609229.759 1263666.789,"
        "2609231.206 1263670.558,"
        "2609229.561 1263672.672,"
        "2609229.472 1263675.47,"
        "2609251.865 1263727.506,"
        "2609275.847 1263783.29,"
        "2609229.759 1263666.789"
        "))",
        extended=True
    ), WKTElement(
        "SRID=2056;POLYGON(("
        "2608901.529 1261990.655,"
        "2608898.665 1261991.598,"
        "2608895.798 1261992.53,"
        "2608892.928 1261993.452,"
        "2608890.054 1261994.363,"
        "2608880.256 1261996.496"
        "2608901.529 1261990.655"
        "))",
        extended=True
    )]


@pytest.fixture
def geometry_model_class(plr_model_class, base):
    geometry_model = get_geometry(base, 'test', String, "POLYGON", 2056, plr_model_class)
    yield geometry_model


@pytest.fixture
def geometries_from_db(geometry_model_class, wkb_geom):
    published_from = datetime.date.today() - datetime.timedelta(days=1)
    published_until = datetime.date.today() + datetime.timedelta(days=1)
    geo_metadata = 'https://geocat.ch'
    yield [
        geometry_model_class(**{
            "id": "1",
            "law_status": 'inKraft',
            "published_from": published_from,
            "published_until": published_until,
            "geo_metadata": geo_metadata,
            "geom": wkb_geom[0]
        })
    ]


def test_from_db_to_legend_entry_record_with_subtheme(plr_source_params, all_plr_result_session,
                                                      legend_entries_from_db, png_binary):
    with patch(
            'pyramid_oereb.core.adapter.DatabaseAdapter.get_session',
            return_value=all_plr_result_session()):
        source = DatabaseSource(**plr_source_params)
        legend_entry_record = source.from_db_to_legend_entry_record(legend_entries_from_db[1])
        assert isinstance(legend_entry_record, LegendEntryRecord)
        assert legend_entry_record.theme.code == 'ch.Nutzungsplanung'
        assert legend_entry_record.symbol.content == ImageRecord(b64.decode(b64.encode(png_binary))).content
        assert legend_entry_record.legend_text == {'de': 'testlegende with sub theme'}
        assert legend_entry_record.type_code == 'testCode'
        assert legend_entry_record.type_code_list == 'testCode,testCode2,testCode3'
        assert isinstance(legend_entry_record.theme, ThemeRecord)
        assert legend_entry_record.view_service_id == '1'
        assert isinstance(legend_entry_record.sub_theme, ThemeRecord)


def test_from_db_to_legend_entry_record_without_subtheme(plr_source_params, all_plr_result_session,
                                                         legend_entries_from_db, png_binary):
    with patch(
            'pyramid_oereb.core.adapter.DatabaseAdapter.get_session',
            return_value=all_plr_result_session()):
        source = DatabaseSource(**plr_source_params)
        legend_entry_record = source.from_db_to_legend_entry_record(legend_entries_from_db[0])
        assert isinstance(legend_entry_record, LegendEntryRecord)
        assert legend_entry_record.theme.code == 'ch.Nutzungsplanung'
        assert legend_entry_record.symbol.content == ImageRecord(b64.decode(b64.encode(png_binary))).content
        assert legend_entry_record.legend_text == {'de': 'testlegende without sub theme'}
        assert legend_entry_record.type_code == 'testCode'
        assert legend_entry_record.type_code_list == 'testCode,testCode2,testCode3'
        assert isinstance(legend_entry_record.theme, ThemeRecord)
        assert legend_entry_record.view_service_id == '1'
        assert legend_entry_record.sub_theme is None


def test_from_db_to_legend_entry_records_with_subtheme(plr_source_params, all_plr_result_session,
                                                       legend_entries_from_db, legend_entry_records):
    with patch(
            'pyramid_oereb.core.adapter.DatabaseAdapter.get_session',
            return_value=all_plr_result_session()):
        source = DatabaseSource(**plr_source_params)
        legend_entry_records = source.from_db_to_legend_entry_records(
            legend_entries_from_db,
            legend_entry_records[0]
        )
        assert len(legend_entry_records) == 1
        assert legend_entry_records[0].legend_text == {'de': 'testlegende with sub theme'}


def test_from_db_to_legend_entry_records_without_subtheme(plr_source_params, all_plr_result_session,
                                                          legend_entries_from_db, legend_entry_records):
    with patch(
            'pyramid_oereb.core.adapter.DatabaseAdapter.get_session',
            return_value=all_plr_result_session()):
        source = DatabaseSource(**plr_source_params)
        legend_entry_records = source.from_db_to_legend_entry_records(
            legend_entries_from_db,
            legend_entry_records[1]
        )
        assert len(legend_entry_records) == 1
        assert legend_entry_records[0].legend_text == {'de': 'testlegende without sub theme'}


def test_from_db_to_view_service_record(plr_source_params, all_plr_result_session,
                                        legend_entry_records, view_service_from_db):
    with patch(
            'pyramid_oereb.core.adapter.DatabaseAdapter.get_session',
            return_value=all_plr_result_session()):
        source = DatabaseSource(**plr_source_params)
        view_service_record = source.from_db_to_view_service_record(
            view_service_from_db,
            legend_entry_records
        )
        assert isinstance(view_service_record, ViewServiceRecord)


@pytest.mark.parametrize('tolerances', [None, 0.1, {'ALL': 0.1},
                                        {'Point': 0.2, 'LineString': 0.5, 'Polygon': 0.1}])
@pytest.mark.parametrize('with_collection', [False, True])
def test_handle_collection_tolerance(tolerances, with_collection, config_config, plr_source_params,
                                     all_plr_result_session):
    with patch(
        'pyramid_oereb.core.adapter.DatabaseAdapter.get_session',
        return_value=all_plr_result_session()
    ):
        if tolerances:
            if isinstance(tolerances, float):
                plr_source_params["tolerance"] = tolerances
                plr_source_params.pop("tolerances", None)
            else:
                plr_source_params["tolerances"] = tolerances
        else:
            plr_source_params.pop("tolerance", None)
            plr_source_params.pop("tolerances", None)
        geom = Polygon(((0, 0), (0, 1), (1, 1)))
        if with_collection:
            geom = GeometryCollection([geom])
            plr_source_params["geometry_type"] = "GEOMETRYCOLLECTION"
        else:
            plr_source_params["geometry_type"] = "POLYGON"

        source = DatabaseSource(**plr_source_params)
        query = source.handle_collection(all_plr_result_session(), geom)

        # check results for 8 combinations of with_collection + tolerances
        from sqlalchemy.sql.annotation import AnnotatedColumn
        from sqlalchemy.sql.elements import BooleanClauseList, TextClause, BindParameter
        from geoalchemy2.functions import ST_Intersects, ST_DWithin, ST_GeomFromWKB
        if with_collection:
            assert type(query.received_clause) is BooleanClauseList
            for clause in query.received_clause.clauses:
                assert type(clause) is TextClause
                if tolerances:
                    assert 'ST_DWithin' in clause.text
                else:
                    assert 'ST_Intersects' in clause.text
        else:
            if tolerances:
                assert type(query.received_clause) is ST_DWithin
                assert {
                    type(el) for el in query.received_clause.clause_expr.element.clauses
                } == {AnnotatedColumn, ST_GeomFromWKB, BindParameter}
                assert math.isclose(query.received_clause.clauses.clauses[2].value, 0.1, rel_tol=1e-9)
            else:
                assert type(query.received_clause) is ST_Intersects
                assert {
                    type(el) for el in query.received_clause.clause_expr.element.clauses
                } == {AnnotatedColumn, ST_GeomFromWKB}


@pytest.mark.parametrize('geom,length,geom_type', [
    (loads('POINT (40 10)'), 1, Point),
    (loads('LINESTRING (10 10, 20 20, 10 40)'), 1, LineString),
    (loads('POLYGON ((40 40, 20 45, 45 30, 40 40))'), 1, Polygon)
])
def test_create_geometry_records_simple(plr_source_params, all_plr_result_session, legend_entry_records,
                                        view_service_from_db, geom, length, geom_type,
                                        law_status_records):
    law_status = law_status_records[0]
    published_from = datetime.date.today() - datetime.timedelta(days=1)
    published_until = datetime.date.today() + datetime.timedelta(days=1)
    geo_metadata = 'https://geocat.ch'
    with patch(
            'pyramid_oereb.core.adapter.DatabaseAdapter.get_session',
            return_value=all_plr_result_session()):
        source = DatabaseSource(**plr_source_params)
        unwrapped_geometries = source.create_geometry_records_(
            law_status,
            published_from,
            published_until,
            geom,
            geo_metadata
        )
        assert len(unwrapped_geometries) == length
        for item in unwrapped_geometries:
            assert item.law_status == law_status
            assert item.published_from == published_from
            assert item.published_until == published_until
            assert item.geo_metadata == geo_metadata
            assert isinstance(item.geom, geom_type)


@pytest.mark.parametrize('geom', [
    (loads(
        'MULTIPOLYGON ('
        '((40 40, 20 45, 45 30, 40 40)),'
        '((20 35, 10 30, 10 10, 30 5, 45 20, 20 35),'
        '(30 20, 20 15, 20 25, 30 20))'
        ')'
    )),
    (loads(
        'MULTIPOINT ('
        '(10 40),'
        '(40 30),'
        '(20 20),'
        '(30 10)'
        ')'
    )),
    (loads(
        'MULTILINESTRING ('
        '(10 10, 20 20, 10 40),'
        '(40 40, 30 30, 40 20, 30 10)'
        ')'
    ))
])
def test_create_geometry_records_multi(plr_source_params, all_plr_result_session, legend_entry_records,
                                       view_service_from_db, geom, law_status_records,
                                       patch_unwrap_multi_geometry):
    from pyramid_oereb.contrib.data_sources.standard.sources.plr import DatabaseSource
    law_status = law_status_records[0]
    published_from = datetime.date.today() - datetime.timedelta(days=1)
    published_until = datetime.date.today() + datetime.timedelta(days=1)
    geo_metadata = 'https://geocat.ch'
    with patch(
            'pyramid_oereb.core.adapter.DatabaseAdapter.get_session',
            return_value=all_plr_result_session()):
        source = DatabaseSource(**plr_source_params)
        unwrapped_geometries = source.create_geometry_records_(
            law_status,
            published_from,
            published_until,
            geom,
            geo_metadata
        )
        assert unwrapped_geometries[0] == source
        assert unwrapped_geometries[1] == law_status
        assert unwrapped_geometries[2] == published_from
        assert unwrapped_geometries[3] == published_until
        assert unwrapped_geometries[4] == geom
        assert unwrapped_geometries[5] == geo_metadata


@pytest.mark.parametrize('geom', [
    (loads('GEOMETRYCOLLECTION (POINT (40 10))')),
    (loads('GEOMETRYCOLLECTION (LINESTRING (10 10, 20 20, 10 40))')),
    (loads('GEOMETRYCOLLECTION (MULTILINESTRING ((10 10, 20 20, 10 40),(40 40, 30 30, 40 20, 30 10)))')),
    (loads('GEOMETRYCOLLECTION (POLYGON ((40 40, 20 45, 45 30, 40 40)))'))
])
def test_create_geometry_records_collection(plr_source_params, all_plr_result_session, legend_entry_records,
                                            view_service_from_db, geom, law_status_records,
                                            patch_unwrap_geometry_collection):
    from pyramid_oereb.contrib.data_sources.standard.sources.plr import DatabaseSource
    law_status = law_status_records[0]
    published_from = datetime.date.today() - datetime.timedelta(days=1)
    published_until = datetime.date.today() + datetime.timedelta(days=1)
    geo_metadata = 'https://geocat.ch'
    with patch('pyramid_oereb.core.adapter.DatabaseAdapter.get_session', return_value=all_plr_result_session()):  # noqa: E501
        source = DatabaseSource(**plr_source_params)
        unwrapped_geometries = source.create_geometry_records_(
            law_status,
            published_from,
            published_until,
            geom,
            geo_metadata
        )
        assert unwrapped_geometries[0] == source
        assert unwrapped_geometries[1] == law_status
        assert unwrapped_geometries[2] == published_from
        assert unwrapped_geometries[3] == published_until
        assert unwrapped_geometries[4] == geom
        assert unwrapped_geometries[5] == geo_metadata


@pytest.mark.parametrize('multi_geom,length,geom_type', [
    (loads(
        'MULTIPOLYGON ('
        '((40 40, 20 45, 45 30, 40 40)),'
        '((20 35, 10 30, 10 10, 30 5, 45 20, 20 35),'
        '(30 20, 20 15, 20 25, 30 20))'
        ')'
    ), 2, Polygon),
    (loads(
        'MULTIPOINT ('
        '(10 40),'
        '(40 30),'
        '(20 20),'
        '(30 10)'
        ')'
       ), 4, Point),
    (loads(
        'MULTILINESTRING ('
        '(10 10, 20 20, 10 40),'
        '(40 40, 30 30, 40 20, 30 10)'
        ')'
    ), 2, LineString)
])
def test_unwrap_multi_geometry(plr_source_params, all_plr_result_session, legend_entry_records,
                               view_service_from_db, multi_geom, length, geom_type,
                               law_status_records):  # noqa: E501
    law_status = law_status_records[0]
    published_from = datetime.date.today() - datetime.timedelta(days=1)
    published_until = datetime.date.today() + datetime.timedelta(days=1)
    geo_metadata = 'https://geocat.ch'
    with patch(
            'pyramid_oereb.core.adapter.DatabaseAdapter.get_session',
            return_value=all_plr_result_session()):
        source = DatabaseSource(**plr_source_params)
        unwrapped_geometries = source.unwrap_multi_geometry_(
            law_status,
            published_from,
            published_until,
            multi_geom,
            geo_metadata
        )
        assert len(unwrapped_geometries) == length
        for item in unwrapped_geometries:
            assert item.law_status == law_status
            assert item.published_from == published_from
            assert item.published_until == published_until
            assert item.geo_metadata == geo_metadata
            assert isinstance(item.geom, geom_type)


@pytest.mark.parametrize('geom,length', [
    (loads('GEOMETRYCOLLECTION (POINT (40 10))'), 1),
    (loads('GEOMETRYCOLLECTION (LINESTRING (10 10, 20 20, 10 40))'), 1),
    (loads('GEOMETRYCOLLECTION (MULTILINESTRING ((10 10, 20 20, 10 40),(40 40, 30 30, 40 20, 30 10)))'), 2),
    (loads('GEOMETRYCOLLECTION (POLYGON ((40 40, 20 45, 45 30, 40 40)))'), 1)
])
def test_unwrap_geometry_collection(plr_source_params, all_plr_result_session, legend_entry_records,
                                    view_service_from_db, geom, law_status_records,
                                    patch_create_geometry_records, length):
    from pyramid_oereb.contrib.data_sources.standard.sources.plr import DatabaseSource
    law_status = law_status_records[0]
    published_from = datetime.date.today() - datetime.timedelta(days=1)
    published_until = datetime.date.today() + datetime.timedelta(days=1)
    geo_metadata = 'https://geocat.ch'
    with patch(
            'pyramid_oereb.core.adapter.DatabaseAdapter.get_session',
            return_value=all_plr_result_session()):
        source = DatabaseSource(**plr_source_params)
        unwrapped_geometries = source.unwrap_geometry_collection_(
            law_status,
            published_from,
            published_until,
            geom,
            geo_metadata
        )
        for index, geom_part in enumerate(geom.geoms):
            assert unwrapped_geometries[0 + index] == source
            assert unwrapped_geometries[1 + index] == law_status
            assert unwrapped_geometries[2 + index] == published_from
            assert unwrapped_geometries[3 + index] == published_until
            assert unwrapped_geometries[4 + index] == geom_part
            assert unwrapped_geometries[5 + index] == geo_metadata


def test_unwrap_collection_geometry_fail(plr_source_params, all_plr_result_session, legend_entry_records,
                                         view_service_from_db, law_status_records):
    with patch(
            'pyramid_oereb.core.adapter.DatabaseAdapter.get_session',
            return_value=all_plr_result_session()):
        source = DatabaseSource(**plr_source_params)
        with pytest.raises(AttributeError):
            source.unwrap_geometry_collection_(
                law_status_records[0],
                datetime.date.today() - datetime.timedelta(days=1),
                datetime.date.today() + datetime.timedelta(days=1),
                loads(
                    'GEOMETRYCOLLECTION ('
                    'POINT (40 10),'
                    'LINESTRING (10 10, 20 20, 10 40),'
                    'POLYGON ((40 40, 20 45, 45 30, 40 40))'
                    ')'
                ),
                'https://geocat.ch'
            )


def test_from_db_to_geometry_records(plr_source_params, all_plr_result_session,
                                     patch_config_get_law_status_by_data_code, patch_create_geometry_records,
                                     geometries_from_db, law_status_records, yesterday, tomorrow):
    from pyramid_oereb.contrib.data_sources.standard.sources.plr import DatabaseSource
    with patch(
            'pyramid_oereb.core.adapter.DatabaseAdapter.get_session',
            return_value=all_plr_result_session()):
        source = DatabaseSource(**plr_source_params)
        geometry_records = source.from_db_to_geometry_records(geometries_from_db)
        assert geometry_records[0] == source
        assert geometry_records[1] == law_status_records[0]
        assert geometry_records[2] == yesterday
        assert geometry_records[3] == tomorrow
        assert isinstance(geometry_records[4], Polygon)
        assert geometry_records[5] == 'https://geocat.ch'


def test_from_db_to_office_record(plr_source_params, all_plr_result_session, office_from_db):
    with patch(
            'pyramid_oereb.core.adapter.DatabaseAdapter.get_session',
            return_value=all_plr_result_session()):
        source = DatabaseSource(**plr_source_params)
        office_record = source.from_db_to_office_record(office_from_db[0])
        assert office_record.name == {'de': 'Office1'}
        assert office_record.office_at_web == {'de': 'https://office1.url'}
        assert office_record.uid == 'abcde'
        assert office_record.line1 == 'entrance 1'
        assert office_record.line2 == 'building 1'
        assert office_record.street == 'Office1 street'
        assert office_record.number == '1a'
        assert office_record.postal_code == 4444
        assert office_record.city == 'Office1 City'


def test_from_db_to_document_records(plr_source_params, all_plr_result_session, documents_from_db,
                                     patch_from_db_to_office_record, patch_config_get_law_status_by_data_code,
                                     patch_get_document_type_by_data_code, document_type_record,
                                     law_status_records, document_db_values, office_records):
    from pyramid_oereb.contrib.data_sources.standard.sources.plr import DatabaseSource
    with patch(
            'pyramid_oereb.core.adapter.DatabaseAdapter.get_session',
            return_value=all_plr_result_session()):
        source = DatabaseSource(**plr_source_params)
        document_records = source.from_db_to_document_records(documents_from_db)
        assert len(document_records) == 2
        for index, record in enumerate(document_records):
            assert record.document_type == document_type_record
            assert record.law_status == law_status_records[0]
            assert record.responsible_office == office_records[0]
            assert record.index == document_db_values[index]['index']
            assert record.title == document_db_values[index]['title']
            assert record.published_from == document_db_values[index]['published_from']
            assert record.published_until == document_db_values[index]['published_until']
            assert record.text_at_web == document_db_values[index]['text_at_web']
            assert record.abbreviation == document_db_values[index]['abbreviation']
            assert record.official_number == document_db_values[index]['official_number']
            assert record.only_in_municipality == document_db_values[index]['only_in_municipality']
            assert len(record.article_numbers) == 0
            assert record.file == document_db_values[index]['file']


def test_from_db_to_plr_record(plr_source_params, all_plr_result_session,
                               patch_from_db_to_legend_entry_record,
                               patch_from_db_to_legend_entry_records, patch_from_db_to_office_record,
                               patch_from_db_to_view_service_record, patch_from_db_to_geometry_records,
                               patch_config_get_law_status_by_data_code,
                               patch_config_get_document_types_lookups,
                               patch_config_get_document_type_by_data_code,
                               patch_from_db_to_document_records,
                               legend_entries_from_db, plrs_from_db,
                               yesterday,
                               tomorrow,
                               legend_entry_records,
                               law_status_records,
                               office_records,
                               view_service_record,
                               geometry_records,
                               documents_from_db,
                               view_service_from_db):
    with patch(
            'pyramid_oereb.core.adapter.DatabaseAdapter.get_session',
            return_value=all_plr_result_session()):
        source = DatabaseSource(**plr_source_params)
        plr_record = source.from_db_to_plr_record(
            Parameter('json'),
            plrs_from_db[0],
            legend_entries_from_db
        )
        assert isinstance(plr_record, PlrRecord)
        assert isinstance(plr_record.theme, ThemeRecord)
        assert plr_record.theme == legend_entry_records[0].theme
        assert isinstance(plr_record.legend_entry, LegendEntryRecord)
        assert plr_record.legend_entry == legend_entry_records[0]
        assert isinstance(plr_record.law_status, LawStatusRecord)
        assert plr_record.law_status == law_status_records[0]
        assert plr_record.published_from == yesterday
        assert plr_record.published_until == tomorrow
        assert isinstance(plr_record.responsible_office, OfficeRecord)
        assert plr_record.responsible_office == office_records[0]
        assert isinstance(plr_record.symbol, ImageRecord)
        assert isinstance(plr_record.view_service, ViewServiceRecord)
        assert plr_record.view_service == view_service_record
        assert isinstance(plr_record.geometries[0], GeometryRecord)
        assert plr_record.geometries[0] == geometry_records[0]
        assert isinstance(plr_record.sub_theme, ThemeRecord)
        assert plr_record.sub_theme == Config.themes[1]
        assert plr_record.type_code == legend_entries_from_db[0].type_code
        assert plr_record.type_code_list == legend_entries_from_db[0].type_code_list
        assert isinstance(plr_record.documents[0], DocumentRecord)
        assert plr_record.min_area == plr_source_params['thresholds']['area']['limit']
        assert plr_record.min_length == plr_source_params['thresholds']['length']['limit']
        assert plr_record.area_unit == plr_source_params['thresholds']['area']['unit']
        assert plr_record.length_unit == plr_source_params['thresholds']['length']['unit']
        assert plr_record.view_service_id == view_service_from_db.id


def test_get_document_records(plr_source_params, all_plr_result_session, plrs_from_db,
                              patch_from_db_to_document_records,
                              document_records):
    with patch(
            'pyramid_oereb.core.adapter.DatabaseAdapter.get_session',
            return_value=all_plr_result_session()):
        source = DatabaseSource(**plr_source_params)
        plr_document_records = source.get_document_records(
            Parameter('json'),
            plrs_from_db[0]
        )
        assert len(plr_document_records) == 1
        assert isinstance(plr_document_records[0], DocumentRecord)
        assert plr_document_records[0] == document_records[0]


def test_extract_geometry_collection_db(real_estate_shapely_geom):
    real_estate_shapely_geom
    clause = DatabaseSource.extract_geometry_collection_db(
        'test.geometry.geom',
        real_estate_shapely_geom
    )
    assert len(clause.clauses) == 3
    assert clause.clauses[0].text == text(
        'ST_Intersects(ST_CollectionExtract(test.geometry.geom, 1), ST_GeomFromText(\'{}\', 2056))'.format(
            real_estate_shapely_geom.wkt
        )
    ).text
    assert clause.clauses[1].text == text(
        'ST_Intersects(ST_CollectionExtract(test.geometry.geom, 2), ST_GeomFromText(\'{}\', 2056))'.format(
            real_estate_shapely_geom.wkt
        )
    ).text
    assert clause.clauses[2].text == text(
        'ST_Intersects(ST_CollectionExtract(test.geometry.geom, 3), ST_GeomFromText(\'{}\', 2056))'.format(
            real_estate_shapely_geom.wkt
        )
    ).text


def test_handle_collection(plr_source_params, all_plr_result_session, real_estate_shapely_geom,
                           db_connection):
    with patch(
            'pyramid_oereb.core.adapter.DatabaseAdapter.get_session',
            return_value=all_plr_result_session()):
        engine = create_engine(db_connection, pool_recycle=30)
        session = orm.scoped_session(orm.sessionmaker(bind=engine))
        source = DatabaseSource(**plr_source_params)
        source._plr_info['geometry_type'] = 'Point'

        query = source.handle_collection(session, real_estate_shapely_geom)
        assert str(query).replace('\n', '').replace(' ', '') == '''
            SELECT
                land_use_plans.geometry.id AS land_use_plans_geometry_id,
                land_use_plans.geometry.law_status AS land_use_plans_geometry_law_status,
                land_use_plans.geometry.published_from AS land_use_plans_geometry_published_from,
                land_use_plans.geometry.published_until AS land_use_plans_geometry_published_until,
                land_use_plans.geometry.geo_metadata AS land_use_plans_geometry_geo_metadata,
                ST_AsEWKB(land_use_plans.geometry.geom) AS land_use_plans_geometry_geom,
                land_use_plans.geometry.public_law_restriction_id AS
                 land_use_plans_geometry_public_law_restriction_id
            FROM land_use_plans.geometry
            WHERE ST_Intersects(
                land_use_plans.geometry.geom,
                ST_GeomFromWKB(%(ST_GeomFromWKB_1)s, %(ST_GeomFromWKB_2)s)
            )
        '''.replace('\n', '').replace(' ', '')
