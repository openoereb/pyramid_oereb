import pytest
from unittest.mock import patch

from pyramid_oereb.contrib.data_sources.standard.sources.document_types import DatabaseSource
from pyramid_oereb.core.records.document_types import DocumentTypeRecord


@pytest.fixture
def document_types_source_params(db_connection):
    yield {
        "db_connection": db_connection,
        "model": "pyramid_oereb.contrib.data_sources.standard.models.main.DocumentTypeText",
        "record_class": "pyramid_oereb.core.records.document_types.DocumentTypeRecord"
    }


@pytest.fixture
def all_document_types_result_session(session, query):
    from pyramid_oereb.contrib.data_sources.standard.models.main import DocumentTypeText

    class Query(query):

        def all(self):
            return [
                DocumentTypeText(**{
                    'code': 'Rechtsvorschrift',
                    'title': {'de': 'Rechtsvorschrift'}
                }),
                DocumentTypeText(**{
                    'code': 'GesetzlicheGrundlage',
                    'title': {'de': 'Gesetzliche Grundlage'}
                }),
                DocumentTypeText(**{
                    'code': 'Hinweis',
                    'title': {'de': 'Hinweis'}
                })
            ]

    class Session(session):

        def query(self, term):
            return Query()

    yield Session


def test_read_all(document_types_source_params, all_document_types_result_session):
    source = DatabaseSource(**document_types_source_params)
    with patch('pyramid_oereb.core.adapter.DatabaseAdapter.get_session', return_value=all_document_types_result_session()):  # noqa: E501
        source.read()
        assert len(source.records) == 3
        assert isinstance(source.records[0], DocumentTypeRecord)
        assert isinstance(source.records[1], DocumentTypeRecord)
        assert isinstance(source.records[2], DocumentTypeRecord)
        assert source.records[0].title == {'de': 'Rechtsvorschrift'}
        assert source.records[1].title == {'de': 'Gesetzliche Grundlage'}
        assert source.records[2].title == {'de': 'Hinweis'}
