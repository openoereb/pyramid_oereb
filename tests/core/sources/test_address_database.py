# -*- coding: utf-8 -*-

import pytest

from pyramid_oereb.core.adapter import DatabaseAdapter

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
    from pyramid_oereb.contrib.data_sources.standard.sources.address import DatabaseSource
    from pyramid_oereb.contrib.data_sources.standard.models.main import Address

    source = DatabaseSource(**pyramid_oereb_test_config.get_address_config().get('source').get('params'))
    assert isinstance(source._adapter_, DatabaseAdapter)
    assert source._model_ == Address


@pytest.mark.run(order=2)
@pytest.mark.parametrize("param,length", [
    ({'street_name': u'test', 'street_number': '10', 'zip_code': 4410}, 1),
    ({'street_name': u'test', 'street_number': '11', 'zip_code': 4410}, 0)
])
def test_read(pyramid_oereb_test_config, address_data, param, length):
    from pyramid_oereb.contrib.data_sources.standard.sources.address import DatabaseSource
    from pyramid_oereb.core.records.address import AddressRecord

    source = DatabaseSource(**pyramid_oereb_test_config.get_address_config().get('source').get('params'))
    source.read(MockParameter(), param.get('street_name'), param.get('zip_code'), param.get('street_number'))
    assert len(source.records) == length
    if length == 1:
        address = source.records[0]
        assert isinstance(address, AddressRecord)
        assert address.zip_code == address_data[0].zip_code


@pytest.mark.run(order=2)
def test_missing_parameter(pyramid_oereb_test_config):
    from pyramid_oereb.contrib.data_sources.standard.sources.address import DatabaseSource

    source = DatabaseSource(**pyramid_oereb_test_config.get_address_config().get('source').get('params'))
    with pytest.raises(TypeError):
        source.read()
