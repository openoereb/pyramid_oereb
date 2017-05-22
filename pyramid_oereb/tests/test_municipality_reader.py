# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.records.municipality import MunicipalityRecord
from pyramid_oereb.lib.sources import Base
from pyramid_oereb.lib.readers.municipality import MunicipalityReader


@pytest.mark.run(order=2)
def test_init(config_reader):
    reader = MunicipalityReader(
        config_reader.get_municipality_config().get('source').get('class'),
        **config_reader.get_municipality_config().get('source').get('params')
    )
    assert isinstance(reader._source_, Base)


@pytest.mark.run(order=2)
def test_read(connection, config_reader):
    assert connection.closed
    reader = MunicipalityReader(
        config_reader.get_municipality_config().get('source').get('class'),
        **config_reader.get_municipality_config().get('source').get('params')
    )
    results = reader.read()
    assert isinstance(results, list)
    assert len(results) == 1
    result = results[0]
    assert isinstance(result, MunicipalityRecord)
    assert result.fosnr == 1234
    assert result.name == 'Test'
    assert result.published
    assert result.geom == 'MULTIPOLYGON (((0 0, 0 1, 1 1, 1 0, 0 0)))'


# TODO: Implement tests for return values, not possible now, cause there is no data in database
