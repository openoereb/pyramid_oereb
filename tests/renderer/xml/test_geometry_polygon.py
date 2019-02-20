# -*- coding: utf-8 -*-

import pytest
from tests import params
from tests.renderer.xml import xml_templates
from shapely.geometry import Polygon

template = xml_templates().get_template('geometry/polygon.xml')


@pytest.mark.parametrize('parameters', params)  # noqa
def test_polygon(parameters):
    polygon = Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)))

    def get_gml_id():
        return 'gml1'

    content = template.render(**{
        'params': parameters,
        'default_language': 'de',
        'polygon': polygon,
        'get_gml_id': get_gml_id
    }).decode('utf-8').split('\n')
    expected_content = """
    <gml:Polygon gml:id="gml1">
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
