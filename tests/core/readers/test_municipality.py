# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.core.records.municipality import MunicipalityRecord
from pyramid_oereb.core.sources import Base
from pyramid_oereb.core.readers.municipality import MunicipalityReader


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
    reader = MunicipalityReader(
        pyramid_oereb_test_config.get_municipality_config().get('source').get('class'),
        **pyramid_oereb_test_config.get_municipality_config().get('source').get('params')
    )
    assert isinstance(reader._source_, Base)


@pytest.mark.run(order=2)
def test_read(pyramid_oereb_test_config, municipality_data):
    reader = MunicipalityReader(
        pyramid_oereb_test_config.get_municipality_config().get('source').get('class'),
        **pyramid_oereb_test_config.get_municipality_config().get('source').get('params')
    )
    results = reader.read()
    assert isinstance(results, list)
    assert len(results) == 1
    result = results[0]
    expected = municipality_data[0]
    assert isinstance(result, MunicipalityRecord)
    assert result.fosnr == expected.fosnr
    assert result.name == expected.name
    assert result.published

# TODO: Implement tests for return values, not possible now, cause there is no data in database
