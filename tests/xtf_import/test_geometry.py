# -*- coding: utf-8 -*-
import pytest
from geoalchemy2.shape import to_shape
from lxml.etree import XML
from pyreproj import Reprojector
from shapely.geometry import Point, LineString, Polygon, MultiPoint, GeometryCollection, MultiLineString, \
    MultiPolygon

from pyramid_oereb.standard.xtf_import.geometry import Geometry


def test_geometry_init():
    geometry = Geometry('foo', 'bar', 'baz', 2056)
    assert geometry._session == 'foo'
    assert geometry._model == 'bar'
    assert geometry._geometry_type == 'baz'
    assert isinstance(geometry._reprojector, Reprojector)


def test_parse_point():
    point = XML("""
    <Punkt>
        <Coord>
            <C1>0</C1>
            <C2>1</C2>
        </Coord>
    </Punkt>
    """)
    geometry = Geometry('foo', 'bar', 'baz', 2056)
    p = geometry._parse_point(point, 2056)
    assert isinstance(p, Point)
    assert p.x == 0.0
    assert p.y == 1.0


def test_parse_line():
    geometry = Geometry('foo', 'bar', 'baz', 2056)
    line = geometry._parse_line(
        XML("""
        <Linie>
            <Polyline>
                <COORD>
                    <C1>0</C1>
                    <C2>0</C2>
                </COORD>
                <COORD>
                    <C1>1</C1>
                    <C2>1</C2>
                </COORD>
            </Polyline>
        </Linie>
        """),
        2056
    )
    assert isinstance(line, LineString)
    assert list(line.coords) == [(0, 0), (1, 1)]


def test_parse_area():
    geometry = Geometry('foo', 'bar', 'baz', 2056)
    area = geometry._parse_area(
        XML("""
        <Flaeche>
            <Surface>
                <Boundary>
                    <Polyline>
                        <COORD>
                            <C1>0</C1>
                            <C2>0</C2>
                        </COORD>
                        <COORD>
                            <C1>1</C1>
                            <C2>1</C2>
                        </COORD>
                        <COORD>
                            <C1>1</C1>
                            <C2>0</C2>
                        </COORD>
                    </Polyline>
                </Boundary>
            </Surface>
        </Flaeche>
        """),
        2056
    )
    assert isinstance(area, Polygon)
    assert list(area.exterior.coords) == [(0, 0), (1, 1), (1, 0), (0, 0)]


@pytest.mark.parametrize('element,geometry_type,instance_type', [
    (
        XML("""
        <Geometrie>
            <Punkt_LV95>
                <COORD>
                    <C1>0</C1>
                    <C2>0</C2>
                </COORD>
            </Punkt_LV95>
        </Geometrie>
        """),
        'multipoint',
        MultiPoint
    ),
    (
        XML("""
        <Geometrie>
            <Punkt_LV95>
                <COORD>
                    <C1>0</C1>
                    <C2>0</C2>
                </COORD>
            </Punkt_LV95>
        </Geometrie>
        """),
        'geometrycollection',
        GeometryCollection
    ),
    (
        XML("""
        <Geometrie>
            <Linie_LV95>
                <Polyline>
                    <COORD>
                        <C1>0</C1>
                        <C2>0</C2>
                    </COORD>
                    <COORD>
                        <C1>1</C1>
                        <C2>1</C2>
                    </COORD>
                </Polyline>
            </Linie_LV95>
        </Geometrie>
        """),
        'multilinestring',
        MultiLineString
    ),
    (
        XML("""
        <Geometrie>
            <Flaeche_LV95>
                <Surface>
                    <Boundary>
                        <Polyline>
                            <COORD>
                                <C1>0</C1>
                                <C2>0</C2>
                            </COORD>
                            <COORD>
                                <C1>1</C1>
                                <C2>1</C2>
                            </COORD>
                            <COORD>
                                <C1>1</C1>
                                <C2>0</C2>
                            </COORD>
                        </Polyline>
                    </Boundary>
                </Surface>
            </Flaeche_LV95>
        </Geometrie>
        """),
        'multipolygon',
        MultiPolygon
    ),
    (
        XML("""
        <Geometrie>
            <Punkt_LV03>
                <COORD>
                    <C1>0</C1>
                    <C2>0</C2>
                </COORD>
            </Punkt_LV03>
        </Geometrie>
        """),
        'multipoint',
        MultiPoint
    ),
    (
        XML("""
        <Geometrie>
            <Punkt_LV03>
                <COORD>
                    <C1>0</C1>
                    <C2>0</C2>
                </COORD>
            </Punkt_LV03>
        </Geometrie>
        """),
        'geometrycollection',
        GeometryCollection
    ),
    (
        XML("""
        <Geometrie>
            <Linie_LV03>
                <Polyline>
                    <COORD>
                        <C1>0</C1>
                        <C2>0</C2>
                    </COORD>
                    <COORD>
                        <C1>1</C1>
                        <C2>1</C2>
                    </COORD>
                </Polyline>
            </Linie_LV03>
        </Geometrie>
        """),
        'multilinestring',
        MultiLineString
    ),
    (
        XML("""
        <Geometrie>
            <Flaeche_LV95>
                <Surface>
                    <Boundary>
                        <Polyline>
                            <COORD>
                                <C1>0</C1>
                                <C2>0</C2>
                            </COORD>
                            <COORD>
                                <C1>1</C1>
                                <C2>1</C2>
                            </COORD>
                            <COORD>
                                <C1>1</C1>
                                <C2>0</C2>
                            </COORD>
                        </Polyline>
                    </Boundary>
                </Surface>
            </Flaeche_LV95>
        </Geometrie>
        """),
        'multipolygon',
        MultiPolygon
    )
])
def test_parse_geom(element, geometry_type, instance_type):
    geometry = Geometry('foo', 'bar', geometry_type, 2056)
    geom = geometry._parse_geom(element)
    assert isinstance(to_shape(geom), instance_type)


def test_parse_coord():
    geometry = Geometry('foo', 'bar', 'baz', 2056)
    coord = XML("""
    <Coord>
        <C1>0</C1>
        <C2>1</C2>
    </Coord>
    """)
    assert geometry._parse_coord(coord, 2056) == (0.0, 1.0)
    assert geometry._parse_coord(coord, 21781) == geometry._reprojector.transform(
        (0.0, 1.0),
        from_srs=21781,
        to_srs=2056
    )


def test_parse_arc():
    geometry = Geometry('foo', 'bar', 'MULTILINESTRING', 2056, arc_max_diff=0.1)
    coords = [
        (0, 0)
    ]
    element = XML("""
    <ARC>
      <C1>2</C1>
      <C2>0</C2>
      <A1>1</A1>
      <A2>1</A2>
    </ARC>
    """)
    coords.extend(geometry._parse_arc(element, coords[-1], 2056))
    assert coords == [
        (0.0, 0.0),
        (0.293, 0.707),
        (1.0, 1.0),
        (1.707, 0.707),
        (2.0, 0.0)
    ]
