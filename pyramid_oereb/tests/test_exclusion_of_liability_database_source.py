# -*- coding: utf-8 -*-

import pytest

from pyramid_oereb.lib.adapter import DatabaseAdapter
from pyramid_oereb.lib.sources.exclusion_of_liability import ExclusionOfLiabilityDatabaseSource
from pyramid_oereb.models import PyramidOerebMainExclusionOfLiability
from pyramid_oereb.tests.conftest import config_reader


@pytest.mark.run(order=2)
def test_init():
    source = ExclusionOfLiabilityDatabaseSource(
        **config_reader.get_exclusion_of_liability_config().get('source').get('params')
    )
    assert isinstance(source._adapter_, DatabaseAdapter)
    assert source._model_ == PyramidOerebMainExclusionOfLiability


@pytest.mark.run(order=2)
def test_read():
    source = ExclusionOfLiabilityDatabaseSource(
        **config_reader.get_exclusion_of_liability_config().get('source').get('params')
    )
    source.read()
    assert len(source.records) == 0
