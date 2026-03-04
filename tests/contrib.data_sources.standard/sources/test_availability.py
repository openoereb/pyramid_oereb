import pytest
from unittest.mock import patch

from pyramid_oereb.contrib.data_sources.standard.sources.availability import DatabaseSource
from pyramid_oereb.core.records.availability import AvailabilityRecord


@pytest.fixture
def availability_source_params(db_connection):
    yield {
        "db_connection": db_connection,
        "model": "pyramid_oereb.contrib.data_sources.standard.models.main.Availability"
    }


@pytest.fixture
def availability_results_session(session, query):
    from pyramid_oereb.contrib.data_sources.standard.models.main import Availability

    class Query(query):

        def all(self):
            return [
                Availability(**{
                    'municipality_fosnr': 1234,
                    'theme_code': 'Theme1',
                    'available': True
                }),
                Availability(**{
                    'municipality_fosnr': 5678,
                    'theme_code': 'Theme2',
                    'available': False
                })
            ]

    class Session(session):

        def query(self, term):
            return Query()

    yield Session


@pytest.fixture
def no_result_session(session, query):

    class Query(query):

        def all(self):
            return []

    class Session(session):

        def query(self, term):
            return Query()

    yield Session


def test_read_all(availability_source_params, availability_results_session):
    source = DatabaseSource(**availability_source_params)
    with patch('pyramid_oereb.core.adapter.DatabaseAdapter.get_session',
               return_value=availability_results_session()):
        records = source.read()
        assert len(records) == 2
        assert isinstance(records[0], AvailabilityRecord)
        assert records[0].fosnr == 1234
        assert records[0].theme_code == 'Theme1'
        assert records[0].available is True
        assert isinstance(records[1], AvailabilityRecord)
        assert records[1].fosnr == 5678
        assert records[1].theme_code == 'Theme2'
        assert records[1].available is False


def test_read_empty(availability_source_params, no_result_session):
    source = DatabaseSource(**availability_source_params)
    with patch('pyramid_oereb.core.adapter.DatabaseAdapter.get_session',
               return_value=no_result_session()):
        records = source.read()
        assert len(records) == 0
