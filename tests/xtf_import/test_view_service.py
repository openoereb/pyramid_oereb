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
    <OeREBKRMtrsfr_V2_0.Transferstruktur.DarstellungsDienst TID="ch.admin.bazl.sizo.wms">
        <VerweisWMS>
            <LocalisationCH_V1.MultilingualMText>
                <LocalisedText>
                    <LocalisationCH_V1.LocalisedMText>
                        <Language>de</Language>
                        <Text>https://wms.geo.admin.ch/?SERVICE=WMS&amp;REQUEST=GetMap&amp;VERSION=1.1.1&amp;LAYERS=ch.bazl.sicherheitszonenplan.oereb&amp;STYLES=default&amp;SRS=EPSG:2056&amp;BBOX=2475000,1065000,2850000,1300000&amp;WIDTH=740&amp;HEIGHT=500&amp;FORMAT=image/png</Text>
                    </LocalisationCH_V1.LocalisedMText>
                </LocalisedText>
            </LocalisationCH_V1.MultilingualMText>
        </VerweisWMS>
    </OeREBKRMtrsfr_V2_0.Transferstruktur.DarstellungsDienst>
    """)
    legend_entry_session = MockSession()
    legend_entry = LegendEntry(legend_entry_session, LegendEntryModel, 'AirportsSecurityZonePlans')
    view_service_session = MockSession()
    view_service = ViewService(view_service_session, ViewServiceModel, legend_entry)
    view_service.parse(element)
    parsed = view_service_session.getData()
    assert len(parsed) == 1
    assert parsed[0].reference_wms == {'de':
                                       'https://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetMap&VERSION=1.1.1'
                                       '&LAYERS=ch.bazl.sicherheitszonenplan.oereb&STYLES=default'
                                       '&SRS=EPSG:2056&BBOX=2475000,1065000,2850000,1300000&WIDTH=740'
                                       '&HEIGHT=500&FORMAT=image/png'
                                       }
