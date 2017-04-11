# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.adapter import DatabaseAdapter
from pyramid_oereb.lib.sources.legend import LegendDatabaseSource
from pyramid_oereb.models import Plr73LegendEntry
from pyramid_oereb.tests.conftest import db_url


@pytest.mark.run(order=2)
@pytest.mark.parametrize("model", [
    Plr73LegendEntry
])
def test_init(model):
    source = LegendDatabaseSource(db_url, model)
    assert isinstance(source._adapter_, DatabaseAdapter)
    assert source._model_ == model


@pytest.mark.run(order=2)
@pytest.mark.parametrize("model", [
    Plr73LegendEntry
])
def test_read(model):
    source = LegendDatabaseSource(db_url, model)
    source.read('StaoTyp1')
    assert len(source.records) == 0
