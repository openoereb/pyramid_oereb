# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.config import Config
from pyramid_oereb.lib.adapter import DatabaseAdapter
from pyramid_oereb.lib.records.real_estate import RealEstateRecord
from pyramid_oereb.standard.sources.real_estate import DatabaseSource
from pyramid_oereb.standard.models.main import RealEstate
from tests.mockrequest import MockParameter


@pytest.mark.run(order=2)
def test_init():
    source = DatabaseSource(**Config.get_real_estate_config().get('source').get('params'))
    assert isinstance(source._adapter_, DatabaseAdapter)
    assert source._model_ == RealEstate


@pytest.mark.run(order=2)
@pytest.mark.parametrize("param", [
    {'nb_ident': 'BLTEST', 'number': '1000'},
    {'egrid': 'TEST'},
    {'geometry': 'SRID=2056;POINT(1 1)'}
])
def test_read(param):
    source = DatabaseSource(**Config.get_real_estate_config().get('source').get('params'))
    source.read(MockParameter(), **param)
    assert len(source.records) == 1
    record = source.records[0]
    assert isinstance(record, RealEstateRecord)
    assert record.fosnr == 1234


@pytest.mark.run(order=2)
def test_missing_parameter():
    source = DatabaseSource(**Config.get_real_estate_config().get('source').get('params'))
    with pytest.raises(AttributeError):
        source.read(MockParameter())
