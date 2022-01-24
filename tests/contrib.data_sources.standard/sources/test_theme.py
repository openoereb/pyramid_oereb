import pytest
from unittest.mock import patch

from pyramid_oereb.contrib.data_sources.standard.sources.theme import DatabaseSource
from pyramid_oereb.core.records.theme import ThemeRecord


@pytest.fixture
def source_params():
    yield {
        "db_connection": "postgresql://postgres:postgres@123.123.123.123:5432/oereb_test_db",
        "model": "pyramid_oereb.contrib.data_sources.standard.models.main.Theme"
    }


@pytest.fixture
def all_result_session(session, query):
    from pyramid_oereb.contrib.data_sources.standard.models.main import Theme

    class Query(query):

        def all(self):
            return [
                Theme(**{
                    "id": "ch.Nutzungsplanung",
                    "code": "ch.Nutzungsplanung",
                    "sub_code": None,
                    "extract_index": 20,
                    "title": {
                        "de": "Nutzungsplanung (kantonal/kommunal)",
                        "fr": "Plans d’affectation (cantonaux/communaux)",
                        "it": "Piani di utilizzazione (cantonali/comunali)",
                        "rm": "Planisaziun d'utilisaziun (chantunal/communal)",
                        "en": "Land use plans (cantonal/municipal)"
                    }
                }),
                Theme(**{
                    "id": "ch.ProjektierungszonenNationalstrassen",
                    "code": "ch.ProjektierungszonenNationalstrassen",
                    "sub_code": None,
                    "extract_index": 110,
                    "title": {
                        "de": "Projektierungszonen Nationalstrassen",
                        "fr": "Zones réservées des routes nationales",
                        "it": "Zone riservate per le strade nazionali",
                        "rm": "Zonas da projectaziun da las vias naziunalas",
                        "en": "Reserved zones for motorways"
                    }
                })
            ]

    class Session(session):

        def query(self, term):
            return Query()

    yield Session


def test_read_all(source_params, all_result_session):
    source = DatabaseSource(**source_params)
    with patch('pyramid_oereb.core.adapter.DatabaseAdapter.get_session', return_value=all_result_session()):
        source.read()
        assert len(source.records) == 2
        assert isinstance(source.records[0], ThemeRecord)
        assert isinstance(source.records[1], ThemeRecord)
        record = source.records[0]
        assert record.title == {
            "de": "Nutzungsplanung (kantonal/kommunal)",
            "fr": "Plans d’affectation (cantonaux/communaux)",
            "it": "Piani di utilizzazione (cantonali/comunali)",
            "rm": "Planisaziun d'utilisaziun (chantunal/communal)",
            "en": "Land use plans (cantonal/municipal)"
        }
        assert record.code == "ch.Nutzungsplanung"
        assert record.sub_code is None
        assert record.extract_index == 20
        assert record.document_records is None
        assert record.identifier == "ch.Nutzungsplanung"
