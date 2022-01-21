import pytest
from unittest.mock import patch

from sqlalchemy import String
from sqlalchemy.orm import declarative_base

from pyramid_oereb.contrib.data_sources.standard.models.theme import get_view_service, get_legend_entry
from pyramid_oereb.contrib.data_sources.standard.sources.legend import DatabaseSource
from pyramid_oereb.core.records.image import ImageRecord
from pyramid_oereb.core.views.webservice import Parameter
from pyramid_oereb.core.records.view_service import LegendEntryRecord


@pytest.fixture
def legend_entry_model_class():
    Base = declarative_base()
    ViewService = get_view_service(Base, 'test', String)
    yield get_legend_entry(Base, 'test', String, ViewService)


@pytest.fixture
def source_params(legend_entry_model_class):
    yield {
        "db_connection": "postgresql://postgres:postgres@123.123.123.123:5432/oereb_test_db",
        "model": legend_entry_model_class
    }


@pytest.fixture
def all_result_session(session, query, legend_entry_model_class, png_binary):


    class Query(query):

        def all(self):
            return [
                legend_entry_model_class(**{
                    'id': '1',
                    'symbol': png_binary,
                    'legend_text': {'de': 'testlegende'},
                    'type_code': 'testCode',
                    'type_code_list': 'testCode,testCode2,testCode3',
                    'theme': 'ch.TestThema',
                    'sub_theme': 'ch.SubTestThema',
                    'view_service_id': '1'
                })
            ]

    class Session(session):

        def query(self, term):
            return Query()

    yield Session


def test_read_all(source_params, all_result_session, png_binary):
    source = DatabaseSource(**source_params)
    with patch('pyramid_oereb.core.adapter.DatabaseAdapter.get_session', return_value=all_result_session()):
        source.read(Parameter('xml'), type_code='testCode')
        assert len(source.records) == 1
        assert isinstance(source.records[0], LegendEntryRecord)
        assert isinstance(source.records[0].symbol, ImageRecord)
        assert source.records[0].legend_text == {'de': 'testlegende'}
        assert source.records[0].type_code == 'testCode'
        assert source.records[0].type_code_list == 'testCode,testCode2,testCode3'
        assert source.records[0].theme == 'ch.TestThema'
        assert source.records[0].sub_theme == 'ch.SubTestThema'
        assert source.records[0].view_service_id == '1'


def test_read_all_missing_type_code(source_params, all_result_session):
    source = DatabaseSource(**source_params)
    with patch('pyramid_oereb.core.adapter.DatabaseAdapter.get_session', return_value=all_result_session()):
        with pytest.raises(AttributeError):
            source.read(Parameter('xml'))
