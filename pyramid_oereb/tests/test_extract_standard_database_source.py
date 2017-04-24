# -*- coding: utf-8 -*-
from shapely.geometry import MultiPolygon

import pytest
from pyramid.path import DottedNameResolver

from pyramid_oereb.lib.adapter import DatabaseAdapter
from pyramid_oereb.lib.records.real_estate import RealEstateRecord
from pyramid_oereb.lib.records.view_service import ViewServiceRecord
from pyramid_oereb.lib.sources.extract import ExtractStandardDatabaseSource
from pyramid_oereb.tests.conftest import config_reader


@pytest.mark.run(order=2)
def test_init():
    source = ExtractStandardDatabaseSource(**{
        'db_connection': config_reader.get('db_connection'),
        # TODO: Find a way to parametrize the extract by all available plr's
        'name': 'plr119'
    })
    assert isinstance(source._adapter_, DatabaseAdapter)
    assert source._model_ == DottedNameResolver().maybe_resolve(
        'pyramid_oereb.models.{name}Geometry'.format(name=source._name_.capitalize())
    )


@pytest.mark.run(order=2)
@pytest.mark.parametrize("param", [
    RealEstateRecord('test', 'BL', 'Laufen', 2770, 1000, MultiPolygon(), ViewServiceRecord(
        'test_link', 'test_legend')
                     )
])
def test_read(param):
    source = ExtractStandardDatabaseSource(**{
        'db_connection': config_reader.get('db_connection'),
        # TODO: Find a way to parametrize the extract by all available plr's
        'name': 'plr119'
    })
    source.read(param)
    assert len(source.records) == 1


@pytest.mark.run(order=2)
def test_missing_parameter():
    source = ExtractStandardDatabaseSource(**{
        'db_connection': config_reader.get('db_connection'),
        # TODO: Find a way to parametrize the extract by all available plr's
        'name': 'plr119'
    })
    with pytest.raises(TypeError):
        source.read()
