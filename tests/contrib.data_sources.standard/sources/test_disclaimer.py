import pytest
from unittest.mock import patch

from pyramid_oereb.contrib.data_sources.standard.sources.disclaimer import DatabaseSource
from pyramid_oereb.core.views.webservice import Parameter
from pyramid_oereb.core.records.disclaimer import DisclaimerRecord


@pytest.fixture
def source_params():
    yield {
        "db_connection": "postgresql://postgres:postgres@123.123.123.123:5432/oereb_test_db",
        "model": "pyramid_oereb.contrib.data_sources.standard.models.main.Disclaimer"
    }


@pytest.fixture
def all_result_session(session, query):
    from pyramid_oereb.contrib.data_sources.standard.models.main import Disclaimer
    class Query(query):
        def all(self):
            return [
                Disclaimer(**{
                    'id': 1,
                    'title': {'de': 'Titel1'},
                    'content': {'de': 'Inhalt1'}
                }),
                Disclaimer(**{
                    'id': 1,
                    'title': {'de': 'Titel2'},
                    'content': {'de': 'Inhalt2'}
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
        assert len(source.records) == 2
        assert isinstance(source.records[0], DisclaimerRecord)
        assert isinstance(source.records[1], DisclaimerRecord)
        assert source.records[0].title == {'de': 'Titel1'}
        assert source.records[0].content == {'de': 'Inhalt1'}
