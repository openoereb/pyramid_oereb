# -*- coding: utf-8 -*-
import pytest
from sqlalchemy.orm.exc import NoResultFound

from pyramid_oereb.lib.sources import Base
from pyramid_oereb.lib.readers.address import AddressReader
from pyramid_oereb.tests.conftest import config_reader


@pytest.mark.run(order=2)
def test_init():
    reader = AddressReader(
        config_reader.get_address_config().get('source').get('class'),
        **config_reader.get_address_config().get('source').get('params')
    )
    assert isinstance(reader._source_, Base)


@pytest.mark.run(order=2)
@pytest.mark.parametrize("param", [
    {'street_name': u'Mühlemattstrasse', 'street_number': '36', 'zip_code': 4410}
])
def test_read(param):
    reader = AddressReader(
        config_reader.get_address_config().get('source').get('class'),
        **config_reader.get_address_config().get('source').get('params')
    )
    with pytest.raises(NoResultFound):
        reader.read(param.get('street_name'), param.get('zip_code'), param.get('street_number'))

# TODO: Implement tests for return values, not possible now, cause there is no data in database
