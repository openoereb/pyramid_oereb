# -*- coding: utf-8 -*-

from shapely.geometry import LineString, Point, Polygon
from tests.conftest import params
import pytest


@pytest.mark.parametrize('parameters', params)
def test_line(parameters, xml_templates):
    line = LineString(((0, 0), (1, 1)))
    template = xml_templates.get_template('geometry/line.xml')
    content = template.render(**{
        'params': parameters,
        'default_language': 'de',
        'line': line
    }).decode('utf-8').split('\n')
    expected_content = """
    <gml:LineString>
        <gml:pos>0.0 0.0</gml:pos>
        <gml:pos>1.0 1.0</gml:pos>
    </gml:LineString>""".split('\n')
    expected_lines = []
    for line in expected_content:
        expected_lines.append(line.strip())
    content_lines = []
    for line in content:
        content_lines.append(line.strip())
    assert expected_lines == content_lines


@pytest.mark.parametrize('parameters', params)
def test_point(parameters, xml_templates):
    point = Point((0, 0))
    template = xml_templates.get_template('geometry/point.xml')
    content = template.render(**{
        'params': parameters,
        'default_language': 'de',
        'point': point
    }).decode('utf-8').split('\n')
    expected_content = """
    <gml:Point>
        <gml:pos>0.0 0.0</gml:pos>
    </gml:Point>""".split('\n')
    expected_lines = []
    for line in expected_content:
        expected_lines.append(line.strip())
    content_lines = []
    for line in content:
        content_lines.append(line.strip())
    assert expected_lines == content_lines


@pytest.mark.parametrize('parameters', params)
def test_polygon(parameters, xml_templates):
    polygon = Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)))
    template = xml_templates.get_template('geometry/polygon.xml')
    content = template.render(**{
        'params': parameters,
        'default_language': 'de',
        'polygon': polygon
    }).decode('utf-8').split('\n')
    expected_content = """
    <gml:Polygon>
        <gml:exterior>
            <gml:LinearRing>
                <gml:pos>0.0 0.0</gml:pos>
                <gml:pos>0.0 1.0</gml:pos>
                <gml:pos>1.0 1.0</gml:pos>
                <gml:pos>1.0 0.0</gml:pos>
                <gml:pos>0.0 0.0</gml:pos>
            </gml:LinearRing>
        </gml:exterior>
        <gml:interior>
            <gml:LinearRing>
                <gml:pos>0.0 0.0</gml:pos>
                <gml:pos>0.0 1.0</gml:pos>
                <gml:pos>1.0 1.0</gml:pos>
                <gml:pos>1.0 0.0</gml:pos>
                <gml:pos>0.0 0.0</gml:pos>
            </gml:LinearRing>
        </gml:interior>
    </gml:Polygon>""".split('\n')
    expected_lines = []
    for line in expected_content:
        expected_lines.append(line.strip())
    content_lines = []
    for line in content:
        content_lines.append(line.strip())
    assert expected_lines == content_lines
