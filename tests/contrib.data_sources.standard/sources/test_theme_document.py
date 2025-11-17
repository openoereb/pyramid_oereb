import pytest
from unittest.mock import patch

from pyramid_oereb.contrib.data_sources.standard.sources.theme_document import DatabaseSource
from pyramid_oereb.core.records.theme_document import ThemeDocumentRecord


@pytest.fixture
def source_params(db_connection):
    yield {
        "db_connection": db_connection,
        "model": "pyramid_oereb.contrib.data_sources.standard.models.main.ThemeDocument",
        "record_class": "pyramid_oereb.core.records.theme_document.ThemeDocumentRecord"
    }


@pytest.fixture
def all_result_session(session, query):
    from pyramid_oereb.contrib.data_sources.standard.models.main import ThemeDocument

    class Query(query):

        def all(self):
            return [
                ThemeDocument(**{
                    "theme_id": "ch.Nutzungsplanung",
                    "document_id": "ch.admin.bk.sr.700",
                    "article_numbers":  None
                }),
                ThemeDocument(**{
                    "theme_id": "ch.ProjektierungszonenNationalstrassen",
                    "document_id": "ch.admin.bk.sr.725.11",
                    "article_numbers":  None
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
        assert isinstance(source.records[0], ThemeDocumentRecord)
        assert isinstance(source.records[1], ThemeDocumentRecord)
        record = source.records[0]
        assert record.theme_id == "ch.Nutzungsplanung"
        assert record.document_id == "ch.admin.bk.sr.700"
        assert record.article_numbers is None
