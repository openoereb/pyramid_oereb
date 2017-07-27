# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.records.address import AddressRecord
from pyramid_oereb.lib.sources import Base
from pyramid_oereb.lib.readers.address import AddressReader


@pytest.mark.run(order=2)
def test_init(config):
    reader = AddressReader(
        config.get_address_config().get('source').get('class'),
        **config.get_address_config().get('source').get('params')
    )
    assert isinstance(reader._source_, Base)


@pytest.mark.run(order=2)
@pytest.mark.parametrize("param,length", [
    ({'street_name': u'test', 'street_number': '10', 'zip_code': 4410}, 1),
    ({'street_name': u'test', 'street_number': '11', 'zip_code': 4410}, 0)
])
def test_read(param, length, config):
    reader = AddressReader(
        config.get_address_config().get('source').get('class'),
        **config.get_address_config().get('source').get('params')
    )
    results = reader.read(param.get('street_name'), param.get('zip_code'), param.get('street_number'))
    assert len(results) == length
    if length == 1:
        address = results[0]
        assert isinstance(address, AddressRecord)
        assert address.zip_code == 4410
