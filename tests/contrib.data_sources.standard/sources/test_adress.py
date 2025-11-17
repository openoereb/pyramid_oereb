import pytest
from unittest.mock import patch

from geoalchemy2.elements import WKTElement
from sqlalchemy.exc import NoResultFound

from pyramid_oereb.contrib.data_sources.standard.sources.address import DatabaseSource
from pyramid_oereb.core.views.webservice import Parameter
from pyramid_oereb.core.records.address import AddressRecord


@pytest.fixture
def address_source_params(db_connection):
    yield {
        "db_connection": db_connection,
        "model": "pyramid_oereb.contrib.data_sources.standard.models.main.Address",
        "record_class": "pyramid_oereb.core.records.address.AddressRecord"
    }


@pytest.fixture
def wkb_point():
    yield WKTElement('SRID=2056;POINT(1 1)', extended=True)


@pytest.fixture
def one_address_result_session(session, query, wkb_point):
    from pyramid_oereb.contrib.data_sources.standard.models.main import Address

    class Query(query):

        def limit(self, limit):
            class LimitedQuery(Query):
                def all(self):
                    return [
                        Address(**{
                            'street_name': 'teststreet',
                            'street_number': '99a',
                            'zip_code': 4050,
                            'geom': wkb_point
                        })
                    ]
            return LimitedQuery()

    class Session(session):

        def query(self, term):
            return Query()

    yield Session


@pytest.fixture
def no_result_session(session, query, wkb_point):

    class Query(query):

        class LimitedQuery(query):
            def all(self):
                raise NoResultFound

        def limit(self, limit):
            return self.LimitedQuery()

        def filter(self, term):
            return self

    class Session(session):

        def query(self, term):
            return Query()

    yield Session


def test_read_one(address_source_params, one_address_result_session):
    source = DatabaseSource(**address_source_params)
    with patch('pyramid_oereb.core.adapter.DatabaseAdapter.get_session', return_value=one_address_result_session()):  # noqa: E501
        source.read(Parameter('xml'), 'teststreet', 4050, '99a')
        assert len(source.records) == 1
        assert isinstance(source.records[0], AddressRecord)
        assert source.records[0].street_name == 'teststreet'
        assert source.records[0].street_number == '99a'
        assert source.records[0].zip_code == 4050
        assert source.records[0].geom.coords[0] == (1.0, 1.0)


def test_read_none_found(address_source_params, no_result_session):
    source = DatabaseSource(**address_source_params)
    with patch('pyramid_oereb.core.adapter.DatabaseAdapter.get_session', return_value=no_result_session()):
        source.read(Parameter('xml'), 'teststreet', 4050, '99a')
        assert len(source.records) == 0
