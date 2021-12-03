# -*- coding: utf-8 -*-
import pytest

from tests.mockrequest import MockParameter


@pytest.mark.run(order=2)
def test_init(pyramid_oereb_test_config):
    from pyramid_oereb.contrib.data_sources.standard.models.main import RealEstate
    from pyramid_oereb.contrib.data_sources.standard.sources.real_estate import DatabaseSource
    from pyramid_oereb.core.adapter import DatabaseAdapter

    print(pyramid_oereb_test_config.get_config())
    source = DatabaseSource(**pyramid_oereb_test_config.get_real_estate_config().get('source').get('params'))
    assert isinstance(source._adapter_, DatabaseAdapter)
    assert source._model_ == RealEstate


@pytest.mark.run(order=2)
@pytest.mark.parametrize("param", [
    {'nb_ident': 'BLTEST', 'number': '1000'},
    {'egrid': 'TEST'},
    {'geometry': 'SRID=2056;POINT(1 1)'}
])
def test_read(pyramid_oereb_test_config, param):
    from pyramid_oereb.contrib.data_sources.standard.sources.real_estate import DatabaseSource
    from pyramid_oereb.core.records.real_estate import RealEstateRecord

    source = DatabaseSource(**pyramid_oereb_test_config.get_real_estate_config().get('source').get('params'))
    source.read(MockParameter(), **param)
    assert len(source.records) == 1
    record = source.records[0]
    assert isinstance(record, RealEstateRecord)
    assert record.fosnr == 1234


@pytest.mark.run(order=2)
def test_missing_parameter(pyramid_oereb_test_config):
    from pyramid_oereb.contrib.data_sources.standard.sources.real_estate import DatabaseSource

    source = DatabaseSource(**pyramid_oereb_test_config.get_real_estate_config().get('source').get('params'))
    with pytest.raises(AttributeError):
        source.read(MockParameter())
