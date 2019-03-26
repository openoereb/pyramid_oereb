# -*- coding: utf-8 -*-
from lxml.etree import XML
from pyramid_oereb.standard.models.airports_security_zone_plans \
    import ViewService as ViewServiceModel, LegendEntry as LegendEntryModel
from pyramid_oereb.standard.xtf_import.legend_entry import LegendEntry
from pyramid_oereb.standard.xtf_import.view_service import ViewService
from tests.xtf_import import MockSession


def test_init():
    view_service = ViewService('foo', 'bar', 'baz')
    assert view_service._session == 'foo'
    assert view_service._model == 'bar'
    assert view_service._legend_entry == 'baz'


def test_parse():
    element = XML("""
    <OeREBKRMtrsfr_V1_1.Transferstruktur.DarstellungsDienst TID="ch.admin.bazl.sizo.wms">
        <VerweisWMS>https://wms.geo.admin.ch/?SERVICE=WMS&amp;REQUEST=GetMap&amp;VERSION=1.1.1&amp;LAYERS=ch.bazl.sicherheitszonenplan.oereb&amp;STYLES=default&amp;SRS=EPSG:21781&amp;BBOX=475000,60000,845000,310000&amp;WIDTH=740&amp;HEIGHT=500&amp;FORMAT=image/png</VerweisWMS>
        <LegendeImWeb>http://example.com</LegendeImWeb>
    </OeREBKRMtrsfr_V1_1.Transferstruktur.DarstellungsDienst>
    """)
    legend_entry_session = MockSession()
    legend_entry = LegendEntry(legend_entry_session, LegendEntryModel, 'AirportsSecurityZonePlans')
    view_service_session = MockSession()
    view_service = ViewService(view_service_session, ViewServiceModel, legend_entry)
    view_service.parse(element)
    parsed = view_service_session.getData()
    assert len(parsed) == 1
    assert parsed[0].reference_wms == 'https://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetMap&VERSION=1.1.1' \
                                      '&LAYERS=ch.bazl.sicherheitszonenplan.oereb&STYLES=default' \
                                      '&SRS=EPSG:21781&BBOX=475000,60000,845000,310000&WIDTH=740' \
                                      '&HEIGHT=500&FORMAT=image/png'
    assert parsed[0].legend_at_web == {'de': 'http://example.com'}


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
