# -*- coding: utf-8 -*-
import pytest
import shapely.wkt
import shapely.geometry
from pyramid_oereb.lib.records.municipality import MunicipalityRecord


def test_get_fields():
    expected_fields = [
            'fosnr',
            'name',
            'published',
            'geom'
        ]
    fields = MunicipalityRecord.get_fields()
    assert fields == expected_fields


def test_mandatory_fields():
    with pytest.raises(TypeError):
        MunicipalityRecord()


def test_init():
    record = MunicipalityRecord(
        969,
        u'FantasyMunicipality',
        True,
        'MULTIPOLYGON(((123 456, 456 789, 789 123, 123 456)))'
    )
    assert isinstance(record.fosnr, int)
    assert isinstance(record.name, unicode)
    assert isinstance(record.published, bool)
    assert isinstance(shapely.wkt.loads(record.geom), shapely.geometry.multipolygon.MultiPolygon)
