# -*- coding: utf-8 -*-

import pytest

from pyramid_oereb.lib.adapter import DatabaseAdapter
from pyramid_oereb.lib.records.address import AddressRecord
from pyramid_oereb.standard.sources.address import DatabaseSource
from pyramid_oereb.standard.models.main import Address


@pytest.mark.run(order=2)
def test_init(config):
    source = DatabaseSource(**config.get_address_config().get('source').get('params'))
    assert isinstance(source._adapter_, DatabaseAdapter)
    assert source._model_ == Address


@pytest.mark.run(order=2)
@pytest.mark.parametrize("param,length", [
    ({'street_name': u'test', 'street_number': '10', 'zip_code': 4410}, 1),
    ({'street_name': u'test', 'street_number': '11', 'zip_code': 4410}, 0)
])
def test_read(param, length, config):
    source = DatabaseSource(**config.get_address_config().get('source').get('params'))
    source.read(param.get('street_name'), param.get('zip_code'), param.get('street_number'))
    assert len(source.records) == length
    if length == 1:
        address = source.records[0]
        assert isinstance(address, AddressRecord)
        assert address.zip_code == 4410


@pytest.mark.run(order=2)
def test_missing_parameter(config):
    source = DatabaseSource(**config.get_address_config().get('source').get('params'))
    with pytest.raises(TypeError):
        source.read()
