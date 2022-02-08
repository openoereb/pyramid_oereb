import pytest
from unittest.mock import patch

from pyramid_oereb.contrib.data_sources.standard.sources.general_information import DatabaseSource
from pyramid_oereb.core.records.general_information import GeneralInformationRecord


@pytest.fixture
def general_information_source_params(db_connection):
    yield {
        "db_connection": db_connection,
        "model": "pyramid_oereb.contrib.data_sources.standard.models.main.GeneralInformation"
    }


@pytest.fixture
def general_information_all_result_session(session, query):
    from pyramid_oereb.contrib.data_sources.standard.models.main import GeneralInformation

    class Query(query):

        def all(self):
            return [
                GeneralInformation(**{
                    'id': 1,
                    'title': {'de': 'Test1'},
                    'content': {'de': 'Das ist Test1'}
                }),
                GeneralInformation(**{
                    'id': 2,
                    'title': {'de': 'Test2'},
                    'content': {'de': 'Das ist Test2'}
                }),
                GeneralInformation(**{
                    'id': 3,
                    'title': {'de': 'Test3'},
                    'content': {'de': 'Das ist Test3'}
                })
            ]

    class Session(session):

        def query(self, term):
            return Query()

    yield Session


def test_read_all(general_information_source_params, general_information_all_result_session):
    source = DatabaseSource(**general_information_source_params)
    with patch('pyramid_oereb.core.adapter.DatabaseAdapter.get_session', return_value=general_information_all_result_session()):  # noqa: E501
        source.read()
        assert len(source.records) == 3
        assert isinstance(source.records[0], GeneralInformationRecord)
        assert isinstance(source.records[1], GeneralInformationRecord)
        assert isinstance(source.records[2], GeneralInformationRecord)
        assert source.records[0].title == {'de': 'Test1'}
        assert source.records[1].title == {'de': 'Test2'}
        assert source.records[2].title == {'de': 'Test3'}
