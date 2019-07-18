# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.config import Config
from pyramid_oereb.lib.sources import Base
from pyramid_oereb.lib.readers.exclusion_of_liability import ExclusionOfLiabilityReader
from pyramid_oereb.lib.records.exclusion_of_liability import ExclusionOfLiabilityRecord


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
    assert len(results) == 1
    assert isinstance(results[0], ExclusionOfLiabilityRecord)
    assert len(results[0].title) == 4
    assert len(results[0].content) == 4
    assert 'du cadastre des sites' in results[0].title['fr']
    assert 'Kataster der belasteten Standorte' in results[0].content['de']
