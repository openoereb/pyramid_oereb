import pytest
import datetime
from unittest.mock import patch

from pyramid_oereb.contrib.data_sources.standard.sources.data_integration import DatabaseSource
from pyramid_oereb.core.records.data_integration import DataIntegrationRecord


@pytest.fixture
def data_integration_source_params(db_connection):
    yield {
        "db_connection": db_connection,
        "model": "pyramid_oereb.contrib.data_sources.standard.models.main.DataIntegration"
    }


@pytest.fixture
def all_data_integration_result_session(session, query):
    from pyramid_oereb.contrib.data_sources.standard.models.main import DataIntegration

    class Query(query):

        def all(self):
            return [
                DataIntegration(**{
                    'id': '1',
                    'date': datetime.datetime(2023, 1, 1),
                    'theme_code': 'Theme1',
                    'office_id': 'Office1',
                    'checksum': 'abc'
                }),
                DataIntegration(**{
                    'id': '2',
                    'date': datetime.datetime(2023, 2, 1),
                    'theme_code': 'Theme2',
                    'office_id': 'Office2',
                    'checksum': 'def'
                })
            ]

    class Session(session):

        def query(self, term):
            return Query()

    yield Session


def test_read_all(data_integration_source_params, all_data_integration_result_session):
    source = DatabaseSource(**data_integration_source_params)
    with patch('pyramid_oereb.core.adapter.DatabaseAdapter.get_session', return_value=all_data_integration_result_session()):  # noqa: E501
        records = source.read()
        assert len(records) == 2
        assert isinstance(records[0], DataIntegrationRecord)
        assert isinstance(records[1], DataIntegrationRecord)
        assert records[0].date == datetime.datetime(2023, 1, 1)
        assert records[0].theme_identifier == 'Theme1'
        assert records[0].office_identifier == 'Office1'
        assert records[0].checksum == 'abc'
        assert records[1].date == datetime.datetime(2023, 2, 1)
        assert records[1].theme_identifier == 'Theme2'
        assert records[1].office_identifier == 'Office2'
        assert records[1].checksum == 'def'
