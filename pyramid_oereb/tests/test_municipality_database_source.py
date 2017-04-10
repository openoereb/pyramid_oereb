# -*- coding: utf-8 -*-

import pytest
from sqlalchemy.orm.exc import NoResultFound

from pyramid_oereb.lib.adapter import DatabaseAdapter
from pyramid_oereb.lib.sources.municipality import MunicipalityDatabaseSource
from pyramid_oereb.models import PyramidOerebMainMunicipality
from pyramid_oereb.tests.conftest import config_reader


@pytest.mark.run(order=2)
def test_init():
    source = MunicipalityDatabaseSource(**config_reader.get_municipality_config().get('source').get('params'))
    assert isinstance(source._adapter_, DatabaseAdapter)
    assert source._model_ == PyramidOerebMainMunicipality


@pytest.mark.run(order=2)
@pytest.mark.parametrize("param", [
    {'id_bfs': 2770}
])
def test_read(param):
    source = MunicipalityDatabaseSource(**config_reader.get_municipality_config().get('source').get('params'))
    with pytest.raises(NoResultFound):
        source.read(**param)


@pytest.mark.run(order=2)
def test_missing_parameter():
    source = MunicipalityDatabaseSource(**config_reader.get_municipality_config().get('source').get('params'))
    with pytest.raises(AttributeError):
        source.read(**{})
