# -*- coding: utf-8 -*-

import datetime
import math

from shapely.geometry import Polygon, MultiPolygon, LineString, Point, MultiPoint, MultiLineString, \
    GeometryCollection

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


@pytest.mark.parametrize('geom,dim', [
    (Point(0, 0), 0),
    (MultiPoint([Point(0, 0)]), 0),
    (LineString([(0, 0), (1, 1)]), 1),
    (MultiLineString([LineString([(0, 0), (1, 1)])]), 1),
    (Polygon([(0, 0), (1, 1), (1, 0)]), 2),
    (MultiPolygon([Polygon([(0, 0), (1, 1), (1, 0)])]), 2),
    (GeometryCollection([Polygon([(0, 0), (1, 1), (1, 0)])]), 3),
    ('nogeom', -1)
])
def test_geom_dim(geom, dim):
    assert GeometryRecord.geom_dim(geom) == dim


@pytest.mark.parametrize('input_geom,result,extracted', [
    (
        Point(0, 0),
        Point(0, 0),
        Point(0, 0)
    ),
    (
        Point(0, 0),
        GeometryCollection([
            Point(0, 0),
            LineString([(0, 0), (1, 1)]),
            Polygon([(0, 0), (1, 1), (1, 0)])
        ]),
        MultiPoint([Point(0, 0)])
    ),
    (
        Point(0, 0),
        GeometryCollection([MultiPoint([Point(0, 0)])]),
        MultiPoint([Point(0, 0)])
    ),
    (
        LineString([(0, 0), (1, 1)]),
        GeometryCollection([
            Point(0, 0),
            LineString([(0, 0), (1, 1)]),
            Polygon([(0, 0), (1, 1), (1, 0)])
        ]),
        LineString([(0, 0), (1, 1)])
    ),
    (
        Polygon([(0, 0), (1, 1), (1, 0)]),
        GeometryCollection([
            Point(0, 0),
            LineString([(0, 0), (1, 1)]),
            Polygon([(0, 0), (1, 1), (1, 0)])
        ]),
        Polygon([(0, 0), (1, 1), (1, 0)])
    )
])
def test_extract_collection(input_geom, result, extracted):
    law_status_record = LawStatusRecord("runningModifications", {u'de': u'BlaBla'})
    geometry_record = GeometryRecord(
        law_status_record,
        datetime.date(1985, 8, 29),
        input_geom,
        'test'
    )
    assert geometry_record._extract_collection(result) == extracted


@pytest.mark.parametrize(
    "geometry,real_estate_geometry,length_limit,area_limit,length_share,area_share,nr_of_points,test", [
        (
            # Intersection area with area result: Polygon in limit, should pass
            Polygon(((0, 0), (0, 1), (1, 1), (1, 0))),
            MultiPolygon([Polygon(((0, 0), (0, 1), (1, 1), (1, 0)))]),
            1,
            1,
            None,
            1,
            None,
            True
        ), (
            # Intersection area with area result: Polygon not in limit, should be dismissed
            Polygon(((0, 0), (0, 1), (1, 1), (1, 0))),
            MultiPolygon([Polygon(((0, 0), (0, 1), (1, 1), (1, 0)))]),
            1,
            2,
            None,
            None,
            None,
            False
        ), (
            # Intersection area with area result: Point, should be dismissed
            Polygon(((0, 0), (0, 1), (1, 1), (1, 0))),
            MultiPolygon([Polygon(((1, 1), (1, 2), (2, 2), (2, 1)))]),
            1,
            1,
            None,
            None,
            None,
            False
        ), (
            # Intersection area with area result: Line, should be dismissed
            Polygon(((0, 0), (0, 1), (1, 1), (1, 0))),
            MultiPolygon([Polygon(((1, 1), (2, 1), (2, 0), (1, 0)))]),
            1,
            1,
            None,
            None,
            None,
            False
        ), (
            # Intersection area with line result: Line in limit, should pass
            LineString(((0, 0), (1, 1))),
            MultiPolygon([Polygon(((0, 0), (0, 1), (1, 1), (1, 0)))]),
            1,
            1,
            math.sqrt(2),
            None,
            None,
            True
        ), (
            # Intersection area with line result: Line not in limit, should be dismissed
            LineString(((0, 0), (1, 1))),
            MultiPolygon([Polygon(((0, 0), (0, 1), (1, 1), (1, 0)))]),
            2,
            1,
            None,
            None,
            None,
            False
        ), (
            # Intersection area with line result: Line on border of area, should pass
            LineString(((0, 0), (0, 1))),
            MultiPolygon([Polygon(((0, 0), (0, 1), (1, 1), (1, 0)))]),
            1,
            1,
            1,
            None,
            None,
            True
        ), (
            # Intersection area with line result: Point, should be dismissed
            LineString(((1, 1), (2, 2))),
            MultiPolygon([Polygon(((0, 0), (0, 1), (1, 1), (1, 0)))]),
            1,
            1,
            None,
            None,
            None,
            False
        ), (
            # Intersection area with point result: Point, should pass
            Point((0.5, 0.5)),
            MultiPolygon([Polygon(((0, 0), (0, 1), (1, 1), (1, 0)))]),
            1,
            1,
            None,
            None,
            1,
            True
        ), (
            # Intersection area with point result: Point, should be dismissed
            Point((2, 2)),
            MultiPolygon([Polygon(((0, 0), (0, 1), (1, 1), (1, 0)))]),
            1,
            1,
            None,
            None,
            None,
            False
        ), (
            # Intersection area with point result: Point, should pass
            MultiPoint([Point((0.4, 0.4)), Point((0.5, 0.5)), Point((0.6, 0.6))]),
            MultiPolygon([Polygon(((0, 0), (0, 1), (1, 1), (1, 0)))]),
            1,
            1,
            None,
            None,
            3,
            True
        )
    ]
)
def test_calculate(geometry, real_estate_geometry, length_limit, area_limit, length_share, area_share,
                   nr_of_points, test):
    law_status_record = LawStatusRecord("runningModifications", {u'de': u'BlaBla'})
    geometry_record = GeometryRecord(
        law_status_record,
        datetime.date(1985, 8, 29),
        geometry,
        'test'
    )
    real_estate = RealEstateRecord(
        'Liegenschaft',
        'BL',
        'Aesch BL',
        2761,
        1,
        real_estate_geometry
    )
    geometry_record.calculate(real_estate, length_limit, area_limit, 'm', 'm2')
    assert geometry_record._test_passed == test
    assert geometry_record._length_share == length_share
    assert geometry_record._area_share == area_share
    assert geometry_record._nr_of_points == nr_of_points
