import pytest
from unittest.mock import patch

from pyramid_oereb.core import b64
from pyramid_oereb.contrib.data_sources.standard.sources.logo import DatabaseSource
from pyramid_oereb.core.records.image import ImageRecord
from pyramid_oereb.core.records.logo import LogoRecord


@pytest.fixture
def logo_source_params(db_connection):
    yield {
        "db_connection": db_connection,
        "model": "pyramid_oereb.contrib.data_sources.standard.models.main.Logo",
        "record_class": "pyramid_oereb.core.records.logo.LogoRecord"
    }


@pytest.fixture
def all_logo_result_session(session, query, png_binary):
    from pyramid_oereb.contrib.data_sources.standard.models.main import Logo

    class Query(query):

        def all(self):
            return [
                Logo(**{
                    'id': 1,
                    'code': 'ch',
                    'logo': {'de': b64.encode(png_binary)}
                }),
                Logo(**{
                    'id': 2,
                    'code': 'ch.ne',
                    'logo': {'de': b64.encode(png_binary)}
                }),
                Logo(**{
                    'id': 3,
                    'code': 'ch.2771',
                    'logo': {'de': b64.encode(png_binary)}
                })
            ]

    class Session(session):

        def query(self, term):
            return Query()

    yield Session


def test_read_all(logo_source_params, all_logo_result_session):
    source = DatabaseSource(**logo_source_params)
    with patch('pyramid_oereb.core.adapter.DatabaseAdapter.get_session', return_value=all_logo_result_session()):  # noqa: E501
        source.read()
        assert len(source.records) == 3
        assert isinstance(source.records[0], LogoRecord)
        assert isinstance(source.records[1], LogoRecord)
        assert isinstance(source.records[2], LogoRecord)
        assert isinstance(source.records[0].image_dict['de'], ImageRecord)
        assert isinstance(source.records[1].image_dict['de'], ImageRecord)
        assert isinstance(source.records[2].image_dict['de'], ImageRecord)
        assert source.records[0].code == 'ch'
        assert source.records[1].code == 'ch.ne'
        assert source.records[2].code == 'ch.2771'
