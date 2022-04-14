# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.core.adapter import DatabaseAdapter


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
    from pyramid_oereb.contrib.data_sources.standard.sources.glossary import DatabaseSource
    from pyramid_oereb.contrib.data_sources.standard.models.main import Glossary

    source = DatabaseSource(**pyramid_oereb_test_config.get_glossary_config().get('source').get('params'))
    assert isinstance(source._adapter_, DatabaseAdapter)
    assert source._model_ == Glossary


@pytest.mark.run(order=2)
def test_read(pyramid_oereb_test_config, glossary_data):
    from pyramid_oereb.contrib.data_sources.standard.sources.glossary import DatabaseSource

    source = DatabaseSource(**pyramid_oereb_test_config.get_glossary_config().get('source').get('params'))
    source.read()
    results = source.records
    assert len(results) == 1
    assert results[0].title['fr'] == glossary_data[0].title['fr']
