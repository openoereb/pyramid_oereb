# -*- coding: utf-8 -*-
import pytest
from sqlalchemy.orm.exc import NoResultFound

from pyramid_oereb.lib.adapter import DatabaseAdapter
from pyramid_oereb.lib.sources.real_estate import RealEstateDatabaseSource
from pyramid_oereb.models import PyramidOerebMainRealEstate
from pyramid_oereb.tests.conftest import adapter, db_url


@pytest.mark.run(order=2)
def test_init():
    adapter.add_connection(db_url)
    source = RealEstateDatabaseSource(db_url, adapter, PyramidOerebMainRealEstate)
    assert isinstance(source._adapter_, DatabaseAdapter)
    assert source._model_ == PyramidOerebMainRealEstate


@pytest.mark.run(order=2)
@pytest.mark.parametrize("param", [
    {'nb_ident': 'BL0200002789', 'number': '545'},
    {'egrid': 'CH1234'}
])
def test_read(param):
    adapter.add_connection(db_url)
    source = RealEstateDatabaseSource(db_url, adapter, PyramidOerebMainRealEstate)
    with pytest.raises(NoResultFound):
        source.read(**param)


@pytest.mark.run(order=2)
def test_missing_parameter():
    adapter.add_connection(db_url)
    source = RealEstateDatabaseSource(db_url, adapter, PyramidOerebMainRealEstate)
    with pytest.raises(AttributeError):
        source.read(**{})
