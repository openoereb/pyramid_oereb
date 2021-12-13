# -*- coding: utf-8 -*-

import pytest
from tests.core.renderer.xml import params
from shapely.geometry import Polygon


@pytest.mark.parametrize('parameters', params)  # noqa
def test_polygon(xml_templates, parameters):
    template = xml_templates.get_template('geometry/polygon.xml')
    polygon = Polygon(
        ((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)),
        [((0.25, 0.25), (0.25, 0.75), (0.75, 0.75), (0.75, 0.25), (0.25, 0.25))]
    )

    def get_gml_id():
        return 'gml1'

    content = template.render(**{
        'params': parameters,
        'default_language': 'de',
        'polygon': polygon,
        'get_gml_id': get_gml_id
    }).decode('utf-8').split('\n')
    expected_content = """
    <geometry:exterior>
      <geometry:polyline>


        <geometry:coord>

        <geometry:c1>0.0</geometry:c1><geometry:c2>0.0</geometry:c2>
        </geometry:coord>
        <geometry:coord>

        <geometry:c1>0.0</geometry:c1><geometry:c2>1.0</geometry:c2>
        </geometry:coord>
        <geometry:coord>

        <geometry:c1>1.0</geometry:c1><geometry:c2>1.0</geometry:c2>
        </geometry:coord>
        <geometry:coord>

        <geometry:c1>1.0</geometry:c1><geometry:c2>0.0</geometry:c2>
        </geometry:coord>
        <geometry:coord>

        <geometry:c1>0.0</geometry:c1><geometry:c2>0.0</geometry:c2>
        </geometry:coord>

      </geometry:polyline>
    </geometry:exterior>
    <geometry:interior>
      <geometry:polyline>


        <geometry:coord>

        <geometry:c1>0.25</geometry:c1><geometry:c2>0.25</geometry:c2>
        </geometry:coord>
        <geometry:coord>

        <geometry:c1>0.25</geometry:c1><geometry:c2>0.75</geometry:c2>
        </geometry:coord>
        <geometry:coord>

        <geometry:c1>0.75</geometry:c1><geometry:c2>0.75</geometry:c2>
        </geometry:coord>
        <geometry:coord>

        <geometry:c1>0.75</geometry:c1><geometry:c2>0.25</geometry:c2>
        </geometry:coord>
        <geometry:coord>

        <geometry:c1>0.25</geometry:c1><geometry:c2>0.25</geometry:c2>
        </geometry:coord>

        </geometry:polyline>
        </geometry:interior>
    """.split('\n')
    expected_lines = []
    for line in expected_content:
        expected_lines.append(line.strip())
    content_lines = []
    for line in content:
        content_lines.append(line.strip())
    assert expected_lines == content_lines
