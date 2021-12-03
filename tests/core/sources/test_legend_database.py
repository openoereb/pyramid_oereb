# -*- coding: utf-8 -*-
import pytest

import tests
from pyramid_oereb.core.config import Config
from pyramid_oereb.core.adapter import DatabaseAdapter
from pyramid_oereb.contrib.data_sources.standard.sources.legend import DatabaseSource
from tests.mockrequest import MockParameter
from pyramid_oereb.contrib.data_sources.standard.sources.plr import StandardThemeConfigParser

Config._config = None
Config.init(tests.pyramid_oereb_test_yml, 'pyramid_oereb')
theme_config = Config.get_theme_config_by_code('ch.Sicherheitszonenplan')
config_parser = StandardThemeConfigParser(**theme_config)
models = config_parser.get_models()
LegendEntry = models.LegendEntry


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
