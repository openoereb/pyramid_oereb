# -*- coding: utf-8 -*-

import sys
import pytest
import shapely.wkt
import shapely.geometry

from pyramid_oereb.lib.records.image import ImageRecord
from pyramid_oereb.lib.records.municipality import MunicipalityRecord


def test_mandatory_fields():
    with pytest.raises(TypeError):
        MunicipalityRecord()


def test_init():
    logo = ImageRecord('abcde')
    geometry = shapely.wkt.loads('MULTIPOLYGON(((123 456, 456 789, 789 123, 123 456)))')
    record = MunicipalityRecord(
        969,
        u'FantasyMunicipality',
        True,
        logo,
        geom=geometry
    )
    assert isinstance(record.fosnr, int)
    if sys.version_info.major == 2:
        assert isinstance(record.name, unicode)  # noqa
    else:
        assert isinstance(record.name, str)
    assert isinstance(record.published, bool)
    assert isinstance(record.logo, ImageRecord)
    assert isinstance(record.geom, shapely.geometry.multipolygon.MultiPolygon)
