import pytest
from unittest.mock import patch

from pyramid_oereb.contrib.data_sources.standard.sources.law_status import DatabaseSource
from pyramid_oereb.core.views.webservice import Parameter
from pyramid_oereb.core.records.law_status import LawStatusRecord


@pytest.fixture
def source_params():
    yield {
        "db_connection": "postgresql://postgres:postgres@123.123.123.123:5432/oereb_test_db",
        "model": "pyramid_oereb.contrib.data_sources.standard.models.main.LawStatus"
    }


@pytest.fixture
def all_result_session(session, query):
    from pyramid_oereb.contrib.data_sources.standard.models.main import LawStatus

    class Query(query):

        def all(self):
            return [
                LawStatus(**{
                    'title': {'de': 'In Kraft'},
                    'code': 'inKraft'
                }),
                LawStatus(**{
                    'title': {'de': 'Änderung mit Vorwirkung'},
                    'code': 'AenderungMitVorwirkung'
                }),
                LawStatus(**{
                    'title': {'de': 'Änderung ohne Vorwirkung'},
                    'code': 'AenderungOhneVorwirkung'
                })
            ]

    class Session(session):

        def query(self, term):
            return Query()

    yield Session


def test_read_one(source_params, all_result_session):
    source = DatabaseSource(**source_params)
    with patch('pyramid_oereb.core.adapter.DatabaseAdapter.get_session', return_value=all_result_session()):
        source.read(Parameter('xml'))
        assert len(source.records) == 3
        assert isinstance(source.records[0], LawStatusRecord)
        assert isinstance(source.records[1], LawStatusRecord)
        assert isinstance(source.records[2], LawStatusRecord)
        assert source.records[0].title == {'de': 'In Kraft'}
        assert source.records[1].title == {'de': 'Änderung mit Vorwirkung'}
        assert source.records[2].title == {'de': 'Änderung ohne Vorwirkung'}
