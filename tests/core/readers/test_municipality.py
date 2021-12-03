# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.core.records.municipality import MunicipalityRecord
from pyramid_oereb.core.sources import Base
from pyramid_oereb.core.readers.municipality import MunicipalityReader
from tests.mockrequest import MockParameter


@pytest.mark.run(order=2)
def test_init(pyramid_oereb_test_config):
    reader = MunicipalityReader(
        pyramid_oereb_test_config.get_municipality_config().get('source').get('class'),
        **pyramid_oereb_test_config.get_municipality_config().get('source').get('params')
    )
    assert isinstance(reader._source_, Base)


@pytest.mark.run(order=2)
def test_read(pyramid_oereb_test_config):
    reader = MunicipalityReader(
        pyramid_oereb_test_config.get_municipality_config().get('source').get('class'),
        **pyramid_oereb_test_config.get_municipality_config().get('source').get('params')
    )
    results = reader.read(MockParameter())
    assert isinstance(results, list)
    assert len(results) == 1
    result = results[0]
    assert isinstance(result, MunicipalityRecord)
    assert result.fosnr == 1234
    assert result.name == 'Test'
    assert result.published
    assert result.geom == 'MULTIPOLYGON (((0 0, 0 10, 10 10, 10 0, 0 0)))'


# TODO: Implement tests for return values, not possible now, cause there is no data in database
