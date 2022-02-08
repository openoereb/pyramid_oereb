import pytest
from unittest.mock import patch

from pyramid_oereb.contrib.data_sources.standard.sources.real_estate_type import DatabaseSource
from pyramid_oereb.core.views.webservice import Parameter
from pyramid_oereb.core.records.real_estate_type import RealEstateTypeRecord


@pytest.fixture
def real_estate_type_source_params(db_connection):
    yield {
        "db_connection": db_connection,
        "model": "pyramid_oereb.contrib.data_sources.standard.models.main.RealEstateType"
    }


@pytest.fixture
def all_real_estate_type_result_session(session, query):
    from pyramid_oereb.contrib.data_sources.standard.models.main import RealEstateType

    class Query(query):

        def all(self):
            return [
                RealEstateType(**{
                    "id": 1,
                    "code": "Liegenschaft",
                    "title": {
                        "de": "Liegenschaft",
                        "fr": "Bien-fonds",
                        "it": "Bene immobile",
                        "rm": "Bain immobigliar",
                        "en": "Property"
                    }
                }),
                RealEstateType(**{
                    "id": 2,
                    "code": "SelbstRecht.Baurecht",
                    "title": {
                        "de": "Baurecht",
                        "fr": "Droit de superficie",
                        "it": "Diritto di superficie",
                        "rm": "Dretg da construcziun",
                        "en": "Building right"
                    }
                }),
                RealEstateType(**{
                    "id": 3,
                    "code": "SelbstRecht.Quellenrecht",
                    "title": {
                        "de": "Quellenrecht",
                        "fr": "Droit de source",
                        "it": "Diritto di sorgente",
                        "rm": "Dretg da funtauna",
                        "en": "Right to spring water"
                    }
                }),
                RealEstateType(**{
                    "id": 4,
                    "code": "SelbstRecht.Konzessionsrecht",
                    "title": {
                        "de": "Konzessionsrecht",
                        "fr": "Droit de concession",
                        "it": "Diritto di concessione",
                        "rm": "Dretg da concessiun",
                        "en": "Right to licence"
                    }
                }),
                RealEstateType(**{
                    "id": 5,
                    "code": "SelbstRecht.weitere",
                    "title": {
                        "de": "weiteres SDR",
                        "fr": "Autre DDP",
                        "it": "altre DSP",
                        "rm": "ulteriur DIP",
                        "en": "other distinct and permanent rights"
                    }
                }),
                RealEstateType(**{
                    "id": 6,
                    "code": "Bergwerk",
                    "title": {
                        "de": "Bergwerk",
                        "fr": "Mine",
                        "it": "Miniera",
                        "rm": "Miniera",
                        "en": "Mine"
                    }
                })
            ]

    class Session(session):

        def query(self, term):
            return Query()

    yield Session


def test_read_all(real_estate_type_source_params, all_real_estate_type_result_session):
    source = DatabaseSource(**real_estate_type_source_params)
    with patch('pyramid_oereb.core.adapter.DatabaseAdapter.get_session', return_value=all_real_estate_type_result_session()):  # noqa: E501
        source.read(Parameter('xml'))
        assert len(source.records) == 6
        assert isinstance(source.records[0], RealEstateTypeRecord)
        assert isinstance(source.records[1], RealEstateTypeRecord)
        record = source.records[0]
        assert record.title == {
            "de": "Liegenschaft",
            "fr": "Bien-fonds",
            "it": "Bene immobile",
            "rm": "Bain immobigliar",
            "en": "Property"
        }
        assert record.code == "Liegenschaft"
