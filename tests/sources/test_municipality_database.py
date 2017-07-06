# -*- coding: utf-8 -*-

import pytest

from pyramid_oereb.lib.adapter import DatabaseAdapter
from pyramid_oereb.lib.sources.municipality import MunicipalityDatabaseSource
from pyramid_oereb.standard.models.main import Municipality


@pytest.mark.run(order=2)
def test_init(config):
    source = MunicipalityDatabaseSource(**config.get_municipality_config().get('source').get('params'))
    assert isinstance(source._adapter_, DatabaseAdapter)
    assert source._model_ == Municipality


def test_read(config):
    source = MunicipalityDatabaseSource(**config.get_municipality_config().get('source').get('params'))
    source.read()
    assert isinstance(source.records, list)
