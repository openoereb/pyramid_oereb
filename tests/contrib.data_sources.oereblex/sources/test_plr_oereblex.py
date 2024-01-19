import datetime

import pytest
from unittest.mock import patch

from geoalchemy2 import WKTElement
from shapely.geometry import Polygon, Point, LineString
from shapely.wkt import loads
from sqlalchemy import String
from sqlalchemy.orm import declarative_base

from pyramid_oereb.core.config import Config
from pyramid_oereb.core.records.documents import DocumentRecord
from pyramid_oereb.core.records.geometry import GeometryRecord
from pyramid_oereb.contrib.data_sources.oereblex.models.theme import model_factory

from pyramid_oereb.core import b64
from pyramid_oereb.core.records.document_types import DocumentTypeRecord
from pyramid_oereb.core.records.image import ImageRecord
from pyramid_oereb.core.records.office import OfficeRecord
from pyramid_oereb.core.records.theme import ThemeRecord
from pyramid_oereb.core.records.view_service import LegendEntryRecord, ViewServiceRecord
from pyramid_oereb.core.views.webservice import Parameter


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
        "code": "ch.StatischeWaldgrenzen",
        "geometry_type": "LINESTRING",
        "thresholds": {
            "length": {
                "limit": 1.0
            },
            "area":
                {"limit": 1.0}
        },
        "language": "de",
        "federal": False,
        "view_service": {
            "layer_index": 1,
            "layer_opacity": 1.0
        },
        "source": {
            "class": "pyramid_oereb.contrib.sources.plr_oereblex.DatabaseOEREBlexSource",
            "params": {
                "db_connection": db_connection,
                "model_factory": "pyramid_oereb.contrib.data_sources.standard."
                                 "models.theme.model_factory_string_pk",
                "schema_name": "forest_perimeters"
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
            "ch.StatischeWaldgrenzen",
            {"de": "Statische Waldgrenzen"},
            20
        )
    ]
    with patch(
            'pyramid_oereb.core.config.Config.themes', themes
    ), patch(
        'pyramid_oereb.core.config.Config._config', app_config
    ):
        yield


@pytest.fixture(autouse=True)
def config_config(plr_source_params):
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
        },
        "plrs": [plr_source_params]
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
def models(db_connection):
    yield model_factory(
        'test',
        String,
        'LINESTRING',
        2056,
        db_connection
    )


@pytest.fixture
def view_service_model_class(models):
    yield models.ViewService


@pytest.fixture
def legend_entry_model_class(models):
    yield models.LegendEntry


@pytest.fixture
def legend_entries_from_db(legend_entry_model_class, png_binary):
    yield [legend_entry_model_class(**{
        'id': '1',
        'legend_text': {'de': 'testlegende without sub theme'},
        'type_code': 'testCode',
        'type_code_list': 'testCode,testCode2,testCode3',
        'theme': 'ch.StatischeWaldgrenzen',
        'sub_theme': None,
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
def plr_model_class(models):
    yield models.PublicLawRestriction


@pytest.fixture
def plrs_from_db(plr_model_class, yesterday, tomorrow, view_service_from_db,
                 office_from_db, legend_entries_from_db, geometries_from_db):
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
    yield [
        plr_from_db_1
    ]


@pytest.fixture
def wkb_geom():
    yield [WKTElement(
        "SRID=2056;LINESTRING(("
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
        "SRID=2056;LINESTRING(("
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
def geometry_model_class(models):
    yield models.Geometry


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


@pytest.fixture
def params():
    yield Parameter('xml', language='de')


def test_init(plr_source_params):
    from pyramid_oereb.contrib.data_sources.oereblex.sources.plr_oereblex import DatabaseOEREBlexSource
    from pyramid_oereb.contrib.data_sources.oereblex.sources.document import OEREBlexSource
    source = DatabaseOEREBlexSource(**plr_source_params)
    assert source._queried_geolinks == {}
    assert isinstance(source._oereblex_source, OEREBlexSource)


@pytest.mark.parametrize('url_param_config,plr_code,output', [
    (
        [{"code": "ch.StatischeWaldgrenzen", "url_param": "oereb_id=5"}],
        "ch.StatischeWaldgrenzen", "oereb_id=5"
    ),
    (
        [{"code": "ch.StatischeWaldgrenzen"}],
        "ch.StatischeWaldgrenzen", None
    ),
    (
        [{"code": "ch.StatischeWaldgrenzen", "url_param": "oereb_id=5"}],
        "BogusPlrCode", None
    )
])
def test_get_config_value_for_plr_code(plr_source_params, url_param_config, plr_code, output):
    from pyramid_oereb.contrib.data_sources.oereblex.sources.plr_oereblex import DatabaseOEREBlexSource
    assert output == DatabaseOEREBlexSource.get_config_value_for_plr_code(url_param_config, plr_code)


@pytest.mark.parametrize('url_param_config,plr_code,output', [
    ([{"url_param": "oereb_id=5"}], "ch.StatischeWaldgrenzen", "oereb_id=5")
])
def test_get_config_value_for_plr_code_raises(plr_source_params, url_param_config, plr_code, output):
    from pyramid_oereb.contrib.data_sources.oereblex.sources.plr_oereblex import DatabaseOEREBlexSource
    with pytest.raises(LookupError):
        DatabaseOEREBlexSource.get_config_value_for_plr_code(url_param_config, plr_code)


def test_get_document_records(plr_source_params, document_records, params, plrs_from_db, law_status_records):
    with patch(
        'pyramid_oereb.contrib.data_sources.oereblex.sources.plr_oereblex.DatabaseOEREBlexSource'
        '.document_records_from_oereblex',
        return_value=document_records), \
        patch('pyramid_oereb.core.config.Config.law_status', law_status_records), \
        patch(
            'pyramid_oereb.core.config.Config.get_law_status_lookups',
            return_value=plr_source_params['law_status_lookup']
    ):
        from pyramid_oereb.contrib.data_sources.oereblex.sources.plr_oereblex import DatabaseOEREBlexSource
        source = DatabaseOEREBlexSource(**plr_source_params)
        assert source.get_document_records(params, plrs_from_db[0]) == document_records


def test_document_records_from_oereblex(plr_source_params, document_records, params, law_status_records):
    with patch(
            'pyramid_oereb.contrib.data_sources.oereblex.sources.document.OEREBlexSource.read',
            return_value=None
    ), patch(
        "pyramid_oereb.contrib.data_sources.oereblex.sources.document.OEREBlexSource.records",
        document_records
    ):
        from pyramid_oereb.contrib.data_sources.oereblex.sources.plr_oereblex import DatabaseOEREBlexSource

        source = DatabaseOEREBlexSource(**plr_source_params)
        assert source.document_records_from_oereblex(
            params,
            1,
            law_status_records[0],
            "oereb_id=5"
        ) == document_records
