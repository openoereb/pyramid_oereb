import pytest
from unittest.mock import patch

from pyramid_oereb.contrib.data_sources.standard.sources.glossary import DatabaseSource
from pyramid_oereb.core.views.webservice import Parameter
from pyramid_oereb.core.records.glossary import GlossaryRecord


@pytest.fixture
def glossary_source_params(db_connection):
    yield {
        "db_connection": db_connection,
        "model": "pyramid_oereb.contrib.data_sources.standard.models.main.Glossary"
    }


@pytest.fixture
def all_glossary_result_session(session, query):
    from pyramid_oereb.contrib.data_sources.standard.models.main import Glossary

    class Query(query):

        def all(self):
            return [
                Glossary(**{
                    'id': 1,
                    'title': {'de': 'Test1'},
                    'content': {'de': 'Das ist Test1'}
                }),
                Glossary(**{
                    'id': 2,
                    'title': {'de': 'Test2'},
                    'content': {'de': 'Das ist Test2'}
                }),
                Glossary(**{
                    'id': 3,
                    'title': {'de': 'Test3'},
                    'content': {'de': 'Das ist Test3'}
                })
            ]

    class Session(session):

        def query(self, term):
            return Query()

    yield Session


def test_read_all(glossary_source_params, all_glossary_result_session):
    source = DatabaseSource(**glossary_source_params)
    with patch('pyramid_oereb.core.adapter.DatabaseAdapter.get_session', return_value=all_glossary_result_session()):  # noqa: E501
        source.read(Parameter('xml'))
        assert len(source.records) == 3
        assert isinstance(source.records[0], GlossaryRecord)
        assert isinstance(source.records[1], GlossaryRecord)
        assert isinstance(source.records[2], GlossaryRecord)
        assert source.records[0].title == {'de': 'Test1'}
        assert source.records[1].title == {'de': 'Test2'}
        assert source.records[2].title == {'de': 'Test3'}
