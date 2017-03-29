# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.lib.records.real_estate import RealEstateRecord


def test_get_fields():
    expected_fields = [
        'type',
        'canton',
        'municipality',
        'fosnr',
        'metadata_of_geographical_base_data',
        'land_registry_area',
        'limit',
        'number',
        'identdn',
        'egrid',
        'subunit_of_land_register'
    ]
    fields = RealEstateRecord.get_fields()
    assert fields == expected_fields


def test_mandatory_fields():
    with pytest.raises(TypeError):
        RealEstateRecord()


def test_init():
    record = RealEstateRecord('test_type', 'BL', 'Nusshof', 1, 'https://www.meta.data', 100,
                              'POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))')
    assert isinstance(record.type, str)
    assert isinstance(record.canton, str)
    assert isinstance(record.municipality, str)
    assert isinstance(record.fosnr, int)
    assert isinstance(record.metadata_of_geographical_base_data, str)
    assert isinstance(record.land_registry_area, int)
    assert isinstance(record.limit, str)
    assert record.number is None
    assert record.identdn is None
    assert record.egrid is None
    assert record.subunit_of_land_register is None
