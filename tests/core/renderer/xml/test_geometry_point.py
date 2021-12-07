# -*- coding: utf-8 -*-

import pytest
from tests.core.renderer.xml import params
from shapely.geometry import Point


@pytest.mark.parametrize('parameters', params)  # noqa
def test_point(template, parameters):
    point = Point((0, 0))
    content = template.render(**{
        'params': parameters,
        'default_language': 'de',
        'point': point
    }).decode('utf-8').split('\n')
    expected_content = """
    <gml:pos>0.0 0.0</gml:pos>""".split('\n')
    expected_lines = []
    for line in expected_content:
        expected_lines.append(line.strip())
    content_lines = []
    for line in content:
        content_lines.append(line.strip())
    assert expected_lines == content_lines
