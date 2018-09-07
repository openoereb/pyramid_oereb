# -*- coding: utf-8 -*-

import datetime
from shapely.geometry import Polygon, MultiPolygon

import pytest

from pyramid_oereb.lib.records.geometry import GeometryRecord
from pyramid_oereb.lib.records.law_status import LawStatusRecord
from pyramid_oereb.lib.records.real_estate import RealEstateRecord


def test_mandatory_fields():
    with pytest.raises(TypeError):
        GeometryRecord()


def test_init():
    record = GeometryRecord("runningModifications", datetime.date(1985, 8, 29), Polygon(), 'test')
    assert isinstance(record.law_status, str)
    assert isinstance(record.published_from, datetime.date)
    assert isinstance(record.geo_metadata, str)
    assert isinstance(record.geom, Polygon)
    assert record.public_law_restriction is None
    assert record.office is None


def test_calculate():
    law_status_record = LawStatusRecord("runningModifications", {u'de': u'BlaBla'})
    geometry_record = GeometryRecord(
        law_status_record,
        datetime.date(1985, 8, 29),
        Polygon(((0, 0), (0, 1), (1, 1), (1, 0))),
        'test'
    )

    real_estate = RealEstateRecord(
        'Liegenschaft',
        'BL',
        'Aesch BL',
        2761,
        100,
        MultiPolygon([Polygon(((0, 0), (0, 1), (1, 1), (1, 0)))])
    )
    geometry_record.calculate(real_estate, 1, 1, 'm', 'm2')
    assert geometry_record._test_passed

    real_estate = RealEstateRecord(
        'Liegenschaft',
        'BL',
        'Aesch BL',
        2761,
        100,
        MultiPolygon([Polygon(((1, 1), (1, 2), (2, 2), (2, 1)))])
    )
    geometry_record.calculate(real_estate, 1, 1, 'm', 'm2')
    assert not geometry_record._test_passed
