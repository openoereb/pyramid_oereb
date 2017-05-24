# -*- coding: utf-8 -*-

import pytest
from sqlalchemy.orm.exc import NoResultFound

from pyramid_oereb.lib.adapter import DatabaseAdapter
from pyramid_oereb.lib.sources.address import AddressDatabaseSource
from pyramid_oereb.standard.models.main import Address


@pytest.mark.run(order=2)
def test_init(config):
    source = AddressDatabaseSource(**config.get_address_config().get('source').get('params'))
    assert isinstance(source._adapter_, DatabaseAdapter)
    assert source._model_ == Address


@pytest.mark.run(order=2)
@pytest.mark.parametrize("param", [
    {'street_name': u'Mühlemattstrasse', 'street_number': '36', 'zip_code': 4410}
])
def test_read(param, config):
    source = AddressDatabaseSource(**config.get_address_config().get('source').get('params'))
    with pytest.raises(NoResultFound):
        source.read(param.get('street_name'), param.get('zip_code'), param.get('street_number'))


@pytest.mark.run(order=2)
def test_missing_parameter(config):
    source = AddressDatabaseSource(**config.get_address_config().get('source').get('params'))
    with pytest.raises(TypeError):
        source.read()
