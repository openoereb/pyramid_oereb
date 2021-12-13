# -*- coding: utf-8 -*-

import pytest

from pyramid_oereb.core.renderer.extract.xml_ import Renderer
from pyramid_oereb.core.records.view_service import ViewServiceRecord


@pytest.fixture
def view_template(xml_templates):
    return xml_templates.get_template('view_service.xml')


def test_empty(view_template, pyramid_oereb_test_config):
    map = ViewServiceRecord(
        reference_wms=dict(),
        layer_index=0,
        layer_opacity=1.0
    )
    content = view_template.render(**{
        'map': map
    }).decode('utf-8').split('\n')
    assert content[0] == ''  # empty filler line
    assert content[1] == '<data:layerIndex>0</data:layerIndex>'
    assert content[2] == '<data:layerOpacity>1.0</data:layerOpacity>'
    assert content[3] == ''  # empty filler line
    assert len(content) == 4


def test_reference_wms(DummyRenderInfo, view_template, pyramid_oereb_test_config):
    renderer = Renderer(DummyRenderInfo())
    renderer._language = 'de'
    map = ViewServiceRecord(
        reference_wms={'de': 'http://example.com?SERVICE=WMS&REQUEST=GetMap&FORMAT=image/png&SRS=epsg:2056'},
        layer_index=0,
        layer_opacity=1.0
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
