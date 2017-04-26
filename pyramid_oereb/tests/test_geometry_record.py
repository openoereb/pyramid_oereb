# -*- coding: utf-8 -*-

import datetime
from shapely.geometry import MultiPolygon

import pytest
from shapely.geometry import Point

from pyramid_oereb.lib.records.geometry import GeometryRecord
from pyramid_oereb.lib.records.office import OfficeRecord


def test_get_fields():
    expected_fields = [
        'legal_state',
        'published_from',
        'geo_metadata',
        'geom',
        'public_law_restriction',
        'office'
    ]
    fields = GeometryRecord.get_fields()
    assert fields == expected_fields


def test_mandatory_fields():
    with pytest.raises(TypeError):
        GeometryRecord()


def test_init():
    record = GeometryRecord("runningModifications", datetime.date(1985, 8, 29), MultiPolygon(), 'test')
    assert isinstance(record.legal_state, str)
    assert isinstance(record.published_from, datetime.date)
    assert isinstance(record.geo_metadata, str)
    assert isinstance(record.geom, MultiPolygon)
    assert record.public_law_restriction is None
    assert record.office is None


def test_to_extract():
    office = OfficeRecord('Office')
    point = Point((0, 0))
    record = GeometryRecord('runningModifications', datetime.date(1985, 8, 29), point, 'test', office=office)
    assert record.to_extract() == {
        'legal_state': 'runningModifications',
        'geo_metadata': 'test',
        'geom': point.wkt,
        'office': {
            'name': 'Office'
        }
    }
