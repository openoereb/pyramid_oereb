import pytest
from unittest.mock import patch

from sqlalchemy import String
from sqlalchemy.orm import declarative_base

from pyramid_oereb.contrib.data_sources.standard.models import get_office
from pyramid_oereb.contrib.data_sources.standard.sources.office import DatabaseSource
from pyramid_oereb.core.records.office import OfficeRecord


@pytest.fixture
def office_source_params(db_connection):
    yield {
        "db_connection": db_connection,
        "model": "pyramid_oereb.contrib.data_sources.standard.models.main.Office"
    }


@pytest.fixture
def office_model_class():
    Base = declarative_base()
    Office = get_office(Base, 'test', String)
    yield Office


@pytest.fixture
def all_office_result_session(session, query, office_model_class):

    class Query(query):

        def all(self):
            return [
                office_model_class(**{
                    'id': 1,
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
                    'id': 2,
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

    class Session(session):

        def query(self, term):
            return Query()

    yield Session


def test_read_all(office_source_params, all_office_result_session):
    source = DatabaseSource(**office_source_params)
    with patch('pyramid_oereb.core.adapter.DatabaseAdapter.get_session', return_value=all_office_result_session()):  # noqa: E501
        source.read()
        assert len(source.records) == 2
        assert isinstance(source.records[0], OfficeRecord)
        assert isinstance(source.records[1], OfficeRecord)
        office_record = source.records[0]
        assert office_record.name == {'de': 'Office1'}
        assert office_record.uid == 'abcde'
        assert office_record.line1 == 'entrance 1'
        assert office_record.line2 == 'building 1'
        assert office_record.street == 'Office1 street'
        assert office_record.number == '1a'
        assert office_record.postal_code == 4444
        assert office_record.city == 'Office1 City'
        assert office_record.identifier == 1
