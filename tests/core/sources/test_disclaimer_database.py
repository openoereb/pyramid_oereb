# -*- coding: utf-8 -*-

import pytest

from pyramid_oereb.core.adapter import DatabaseAdapter


@pytest.fixture
def disclaimer_data(dbsession, transact):
    from pyramid_oereb.contrib.data_sources.standard.models.main import Disclaimer
    del transact
    disclaimers = [
        Disclaimer(**{
            'id': 1,
            'title': {
                'de': u'Haftungsausschluss Kataster der belasteten Standorte',
                'fr': u'Clause de non-responsabilité du cadastre des sites pollués (CSP)',
                'it': u'Clausola di esclusione della responsabilità ...',
                'rm': u''
            },
            'content': {
                'de': u'Der Kataster der belasteten Standorte (KbS) \
                      wurde anhand der vom Bundesamt für Umwelt BAFU fe ...',
                'fr': u'Le cadastre des sites pollués (CSP) est établi d’après \
                      les critères émis par l’Office fédéral ...',
                'it': u'Il catasto dei siti inquinati (CSIN) è stato elaborato sulla \
                      base dei criteri definiti dall ...',
                'rm': u'',
            }
        })
    ]
    dbsession.add_all(disclaimers)
    dbsession.flush()
    yield disclaimers


@pytest.mark.run(order=2)
def test_init(pyramid_oereb_test_config):
    from pyramid_oereb.contrib.data_sources.standard.sources.disclaimer import DatabaseSource
    from pyramid_oereb.contrib.data_sources.standard.models.main import Disclaimer
    source = DatabaseSource(
        **pyramid_oereb_test_config.get_disclaimer_config().get('source').get('params')
    )
    assert isinstance(source._adapter_, DatabaseAdapter)
    assert source._model_ == Disclaimer


@pytest.mark.run(order=2)
def test_read(pyramid_oereb_test_config, disclaimer_data):
    from pyramid_oereb.contrib.data_sources.standard.sources.disclaimer import DatabaseSource

    source = DatabaseSource(
        **pyramid_oereb_test_config.get_disclaimer_config().get('source').get('params')
    )
    source.read()
    assert len(source.records) == 1
    assert source.records[0].title['de'] == disclaimer_data[0].title['de']
