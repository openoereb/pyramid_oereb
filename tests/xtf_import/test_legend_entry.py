# -*- coding: utf-8 -*-
from lxml.etree import XML
from pyramid_oereb.standard.models.airports_security_zone_plans \
    import LegendEntry as LegendEntryModel
from pyramid_oereb.standard.xtf_import.legend_entry import LegendEntry
from tests.xtf_import import MockSession


def test_init():
    legend_entry = LegendEntry('foo', 'bar', 'baz')
    assert legend_entry._session == 'foo'
    assert legend_entry._model == 'bar'
    assert legend_entry._topic_code == 'baz'


def test_parse():
    element = XML("""
    <OeREBKRMtrsfr_V1_1.Transferstruktur.DarstellungsDienst TID="ch.admin.bazl.sizo.wms">
        <Legende>
            <OeREBKRMtrsfr_V1_1.Transferstruktur.LegendeEintrag>
                <Symbol>
                    <BINBLBOX>test</BINBLBOX>
                </Symbol>
                <LegendeText>
                    <LocalisationCH_V1.MultilingualText>
                        <LocalisedText>
                            <LocalisationCH_V1.LocalisedText>
                                <Language>de</Language>
                                <Text>Sicherheitszonenperimeter</Text>
                            </LocalisationCH_V1.LocalisedText>
                            <LocalisationCH_V1.LocalisedText>
                                <Language>fr</Language>
                                <Text>Périmètre de la zone de sécurité</Text>
                            </LocalisationCH_V1.LocalisedText>
                            <LocalisationCH_V1.LocalisedText>
                                <Language>it</Language>
                                <Text>Perimetro della zona di sicurezza</Text>
                            </LocalisationCH_V1.LocalisedText>
                        </LocalisedText>
                    </LocalisationCH_V1.MultilingualText>
                </LegendeText>
                <ArtCode>108-T-01</ArtCode>
                <ArtCodeliste>https://models.geo.admin.ch/BAZL/SafetyZonePlan_Catalogues_V1_2_20181102.xml</ArtCodeliste>
                <Thema>SicherheitszonenplanFlughafen</Thema>
                <SubThema>A SubTheme</SubThema>
            </OeREBKRMtrsfr_V1_1.Transferstruktur.LegendeEintrag>
        </Legende>
    </OeREBKRMtrsfr_V1_1.Transferstruktur.DarstellungsDienst>
    """)
    session = MockSession()
    legend_entry = LegendEntry(
        session,
        LegendEntryModel,
        'AirportsSecurityZonePlans'
    )
    legend_entry.parse(element)
    parsed = session.getData()
    assert len(parsed) == 1
    assert parsed[0].id == 'ch.admin.bazl.sizo.wms.legende.1'
    assert parsed[0].symbol == 'test'
    assert parsed[0].legend_text['de'] == 'Sicherheitszonenperimeter'
    assert parsed[0].type_code == '108-T-01'
    assert parsed[0].type_code_list == 'https://models.geo.admin.ch/BAZL/' \
                                       'SafetyZonePlan_Catalogues_V1_2_20181102.xml'
    assert parsed[0].topic == 'AirportsSecurityZonePlans'
    assert parsed[0].sub_theme == {
        'de': 'A SubTheme'
    }
    assert parsed[0].other_theme is None
    assert parsed[0].view_service_id == 'ch.admin.bazl.sizo.wms'


def test_parse_symbol():
    element = XML("""
    <LegendeEintrag>
        <Symbol>
            <BINBLBOX>test</BINBLBOX>
        </Symbol>
    </LegendeEintrag>
    """)
    legend_entry = LegendEntry('foo', 'bar', 'baz')
    assert legend_entry._parse_symbol(element, 'foo') is None
    assert legend_entry._parse_symbol(element, 'Symbol') == 'test'
