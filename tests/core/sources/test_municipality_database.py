# -*- coding: utf-8 -*-

import pytest


@pytest.fixture
def municipality_data(dbsession, transact):
    from pyramid_oereb.contrib.data_sources.standard.models.main import Municipality
    del transact
    municipalities = [
        Municipality(**{
            'fosnr': 1234,
            'name': u'Test',
            'published': True,
            'geom': 'SRID=2056;MULTIPOLYGON(((0 0, 0 10, 10 10, 10 0, 0 0)))',
        })
    ]
    dbsession.add_all(municipalities)
    dbsession.flush()
    yield municipalities


@pytest.mark.run(order=2)
def test_init(pyramid_oereb_test_config):
    from pyramid_oereb.contrib.data_sources.standard.sources.municipality import DatabaseSource
    from pyramid_oereb.core.adapter import DatabaseAdapter
    from pyramid_oereb.contrib.data_sources.standard.models.main import Municipality

    source = DatabaseSource(**pyramid_oereb_test_config.get_municipality_config().get('source').get('params'))
    assert isinstance(source._adapter_, DatabaseAdapter)
    assert source._model_ == Municipality


def test_read(pyramid_oereb_test_config, municipality_data):
    from pyramid_oereb.contrib.data_sources.standard.sources.municipality import DatabaseSource

    source = DatabaseSource(**pyramid_oereb_test_config.get_municipality_config().get('source').get('params'))
    source.read()
    assert isinstance(source.records, list)
    assert len(source.records) == len(municipality_data)
    assert source.records[0].fosnr == municipality_data[0].fosnr
