# -*- coding: utf-8 -*-

import pytest
from tests.core.renderer.xml import params
from shapely.geometry import LineString


@pytest.mark.parametrize('parameters', params)  # noqa
def test_line(template, parameters):
    line = LineString(((0, 0), (1, 1)))

    def get_gml_id():
        return 'gml1'

    content = template.render(**{
        'params': parameters,
        'default_language': 'de',
        'line': line,
        'get_gml_id': get_gml_id
    }).decode('utf-8').split('\n')
    expected_content = """

    <gml:LineString gml:id="gml1">
        <gml:posList>
            0.0 0.0 1.0 1.0
        </gml:posList>
    </gml:LineString>
    """.split('\n')
    expected_lines = []
    for line in expected_content:
        expected_lines.append(line.strip())
    content_lines = []
    for line in content:
        content_lines.append(line.strip())
    assert expected_lines == content_lines
