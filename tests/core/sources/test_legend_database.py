# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.core.adapter import DatabaseAdapter
from tests.mockrequest import MockParameter


@pytest.mark.run(order=2)
@pytest.mark.parametrize("model", [
    "legend_entry"
])
def test_init(pyramid_oereb_test_config, model):
    
    from pyramid_oereb.contrib.data_sources.standard.sources.legend import DatabaseSource

    db_url = pyramid_oereb_test_config.get('app_schema').get('db_connection')
    source = DatabaseSource(**{'db_connection': db_url, 'model': model})
    assert isinstance(source._adapter_, DatabaseAdapter)
    assert source._model_ == model
    print(model)
    assert False


@pytest.mark.run(order=2)
@pytest.mark.parametrize("model", [
    "legend_entry"
])
def test_read(pyramid_oereb_test_config, model):
    from pyramid_oereb.contrib.data_sources.standard.sources.legend import DatabaseSource

    db_url = pyramid_oereb_test_config.get('app_schema').get('db_connection')
    source = DatabaseSource(**{'db_connection': db_url, 'model': model})
    source.read(MockParameter(), **{'type_code': 'StaoTyp1'})
    assert len(source.records) == 0
