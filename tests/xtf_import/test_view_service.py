# -*- coding: utf-8 -*-
from pyramid_oereb.standard.xtf_import.view_service import ViewService


def test_init():
    view_service = ViewService('foo', 'bar', 'baz')
    assert view_service._session == 'foo'
    assert view_service._model == 'bar'
    assert view_service._legend_entry == 'baz'


def test_copy_legend_at_web_from_reference_wms():
    view_service = ViewService('foo', 'bar', 'baz')
    url = 'https://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetMap&VERSION=1.1.1&STYLES=default&SRS=EPSG:21781' \
          '&BBOX=475000,60000,845000,310000&WIDTH=740&HEIGHT=500&FORMAT=image/png' \
          '&LAYERS=ch.bav.kataster-belasteter-standorte-oev.oereb'
    result = view_service._copy_legend_at_web_from_reference_wms(url)
    assert 'https://wms.geo.admin.ch/?' in result
    assert 'LAYER=ch.bav.kataster-belasteter-standorte-oev.oereb' in result
    assert 'SERVICE=WMS' in result
    assert 'FORMAT=image%2Fpng' in result
    assert 'REQUEST=GetLegendGraphic' in result
    assert 'VERSION=1.1.1' in result
