# -*- coding: utf-8 -*-

import pytest
from tests.core.renderer.xml import params
from shapely.geometry import Point


@pytest.mark.parametrize('parameters', params)  # noqa
def test_point(xml_templates, parameters):
    template = xml_templates.get_template('geometry/point.xml')
    point = Point((0, 0))
    content = template.render(**{
        'params': parameters,
        'default_language': 'de',
        'coords': point.coords[0]
    }).decode('utf-8').split('\n')
    expected_content = """
    <geometry:c1>0.0</geometry:c1><geometry:c2>0.0</geometry:c2>""".split('\n')
    expected_lines = []
    for line in expected_content:
        expected_lines.append(line.strip())
    content_lines = []
    for line in content:
        content_lines.append(line.strip())
    assert expected_lines == content_lines
