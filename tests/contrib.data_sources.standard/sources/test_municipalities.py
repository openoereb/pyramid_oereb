import pytest
from unittest.mock import patch

from geoalchemy2 import WKTElement
from geoalchemy2.shape import to_shape
from pyramid_oereb.contrib.data_sources.standard.sources.municipality import DatabaseSource
from pyramid_oereb.core.records.municipality import MunicipalityRecord


@pytest.fixture
def municipalities_source_params(db_connection):
    yield {
        "db_connection": db_connection,
        "model": "pyramid_oereb.contrib.data_sources.standard.models.main.Municipality"
    }


@pytest.fixture
def wkb_multipolygon():
    yield WKTElement(
        "SRID=2056;MULTIPOLYGON((("
        "2609229.759 1263666.789,"
        "2609231.206 1263670.558,"
        "2609229.561 1263672.672,"
        "2609229.472 1263675.47,"
        "2609251.865 1263727.506,"
        "2609275.847 1263783.29,"
        "2609229.759 1263666.789"
        ")))",
        extended=True
    )


@pytest.fixture
def municipalities(wkb_multipolygon):
    from pyramid_oereb.contrib.data_sources.standard.models.main import Municipality
    yield [
        Municipality(**{
            "fosnr": 2771,
            "geom": wkb_multipolygon,
            "name": "Oberwil (BL)",
            "published": True
        }),
        Municipality(**{
            "fosnr": 2777,
            "geom": wkb_multipolygon,
            "name": "Testwil",
            "published": True
        })
    ]


@pytest.fixture
def all_municipalities_result_session(session, query, municipalities):

    class Query(query):

        def all(self):
            return municipalities

    class Session(session):

        def query(self, term):
            return Query()

    yield Session


@pytest.fixture
def all_municipalities_filtered_result_session(session, query, municipalities):

    class Query(query):

        def all(self):
            return [municipalities[0]]

        def filter(self, term):
            assert str(term) == 'test.municipality.fosnr = :fosnr_1'
            return self

    class Session(session):

        def query(self, term):
            return Query()

    yield Session


def test_read_all(municipalities_source_params, all_municipalities_result_session, wkb_multipolygon):
    source = DatabaseSource(**municipalities_source_params)
    with patch('pyramid_oereb.core.adapter.DatabaseAdapter.get_session', return_value=all_municipalities_result_session()):  # noqa: E501
        source.read()
        assert len(source.records) == 2
        assert isinstance(source.records[0], MunicipalityRecord)
        assert isinstance(source.records[1], MunicipalityRecord)
        assert source.records[0].fosnr == 2771
        assert source.records[0].geom == to_shape(wkb_multipolygon).wkt
        assert source.records[0].name == "Oberwil (BL)"
        assert source.records[0].published
