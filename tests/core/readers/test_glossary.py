# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.core.sources import Base
from pyramid_oereb.core.readers.glossary import GlossaryReader
from pyramid_oereb.core.records.glossary import GlossaryRecord


@pytest.fixture
def glossary_data(dbsession, transact):
    from pyramid_oereb.contrib.data_sources.standard.models.main import Glossary
    del transact
    glossary = [
        Glossary(**{
            'id': 1,
            'title': {u'fr': u'SGRF', u'de': u'AGI'},
            'content': {'fr': u'Service de la géomatique et du registre foncier',
                        'de': u'Amt für Geoinformation'},
        })
    ]
    dbsession.add_all(glossary)
    dbsession.flush()
    yield glossary


@pytest.mark.run(order=2)
def test_init(pyramid_oereb_test_config):

    reader = GlossaryReader(
        pyramid_oereb_test_config.get_glossary_config().get('source').get('class'),
        **pyramid_oereb_test_config.get_glossary_config().get('source').get('params')
    )
    assert isinstance(reader._source_, Base)


@pytest.mark.run(order=2)
def test_read(pyramid_oereb_test_config, glossary_data):
    reader = GlossaryReader(
        pyramid_oereb_test_config.get_glossary_config().get('source').get('class'),
        **pyramid_oereb_test_config.get_glossary_config().get('source').get('params')
    )
    results = reader.read()
    assert isinstance(results, list)
    assert isinstance(results[0], GlossaryRecord)
    assert len(results) == 1
    assert results[0].title['fr'] == glossary_data[0].title['fr']
    assert results[0].title['de'] == glossary_data[0].title['de']
    assert 'Geoinformation' in results[0].content['de']
