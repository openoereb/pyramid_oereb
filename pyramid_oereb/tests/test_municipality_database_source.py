# -*- coding: utf-8 -*-

import pytest

from pyramid_oereb.lib.adapter import DatabaseAdapter
from pyramid_oereb.lib.sources.municipality import MunicipalityDatabaseSource
from pyramid_oereb.models import PyramidOerebMainMunicipality
from pyramid_oereb.tests.conftest import config_reader


@pytest.mark.run(order=2)
def test_init():
    source = MunicipalityDatabaseSource(**config_reader.get_municipality_config().get('source').get('params'))
    assert isinstance(source._adapter_, DatabaseAdapter)
    assert source._model_ == PyramidOerebMainMunicipality


def test_read():
    source = MunicipalityDatabaseSource(**config_reader.get_municipality_config().get('source').get('params'))
    source.read()
    assert isinstance(source.records, list)
