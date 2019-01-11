# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.config import Config
from pyramid_oereb.lib.sources import Base
from pyramid_oereb.lib.readers.exclusion_of_liability import ExclusionOfLiabilityReader


@pytest.mark.run(order=2)
def test_init():
    reader = ExclusionOfLiabilityReader(
        Config.get_exclusion_of_liability_config().get('source').get('class'),
        **Config.get_exclusion_of_liability_config().get('source').get('params')
    )
    assert isinstance(reader._source_, Base)


@pytest.mark.run(order=2)
def test_read():
    reader = ExclusionOfLiabilityReader(
        Config.get_exclusion_of_liability_config().get('source').get('class'),
        **Config.get_exclusion_of_liability_config().get('source').get('params')
    )
    results = reader.read()
    assert isinstance(results, list)
    assert len(results) == 0

# TODO: Implement tests for return values, not possible now, cause there is no data in database
