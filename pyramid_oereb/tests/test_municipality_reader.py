# -*- coding: utf-8 -*-
import pytest
from sqlalchemy.orm.exc import NoResultFound

from pyramid_oereb.lib.sources import Base
from pyramid_oereb.lib.readers.municipality import MunicipalityReader
from pyramid_oereb.tests.conftest import config_reader


@pytest.mark.run(order=2)
def test_init():
    reader = MunicipalityReader(
        config_reader.get_municipality_config().get('source').get('class'),
        **config_reader.get_municipality_config().get('source').get('params')
    )
    assert isinstance(reader._source_, Base)


@pytest.mark.run(order=2)
@pytest.mark.parametrize("param", [
    {'id_bfs': 2770}
])
def test_read(param):
    reader = MunicipalityReader(
        config_reader.get_municipality_config().get('source').get('class'),
        **config_reader.get_municipality_config().get('source').get('params')
    )
    with pytest.raises(NoResultFound):
        reader.read(**param)

# TODO: Implement tests for return values, not possible now, cause there is no data in database
