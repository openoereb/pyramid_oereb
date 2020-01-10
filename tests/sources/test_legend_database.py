# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.config import Config
from pyramid_oereb.lib.adapter import DatabaseAdapter
from pyramid_oereb.standard.sources.legend import DatabaseSource
from pyramid_oereb.standard.models.airports_building_lines import LegendEntry
from tests.mockrequest import MockParameter


@pytest.mark.run(order=2)
@pytest.mark.parametrize("model", [
    LegendEntry
])
def test_init(model):
    db_url = Config.get('app_schema').get('db_connection')
    source = DatabaseSource(**{'db_connection': db_url, 'model': model})
    assert isinstance(source._adapter_, DatabaseAdapter)
    assert source._model_ == model


@pytest.mark.run(order=2)
@pytest.mark.parametrize("model", [
    LegendEntry
])
def test_read(model):
    db_url = Config.get('app_schema').get('db_connection')
    source = DatabaseSource(**{'db_connection': db_url, 'model': model})
    source.read(MockParameter(), **{'type_code': 'StaoTyp1'})
    assert len(source.records) == 0
