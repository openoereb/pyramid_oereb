# -*- coding: utf-8 -*-

import pytest

from pyramid_oereb.core.renderer.extract.xml_ import Renderer
from pyramid_oereb.core.records.view_service import ViewServiceRecord


@pytest.fixture
def view_template(xml_templates):
    return xml_templates.get_template('view_service.xml')


def test_reference_wms(DummyRenderInfo, view_template, pyramid_oereb_test_config):
    renderer = Renderer(DummyRenderInfo())
    renderer._language = 'de'
    map = ViewServiceRecord(
        {'de': 'http://example.com?SERVICE=WMS&REQUEST=GetMap&FORMAT=image/png&SRS=epsg:2056'},
        1, 1.0, 'de', 2056, None, None
    )
    content = view_template.render(**{
        'map': map,
        'multilingual': renderer.get_multilingual_text
    }).decode('utf-8').split('\n')

    assert content[5].strip() == """
    <data:Language>de</data:Language>
    """.replace(" ", "").replace('\n', '')
    assert content[6].strip() == """
    <data:Text>
    http://example.com?SERVICE=WMS&amp;REQUEST=GetMap&amp;FORMAT=image/png&amp;SRS=epsg:2056
    </data:Text>
    """.replace(" ", "").replace('\n', '')
    assert len(content) == 13
