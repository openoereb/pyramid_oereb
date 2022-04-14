import pytest
from unittest.mock import patch

from pyramid_oereb.contrib.data_sources.standard.sources.disclaimer import DatabaseSource
from pyramid_oereb.core.records.disclaimer import DisclaimerRecord


@pytest.fixture
def disclaimer_source_params(db_connection):
    yield {
        "db_connection": db_connection,
        "model": "pyramid_oereb.contrib.data_sources.standard.models.main.Disclaimer"
    }


@pytest.fixture
def all_disclaimer_result_session(session, query):
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
                    'id': 2,
                    'title': {'de': 'Titel2'},
                    'content': {'de': 'Inhalt2'}
                })
            ]

    class Session(session):

        def query(self, term):
            return Query()

    yield Session


def test_read_all(disclaimer_source_params, all_disclaimer_result_session):
    source = DatabaseSource(**disclaimer_source_params)
    with patch('pyramid_oereb.core.adapter.DatabaseAdapter.get_session', return_value=all_disclaimer_result_session()):  # noqa: E501
        source.read()
        assert len(source.records) == 2
        assert isinstance(source.records[0], DisclaimerRecord)
        assert isinstance(source.records[1], DisclaimerRecord)
        assert source.records[0].title == {'de': 'Titel1'}
        assert source.records[0].content == {'de': 'Inhalt1'}
