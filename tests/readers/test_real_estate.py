# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.core.config import Config
from pyramid_oereb.core.records.real_estate import RealEstateRecord
from pyramid_oereb.core.sources import Base
from pyramid_oereb.core.readers.real_estate import RealEstateReader
from tests.mockrequest import MockParameter


@pytest.mark.run(order=2)
def test_init():
    reader = RealEstateReader(
        Config.get_real_estate_config().get('source').get('class'),
        **Config.get_real_estate_config().get('source').get('params')
    )
    assert isinstance(reader._source_, Base)


@pytest.mark.run(order=2)
@pytest.mark.parametrize("param", [
    {'nb_ident': 'BLTEST', 'number': '1000'},
    {'egrid': 'TEST'},
    {'geometry': 'SRID=2056;POINT(1 1)'}
])
def test_read(param):
    reader = RealEstateReader(
        Config.get_real_estate_config().get('source').get('class'),
        **Config.get_real_estate_config().get('source').get('params')
    )
    records = reader.read(MockParameter(), **param)
    assert len(records) == 1
    record = records[0]
    assert isinstance(record, RealEstateRecord)
    assert record.fosnr == 1234
