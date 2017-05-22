# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.adapter import DatabaseAdapter
from pyramid_oereb.lib.sources.real_estate import RealEstateDatabaseSource
from pyramid_oereb.standard.models.main import RealEstate


@pytest.mark.run(order=2)
def test_init(config_reader):
    source = RealEstateDatabaseSource(**config_reader.get_real_estate_config().get('source').get('params'))
    assert isinstance(source._adapter_, DatabaseAdapter)
    assert source._model_ == RealEstate


@pytest.mark.run(order=2)
@pytest.mark.parametrize("param", [
    {'nb_ident': 'BL0200002789', 'number': '545'}
])
def test_read_ndident_number(param, config_reader):
    source = RealEstateDatabaseSource(**config_reader.get_real_estate_config().get('source').get('params'))
    with pytest.raises(LookupError):
        source.read(nb_ident=param.get('nb_ident'), number=param.get('number'))


@pytest.mark.run(order=2)
@pytest.mark.parametrize("param", [
    {'egrid': 'CH1234'}
])
def test_read_egrid(param, config_reader):
    source = RealEstateDatabaseSource(**config_reader.get_real_estate_config().get('source').get('params'))
    with pytest.raises(LookupError):
        source.read(egrid=param.get('egrid'))


@pytest.mark.run(order=2)
def test_missing_parameter(config_reader):
    source = RealEstateDatabaseSource(**config_reader.get_real_estate_config().get('source').get('params'))
    with pytest.raises(AttributeError):
        source.read()
