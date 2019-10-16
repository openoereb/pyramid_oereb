# -*- coding: utf-8 -*-

from tests.renderer.xml import xml_templates
from pyramid_oereb.lib.records.view_service import ViewServiceRecord
from pyramid_oereb.views.webservice import Parameter
from pyramid_oereb.lib.renderer.extract.xml_ import Renderer

template = xml_templates().get_template('view_service.xml')


def test_empty():
    map = ViewServiceRecord(
        reference_wms='',
        layer_index=0,
        layer_opacity=1.0
    )
    content = template.render(**{
        'map': map
    }).decode('utf-8').split('\n')
    assert content[0] == ''  # empty filler line
    assert content[1] == '<data:layerIndex>0</data:layerIndex>'
    assert content[2] == '<data:layerOpacity>1.0</data:layerOpacity>'
    assert content[3] == ''  # empty filler line
    assert len(content) == 4


def test_reference_wms():
    map = ViewServiceRecord(
        reference_wms='http://example.com?SERVICE=WMS&REQUEST=GetMap&FORMAT=image/png&SRS=epsg:2056',
        layer_index=0,
        layer_opacity=1.0
    )
    content = template.render(**{
        'map': map
    }).decode('utf-8').split('\n')
    assert content[1] == """
    <data:ReferenceWMS>
    http%3A%2F%2Fexample.com%3F
    SERVICE%3DWMS%26
    REQUEST%3DGetMap%26
    FORMAT%3Dimage%2Fpng%26
    SRS%3Depsg%3A2056
    </data:ReferenceWMS>
    """.replace(" ", "").replace('\n', '')
    assert len(content) == 5


def test_legend_at_web():
    parameters = Parameter('reduced', 'xml', False, False, 'BL0200002829', '1000', 'CH775979211712', 'de')
    renderer = Renderer(None)
    legend_url = """
    http://example.com?
    SERVICE=WMS&
    REQUEST=GetLegendGraphic&
    FORMAT=image/png&
    SRS=epsg:2056
    """.replace(" ", "").replace('\n', '')
    map = ViewServiceRecord(
        reference_wms='',
        legend_at_web={'de': legend_url},
        layer_index=0,
        layer_opacity=1.0
    )
    content = template.render(**{
        'params': parameters,
        'localized': renderer.get_localized_text,
        'map': map
    }).decode('utf-8').split('\n')
    assert len(content) == 6
    assert content[2] == """
    <data:LegendAtWeb>
    http%3A%2F%2Fexample.com%3F
    SERVICE%3DWMS%26
    REQUEST%3DGetLegendGraphic%26
    FORMAT%3Dimage%2Fpng%26
    SRS%3Depsg%3A2056
    </data:LegendAtWeb>
    """.replace(" ", "").replace('\n', '')


def test_legend_at_web_no_language():
    # Requests italian, but only german is available -> best effort: deliver german instead
    parameters = Parameter('reduced', 'xml', False, False, 'BL0200002829', '1000', 'CH775979211712', 'it')
    renderer = Renderer(None)
    legend_url = """
    http://example.com?
    SERVICE=WMS&
    REQUEST=GetLegendGraphic&
    FORMAT=image/png&
    SRS=epsg:2056
    """.replace(" ", "").replace('\n', '')
    map = ViewServiceRecord(
        reference_wms='',
        legend_at_web={'de': legend_url},
        layer_index=0,
        layer_opacity=1.0
    )
    content = template.render(**{
        'params': parameters,
        'localized': renderer.get_localized_text,
        'map': map
    }).decode('utf-8').split('\n')
    assert len(content) == 6
    assert content[2] == """
        <data:LegendAtWeb>
        http%3A%2F%2Fexample.com%3F
        SERVICE%3DWMS%26
        REQUEST%3DGetLegendGraphic%26
        FORMAT%3Dimage%2Fpng%26
        SRS%3Depsg%3A2056
        </data:LegendAtWeb>
    """.replace(" ", "").replace('\n', '')
