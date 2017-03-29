# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.adapter import DatabaseAdapter
from pyramid_oereb.lib.sources.plr import PlrDatabaseSource
from pyramid_oereb.lib.records.plr import PlrRecord
from pyramid_oereb.models import Plr73PublicLawRestriction, Plr116PublicLawRestriction
from pyramid_oereb.tests.conftest import adapter, db_url


@pytest.mark.run(order=2)
@pytest.mark.parametrize("model", [
    Plr73PublicLawRestriction,
    Plr116PublicLawRestriction
])
def test_init(model):
    adapter.add_connection(db_url)
    source = PlrDatabaseSource(db_url, adapter, model, PlrRecord)
    assert isinstance(source._adapter_, DatabaseAdapter)
    assert source._model_ == model


@pytest.mark.run(order=2)
@pytest.mark.parametrize("model", [
    Plr73PublicLawRestriction,
    Plr116PublicLawRestriction
])
def test_read(model):
    adapter.add_connection(db_url)
    source = PlrDatabaseSource(db_url, adapter, model, PlrRecord)
    source.read('POINT(1 1)')
    assert len(source.records) == 0
