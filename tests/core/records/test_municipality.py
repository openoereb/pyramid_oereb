# -*- coding: utf-8 -*-

import pytest
import shapely.wkt
import shapely.geometry

from pyramid_oereb.core.records.municipality import MunicipalityRecord


def test_mandatory_fields():
    with pytest.raises(TypeError):
        MunicipalityRecord()


def test_init():
    geometry = shapely.wkt.loads('MULTIPOLYGON(((123 456, 456 789, 789 123, 123 456)))')
    record = MunicipalityRecord(
        969,
        u'FantasyMunicipality',
        True,
        geom=geometry
    )
    assert isinstance(record.fosnr, int)
    assert isinstance(record.name, str)
    assert isinstance(record.published, bool)
    assert isinstance(record.geom, shapely.geometry.multipolygon.MultiPolygon)
