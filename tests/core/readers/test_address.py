# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.core.records.address import AddressRecord
from pyramid_oereb.core.sources import Base
from tests.mockrequest import MockParameter


@pytest.fixture
def address_data(dbsession, transact):
    from pyramid_oereb.contrib.data_sources.standard.models.main import Address
    del transact
    addresses = [
        Address(**{
            'street_name': u'test',
            'street_number': u'10',
            'zip_code': 4410,
            'geom': 'SRID=2056;POINT(1 1)'
        })
    ]
    dbsession.add_all(addresses)
    dbsession.flush()
    yield addresses


@pytest.mark.run(order=2)
def test_init(pyramid_oereb_test_config):
    from pyramid_oereb.core.readers.address import AddressReader

    reader = AddressReader(
        pyramid_oereb_test_config.get_address_config().get('source').get('class'),
        **pyramid_oereb_test_config.get_address_config().get('source').get('params')
    )
    assert isinstance(reader._source_, Base)


@pytest.mark.run(order=2)
@pytest.mark.parametrize("param,length", [
    ({'street_name': u'test', 'street_number': u'10', 'zip_code': 4410}, 1),
    ({'street_name': u'test', 'street_number': u'11', 'zip_code': 4410}, 0)
])
def test_read(pyramid_oereb_test_config, address_data, param, length):
    from pyramid_oereb.core.readers.address import AddressReader

    reader = AddressReader(
        pyramid_oereb_test_config.get_address_config().get('source').get('class'),
        **pyramid_oereb_test_config.get_address_config().get('source').get('params')
    )
    results = reader.read(MockParameter(), param.get('street_name'), param.get('zip_code'),
                          param.get('street_number'))
    assert len(results) == length
    if length == 1:
        address = results[0]
        assert isinstance(address, AddressRecord)
        assert address.zip_code == address_data[0].zip_code
