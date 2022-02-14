import pytest
from unittest.mock import patch

from pyramid_oereb.contrib.data_sources.standard.sources.map_layering import DatabaseSource
from pyramid_oereb.core.records.map_layering import MapLayeringRecord


@pytest.fixture
def map_layering_source_params(db_connection):
    yield {
        "db_connection": db_connection,
        "model": "pyramid_oereb.contrib.data_sources.standard.models.main.MapLayering"
    }


@pytest.fixture
def view_service_url():
    yield "https://wms.geo.admin.ch/?" \
          "service=WMS&" \
          "version=1.3.0&" \
          "request=GetMap&" \
          "layers=ch.vbs.kataster-belasteter-standorte-militaer_v2_0.oereb&" \
          "style=default&" \
          "crs=EPSG:2056&" \
          "bbox=2475000,1060000,2845000,1310000&" \
          "width=740&" \
          "height=500&" \
          "format=image/png"


@pytest.fixture
def all_map_layering_result_session(session, query, view_service_url):
    from pyramid_oereb.contrib.data_sources.standard.models.main import MapLayering

    class Query(query):

        def all(self):
            return [
                MapLayering(**{
                    'id': 1,
                    'view_service': {"fr": view_service_url},
                    'layer_index': 1,
                    'layer_opacity': 1.0
                })
            ]

    class Session(session):

        def query(self, term):
            return Query()

    yield Session


def test_read_all(map_layering_source_params, all_map_layering_result_session, view_service_url):
    source = DatabaseSource(**map_layering_source_params)
    with patch('pyramid_oereb.core.adapter.DatabaseAdapter.get_session', return_value=all_map_layering_result_session()):  # noqa: E501
        source.read()
        assert len(source.records) == 1
        assert isinstance(source.records[0], MapLayeringRecord)
        assert isinstance(source.records[0].view_service, dict)
        assert source.records[0].view_service['fr'] == view_service_url
        assert source.records[0].layer_index == 1
        assert source.records[0].layer_opacity == 1.0
