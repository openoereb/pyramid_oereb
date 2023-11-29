import binascii
from pyramid_oereb.contrib.data_sources.interlis_2_3.models.theme import Models
from pyramid_oereb.contrib.data_sources.interlis_2_3.sources.plr import StandardThemeConfigParser

import pytest
from unittest.mock import patch
from sqlalchemy import Integer
from sqlalchemy.orm import declarative_base
from pyramid.httpexceptions import HTTPNotFound, HTTPServerError
from pyramid_oereb.contrib.data_sources.interlis_2_3.hook_methods import get_symbol
from pyramid_oereb.contrib.data_sources.standard.models import get_view_service, get_legend_entry
from pyramid_oereb.core import b64


@pytest.fixture
def theme_config():
    yield {
        "srid": 2056,
        "code": "ch.BelasteteStandorteZivileFlugplaetze",
        "geometry_type": "GEOMETRYCOLLECTION",
        "view_service": {
            "layer_index": 1,
            "layer_opacity": 0.25,
        },
        "law_status_lookup": [{
            "data_code": "inKraft",
            "transfer_code": "inKraft",
            "extract_code": "inForce"
        }],
        "standard": False,
        "federal": True,
        "source": {
            "class": "pyramid_oereb.contrib.data_sources.interlis_2_3.sources.plr.DatabaseSource",
            "params": {
                "db_connection": "postgresql://postgres:postgres@123.123.123.123:5432/oereb_test_db",
                "model_factory": "pyramid_oereb.contrib.data_sources.interlis_2_3.models.theme.model_factory_string_pk",  # noqa: E501
                "schema_name": "contaminated_civil_aviation_sites"
            }
        },
        "hooks": {
            "get_symbol": "pyramid_oereb.contrib.data_sources.interlis_2_3.hook_methods.get_symbol",
            "get_symbol_ref": "pyramid_oereb.core.hook_methods.get_symbol_ref"
        },
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


@pytest.fixture
def legend_entry():
    Base = declarative_base()
    ViewService = get_view_service(Base, 'test', Integer)
    LegendEntry = get_legend_entry(Base, 'test', Integer, ViewService)
    yield LegendEntry


@pytest.fixture
def one_result_binary_session(legend_entry, png_binary, session, query):

    class Query(query):

        def one(self):
            return legend_entry(**{
                'id': 1,
                'symbol': png_binary,
                'legend_text': {'de': 'testlegende'},
                'type_code': 'testCode',
                'type_code_list': 'testCode,testCode2,testCode3',
                'theme': 'ch.TestThema',
                'sub_theme': 'ch.SubTestThema',
                'view_service_id': 1
            })

    class Session(session):

        def query(self, term):
            return Query()

    yield Session


@pytest.fixture
def no_result_session(legend_entry, png_binary, session, query):

    class Session(session):

        def query(self, term):
            return query()

    yield Session


@pytest.fixture
def one_result_no_symbol_session(legend_entry, session, query):

    class Query(query):

        def one(self):
            return legend_entry(**{
                'id': 1,
                'legend_text': {'de': 'testlegende'},
                'type_code': 'testCode',
                'type_code_list': 'testCode,testCode2,testCode3',
                'theme': 'ch.TestThema',
                'sub_theme': 'ch.SubTestThema',
                'view_service_id': 1
            })

    class Session(session):

        def query(self, term):
            return Query()

    yield Session


@pytest.fixture
def one_result_wrong_content_session(legend_entry, session, query):

    class Query(query):

        def one(self):
            return legend_entry(**{
                'id': 1,
                'symbol': 1,
                'legend_text': {'de': 'testlegende'},
                'type_code': 'testCode',
                'type_code_list': 'testCode,testCode2,testCode3',
                'theme': 'ch.TestThema',
                'sub_theme': 'ch.SubTestThema',
                'view_service_id': 1
            })

    class Session(session):

        def query(self, term):
            return Query()

    yield Session


@pytest.fixture
def one_result_b64_session(legend_entry, png_binary, session, query):

    class Query(query):
        def one(self):
            return legend_entry(**{
                'id': 1,
                'symbol': b64.encode(png_binary),
                'legend_text': {'de': 'testlegende'},
                'type_code': 'testCode',
                'type_code_list': 'testCode,testCode2,testCode3',
                'theme': 'ch.TestThema',
                'sub_theme': 'ch.SubTestThema',
                'view_service_id': 1
            })

    class Session(session):
        def query(self, term):
            return Query()

    yield Session


@pytest.fixture
def mock_get_models():

    class LegendEntry():
        t_id = 1

    office = ''
    document = ''
    view_service = ''
    legend_entry = LegendEntry()
    public_law_restriction = []
    geometry = ''
    public_law_restriction_document = ''
    localised_blob = ''
    localised_uri = ''
    multilingual_blob = {}
    multilingual_uri = {}
    base = ''
    db_connection = ''
    schema_name = ''
    return Models(office, document, view_service,
                  legend_entry, public_law_restriction, geometry,
                  public_law_restriction_document,
                  localised_blob, localised_uri, multilingual_blob, multilingual_uri,
                  base, db_connection, schema_name)


def test_get_symbol_binary_content(theme_config, one_result_binary_session, png_binary, mock_get_models):
    with patch(
            'pyramid_oereb.core.adapter.DatabaseAdapter.get_session',
            return_value=one_result_binary_session()):
        with patch.object(StandardThemeConfigParser, 'get_models', return_value=mock_get_models):
            body, content_type = get_symbol({'identifier': "1"}, theme_config)
            assert content_type == 'image/png'
            assert body == b64.decode(binascii.b2a_base64(png_binary).decode('ascii'))


def test_get_symbol_no_symbol_content(theme_config, one_result_no_symbol_session, mock_get_models):
    with patch(
            'pyramid_oereb.core.adapter.DatabaseAdapter.get_session',
            return_value=one_result_no_symbol_session()):
        with patch.object(StandardThemeConfigParser, 'get_models', return_value=mock_get_models):
            with pytest.raises(HTTPServerError):
                get_symbol({'identifier': "1"}, theme_config)


def test_get_symbol_wrong_param(theme_config, one_result_no_symbol_session, mock_get_models):
    with patch(
            'pyramid_oereb.core.adapter.DatabaseAdapter.get_session',
            return_value=one_result_no_symbol_session()):
        with patch.object(StandardThemeConfigParser, 'get_models', return_value=mock_get_models):
            with pytest.raises(HTTPServerError):
                get_symbol({'identif': "1"}, theme_config)


def test_get_symbol_no_legend_entry(theme_config, no_result_session, mock_get_models):
    with patch(
            'pyramid_oereb.core.adapter.DatabaseAdapter.get_session',
            return_value=no_result_session()):
        with patch.object(StandardThemeConfigParser, 'get_models', return_value=mock_get_models):
            with pytest.raises(HTTPNotFound):
                get_symbol({'identifier': "2"}, theme_config)


def test_get_symbol_wrong_content(theme_config, one_result_wrong_content_session, mock_get_models):
    with patch('pyramid_oereb.core.adapter.DatabaseAdapter.get_session',
               return_value=one_result_wrong_content_session()):
        with patch.object(StandardThemeConfigParser, 'get_models', return_value=mock_get_models):
            with pytest.raises(HTTPServerError):
                get_symbol({'identifier': "1"}, theme_config)


def test_get_symbol_b64_content(theme_config, one_result_b64_session, png_binary, mock_get_models):
    with patch('pyramid_oereb.core.adapter.DatabaseAdapter.get_session',
               return_value=one_result_b64_session()):
        with patch.object(StandardThemeConfigParser, 'get_models', return_value=mock_get_models):
            body, content_type = get_symbol({'identifier': "1"}, theme_config)
            assert content_type == 'image/png'
            assert body == b64.decode(binascii.b2a_base64(png_binary).decode('ascii'))
