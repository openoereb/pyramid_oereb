# -*- coding: utf-8 -*-
from lxml.etree import XML
import tests
from pyramid_oereb.lib.config import Config
from pyramid_oereb.standard.xtf_import.public_law_restriction import PublicLawRestriction
from pyramid_oereb.standard.sources.plr import StandardThemeConfigParser
from tests.xtf_import import MockSession

Config._config = None
Config.init(tests.pyramid_oereb_test_yml, 'pyramid_oereb')
theme_config = Config.get_theme_config_by_code('AirportsSecurityZonePlans')
config_parser = StandardThemeConfigParser(**theme_config)
models = config_parser.get_models()

PublicLawRestrictionModel = models.PublicLawRestriction


def test_init():
    public_law_restriction = PublicLawRestriction('foo', 'bar', 'baz')
    assert public_law_restriction._session == 'foo'
    assert public_law_restriction._model == 'bar'
    assert public_law_restriction._topic_code == 'baz'


def test_parse():
    element = XML("""
    <OeREBKRMtrsfr_V1_1.Transferstruktur.Eigentumsbeschraenkung TID="108-Z-0010-A">
        <Aussage>
            <LocalisationCH_V1.MultilingualMText>
                <LocalisedText>
                    <LocalisationCH_V1.LocalisedMText>
                        <Language>de</Language>
                        <Text>Höhenbeschränkung für Bauten und andere Hindernisse</Text>
                    </LocalisationCH_V1.LocalisedMText>
                    <LocalisationCH_V1.LocalisedMText>
                        <Language>fr</Language>
                        <Text>Limitation de la hauteur des bâtiments et autres obstacles</Text>
                    </LocalisationCH_V1.LocalisedMText>
                    <LocalisationCH_V1.LocalisedMText>
                        <Language>it</Language>
                        <Text>Limitazione di altezza per gli edifici e altri ostacoli</Text>
                    </LocalisationCH_V1.LocalisedMText>
                </LocalisedText>
            </LocalisationCH_V1.MultilingualMText>
        </Aussage>
        <Thema>SicherheitszonenplanFlughafen</Thema>
        <ArtCode>108-T-01</ArtCode>
        <ArtCodeliste>https://models.geo.admin.ch/BAZL/SafetyZonePlan_Catalogues_V1_2_20181102.xml</ArtCodeliste>
        <Rechtsstatus>inForce</Rechtsstatus>
        <publiziertAb>2001-03-02</publiziertAb>
        <DarstellungsDienst REF="ch.admin.bazl.sizo.wms"></DarstellungsDienst>
        <ZustaendigeStelle REF="ch.admin.bazl"></ZustaendigeStelle>
        <SubThema>Just a SubTheme</SubThema>
    </OeREBKRMtrsfr_V1_1.Transferstruktur.Eigentumsbeschraenkung>
    """)
    session = MockSession()
    public_law_restriction = PublicLawRestriction(
        session,
        PublicLawRestrictionModel,
        'AirportsSecurityZonePlans'
    )
    public_law_restriction.parse(element)
    parsed = session.getData()
    assert len(parsed) == 1
    assert parsed[0].id == '108-Z-0010-A'
    assert parsed[0].legend_text['de'] == u'Höhenbeschränkung für Bauten und andere Hindernisse'
    assert parsed[0].topic == 'AirportsSecurityZonePlans'
    assert parsed[0].sub_theme == {
        'de': 'Just a SubTheme'
    }
    assert parsed[0].type_code == '108-T-01'
    assert parsed[0].type_code_list == 'https://models.geo.admin.ch/BAZL/' \
                                       'SafetyZonePlan_Catalogues_V1_2_20181102.xml'
    assert parsed[0].law_status == 'inForce'
    assert parsed[0].published_from == '2001-03-02'
    assert parsed[0].view_service_id == 'ch.admin.bazl.sizo.wms'
    assert parsed[0].office_id == 'ch.admin.bazl'
