# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.sources import Base
from pyramid_oereb.lib.readers.exclusion_of_liability import ExclusionOfLiabilityReader
from pyramid_oereb.tests.conftest import config_reader


@pytest.mark.run(order=2)
def test_init():
    reader = ExclusionOfLiabilityReader(
        config_reader.get_exclusion_of_liability_config().get('source').get('class'),
        **config_reader.get_exclusion_of_liability_config().get('source').get('params')
    )
    assert isinstance(reader._source_, Base)


@pytest.mark.run(order=2)
def test_read():
    reader = ExclusionOfLiabilityReader(
        config_reader.get_exclusion_of_liability_config().get('source').get('class'),
        **config_reader.get_exclusion_of_liability_config().get('source').get('params')
    )
    results = reader.read()
    assert isinstance(results, list)
    assert len(results) == 0

# TODO: Implement tests for return values, not possible now, cause there is no data in database
