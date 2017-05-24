# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.sources import Base
from pyramid_oereb.lib.readers.real_estate import RealEstateReader


@pytest.mark.run(order=2)
def test_init(config):
    reader = RealEstateReader(
        config.get_real_estate_config().get('source').get('class'),
        **config.get_real_estate_config().get('source').get('params')
    )
    assert isinstance(reader._source_, Base)


@pytest.mark.run(order=2)
@pytest.mark.parametrize("param", [
    {'nb_ident': 'BL0200002789', 'number': '545'}
])
def test_read_ndident_number(param, config):
    reader = RealEstateReader(
        config.get_real_estate_config().get('source').get('class'),
        **config.get_real_estate_config().get('source').get('params')
    )
    with pytest.raises(LookupError):
        reader.read(nb_ident=param.get('nb_ident'), number=param.get('number'))


@pytest.mark.run(order=2)
@pytest.mark.parametrize("param", [
    {'egrid': 'CH1234'}
])
def test_read_egrid(param, config):
    reader = RealEstateReader(
        config.get_real_estate_config().get('source').get('class'),
        **config.get_real_estate_config().get('source').get('params')
    )
    with pytest.raises(LookupError):
        reader.read(egrid=param.get('egrid'))

# TODO: Implement tests for return values, not possible now, cause there is no data in database
