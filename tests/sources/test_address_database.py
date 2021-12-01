# -*- coding: utf-8 -*-

import pytest

from pyramid_oereb.core.config import Config
from pyramid_oereb.core.adapter import DatabaseAdapter
from pyramid_oereb.core.records.address import AddressRecord
from pyramid_oereb.contrib.data_sources.standard.sources.address import DatabaseSource
from pyramid_oereb.contrib.data_sources.standard.models import Address
from tests.mockrequest import MockParameter


@pytest.mark.run(order=2)
def test_init():
    source = DatabaseSource(**Config.get_address_config().get('source').get('params'))
    assert isinstance(source._adapter_, DatabaseAdapter)
    assert source._model_ == Address


@pytest.mark.run(order=2)
@pytest.mark.parametrize("param,length", [
    ({'street_name': u'test', 'street_number': '10', 'zip_code': 4410}, 1),
    ({'street_name': u'test', 'street_number': '11', 'zip_code': 4410}, 0)
])
def test_read(param, length):
    source = DatabaseSource(**Config.get_address_config().get('source').get('params'))
    source.read(MockParameter(), param.get('street_name'), param.get('zip_code'), param.get('street_number'))
    assert len(source.records) == length
    if length == 1:
        address = source.records[0]
        assert isinstance(address, AddressRecord)
        assert address.zip_code == 4410


@pytest.mark.run(order=2)
def test_missing_parameter():
    source = DatabaseSource(**Config.get_address_config().get('source').get('params'))
    with pytest.raises(TypeError):
        source.read()
