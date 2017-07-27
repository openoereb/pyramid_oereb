# -*- coding: utf-8 -*-

import pytest

from pyramid_oereb.lib.adapter import DatabaseAdapter
from pyramid_oereb.standard.sources.exclusion_of_liability import DatabaseSource
from pyramid_oereb.standard.models.main import ExclusionOfLiability


@pytest.mark.run(order=2)
def test_init(config):
    source = DatabaseSource(
        **config.get_exclusion_of_liability_config().get('source').get('params')
    )
    assert isinstance(source._adapter_, DatabaseAdapter)
    assert source._model_ == ExclusionOfLiability


@pytest.mark.run(order=2)
def test_read(config):
    source = DatabaseSource(
        **config.get_exclusion_of_liability_config().get('source').get('params')
    )
    source.read()
    assert len(source.records) == 0
