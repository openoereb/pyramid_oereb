# -*- coding: utf-8 -*-

import pytest
from tests import params
from tests.renderer.xml import xml_templates
from pyramid_oereb.lib.records.view_service import ViewServiceRecord

template = xml_templates().get_template('view_service.xml')


@pytest.mark.parametrize('parameters', params)
def test_empty(parameters):
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


@pytest.mark.parametrize('parameters', params)
def test_reference_wms(parameters):
    map = ViewServiceRecord(
        reference_wms='http://example.com',
        layer_index=0,
        layer_opacity=1.0
    )
    content = template.render(**{
        'map': map
    }).decode('utf-8').split('\n')
    assert content[1] == '<data:ReferenceWMS>http%3A%2F%2Fexample.com</data:ReferenceWMS>'
    assert len(content) == 5


@pytest.mark.parametrize('parameters', params)
def test_legend_at_web(parameters):
    map = ViewServiceRecord(
        reference_wms='',
        legend_at_web='http://example-legend.com',
        layer_index=0,
        layer_opacity=1.0
    )
    content = template.render(**{
        'map': map
    }).decode('utf-8').split('\n')
    assert content[1] == '<data:LegendAtWeb>http%3A%2F%2Fexample-legend.com</data:LegendAtWeb>'
    assert len(content) == 5
