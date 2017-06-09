# -*- coding: utf-8 -*-
import pytest
from shapely.geometry import Polygon
from shapely.wkt import loads

from pyramid_oereb.lib.records.real_estate import RealEstateRecord


def test_mandatory_fields():
    with pytest.raises(TypeError):
        RealEstateRecord()


def test_init():
    record = RealEstateRecord('test_type', 'BL', 'Nusshof', 1, 100,
                              loads('POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))'))
    assert isinstance(record.type, str)
    assert isinstance(record.canton, str)
    assert isinstance(record.municipality, str)
    assert isinstance(record.fosnr, int)
    assert isinstance(record.land_registry_area, int)
    assert isinstance(record.limit, Polygon)
    assert record.metadata_of_geographical_base_data is None
    assert record.number is None
    assert record.identdn is None
    assert record.egrid is None
    assert record.subunit_of_land_register is None
    assert record.areas_ratio == 0.01
