# -*- coding: utf-8 -*-

import datetime
from shapely.geometry import Polygon

import pytest

from pyramid_oereb.lib.records.geometry import GeometryRecord


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
