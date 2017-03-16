# -*- coding: utf-8 -*-
import os
import pytest

from pyramid_oereb.lib.adapter import DatabaseAdapter
from pyramid_oereb.lib.sources.plr import PlrDatabaseSource
from pyramid_oereb.models import *
from pyramid_oereb.tests.conftest import adapter

__author__ = 'Clemens Rudert'
__create_date__ = '16.03.17'


@pytest.mark.run(order=2)
@pytest.mark.parametrize("model", [
    Plr73PublicLawRestriction,
    Plr116PublicLawRestriction
])
def test_init(model):
    db_url = os.environ.get('SQLALCHEMY_URL')
    adapter.add_connection(db_url)
    source = PlrDatabaseSource(adapter, model)
    assert isinstance(source._adapter_, DatabaseAdapter)
    assert source._model_ == model


@pytest.mark.run(order=2)
@pytest.mark.parametrize("model", [
    Plr73PublicLawRestriction,
    Plr116PublicLawRestriction
])
def test_read(model):
    db_url = os.environ.get('SQLALCHEMY_URL')
    adapter.add_connection(db_url)
    source = PlrDatabaseSource(adapter, model)
    source.read(db_url)
    assert len(source.records) == 0
