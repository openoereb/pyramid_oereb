# -*- coding: utf-8 -*-

import datetime
from datetime import date, timedelta
import math
import os

from shapely.geometry import Polygon, MultiPolygon, LineString, Point, \
    MultiPoint, MultiLineString, GeometryCollection
import shapely.wkt

import pytest

from pyramid_oereb.core.records.geometry import GeometryRecord
from pyramid_oereb.core.records.law_status import LawStatusRecord
from pyramid_oereb.core.records.real_estate import RealEstateRecord


__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def test_mandatory_fields():
    with pytest.raises(TypeError):
        GeometryRecord()


def test_init():
    record = GeometryRecord("AenderungMitVorwirkung", datetime.date(1985, 8, 29),
                            None, Polygon(), 'test')
    assert isinstance(record.law_status, str)
    assert isinstance(record.published_from, datetime.date)
    assert isinstance(record.geo_metadata, str)
    assert isinstance(record.geom, Polygon)
    assert record.public_law_restriction is None


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
    law_status_record = LawStatusRecord("AenderungMitVorwirkung", {u'de': u'BlaBla'})
    geometry_record = GeometryRecord(
        law_status_record,
        datetime.date(1985, 8, 29),
        None,
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
        ), (
            # Intersection area with polygon result: Polygon, should pass
            # PLR geometry is Interlis valid and OGC invalid
            shapely.wkt.loads(
                open(
                    os.path.join(__location__, "interlis-valid-ogc-invalid-geometry.txt")
                ).read()
            ).buffer(0),  # does not work any longer without repairing the geometry
            Polygon([(2698200, 1208800), (2698400, 1208800), (2698400, 1209000), (2698200, 1209000)]),
            1,
            1,
            None,
            40000,
            None,
            True
        ), (
            # Intersection area with polygon result: Polygon, should be dismissed
            # PLR geometry is Interlis valid and OGC invalid
            shapely.wkt.loads(
                open(
                    os.path.join(__location__, "interlis-valid-ogc-invalid-geometry.txt")
                ).read()
            ).buffer(0),  # does not work any longer without repairing the geometry,
            Polygon([(2696500, 1208800), (2696700, 1208800), (2696700, 1209000), (2696500, 1209000)]),
            1,
            1,
            None,
            None,
            None,
            False
        )
    ]
)
def test_calculate(pyramid_oereb_test_config, geometry, real_estate_geometry,
                   length_limit, area_limit, length_share, area_share, nr_of_points, test, geometry_types):
    law_status_record = LawStatusRecord("AenderungMitVorwirkung", {u'de': u'BlaBla'})
    geometry_record = GeometryRecord(
        law_status_record,
        datetime.date(1985, 8, 29),
        None,
        geometry,
        'test'
    )
    real_estate = RealEstateRecord(
        'Liegenschaft',
        'BL',
        'Aesch BL',
        2761,
        round(real_estate_geometry.area),
        real_estate_geometry
    )
    geometry_record.calculate(real_estate, length_limit, area_limit, 'm', 'm2', geometry_types)
    assert geometry_record._test_passed == test
    assert geometry_record._length_share == length_share
    assert geometry_record._area_share == area_share
    assert geometry_record._nr_of_points == nr_of_points


@pytest.mark.parametrize(
    "geometry,test", [
        (
            # Invalid geometry according to OGC
            shapely.wkt.loads(
                open(
                    os.path.join(__location__, "interlis-valid-ogc-invalid-geometry.txt")
                ).read()
            ),
            False,
        ), (
            # Valid geometry according to OGC
            shapely.wkt.loads(
                open(
                    os.path.join(__location__, "interlis-valid-ogc-valid-geometry.txt")
                ).read()
            ),
            True,
        )
    ]
)
def test_validity(geometry, test):
    assert geometry.is_valid == test


@pytest.mark.parametrize('published_from,published_until,published', [
    (date.today() + timedelta(days=0), date.today() + timedelta(days=2), True),
    (date.today() + timedelta(days=1), date.today() + timedelta(days=2), False),
    (date.today() - timedelta(days=3), date.today() - timedelta(days=2), False),
    (date.today() + timedelta(days=0), None, True),
    (date.today() + timedelta(days=1), None, False)]
)
def test_published(published_from, published_until, published):
    geometry_record = GeometryRecord(
        LawStatusRecord("AenderungMitVorwirkung", {u'de': u'BlaBla'}),
        published_from,
        published_until,
        Polygon([(2698200, 1208800), (2698400, 1208800), (2698400, 1209000), (2698200, 1209000)]),
        'test'
    )
    assert geometry_record.published == published
