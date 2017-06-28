# -*- coding: utf-8 -*-

import base64

import datetime
import pytest
from shapely.geometry import MultiPolygon, Polygon, Point, LineString

from pyramid.path import DottedNameResolver

from pyramid_oereb import Config
from pyramid_oereb.lib.records.documents import LegalProvisionRecord, ArticleRecord, DocumentRecord
from pyramid_oereb.lib.records.embeddable import EmbeddableRecord
from pyramid_oereb.lib.records.exclusion_of_liability import ExclusionOfLiabilityRecord
from pyramid_oereb.lib.records.extract import ExtractRecord
from pyramid_oereb.lib.records.geometry import GeometryRecord
from pyramid_oereb.lib.records.glossary import GlossaryRecord
from pyramid_oereb.lib.records.image import ImageRecord
from pyramid_oereb.lib.records.office import OfficeRecord
from pyramid_oereb.lib.records.plr import PlrRecord
from pyramid_oereb.lib.records.real_estate import RealEstateRecord
from pyramid_oereb.lib.records.theme import ThemeRecord, EmbeddableThemeRecord
from pyramid_oereb.lib.records.view_service import ViewServiceRecord, LegendEntryRecord
from pyramid_oereb.lib.renderer import Base
from pyramid_oereb.lib.renderer.extract.json_ import Renderer
from pyramid_oereb.tests.conftest import MockRequest, pyramid_oereb_test_config
from pyramid_oereb.tests.renderer import DummyRenderInfo
from pyramid_oereb.views.webservice import Parameter


@pytest.fixture()
def params():
    return Parameter('reduced', 'json', False, False, 'BL0200002829', '1000', 'CH775979211712', 'de')


def test_get_localized_text_from_str(config):
    assert isinstance(config._config, dict)
    renderer = Renderer(DummyRenderInfo())
    renderer._language = u'de'
    assert renderer.get_localized_text('test') == [
        {
            u'Language': u'de',
            u'Text': u'test'
        }
    ]


@pytest.mark.parametrize('language,result', [
    (u'de', u'Dies ist ein Test'),
    (u'en', u'This is a test'),
    (u'fr', u'Dies ist ein Test')  # fr not available; use default language (de)
])
def test_get_localized_text_from_dict(config, language, result):
    assert isinstance(config._config, dict)
    renderer = Renderer(DummyRenderInfo())
    renderer._language = language
    multilingual_text = {
        u'de': u'Dies ist ein Test',
        u'en': u'This is a test'
    }
    localized_text = renderer.get_localized_text(multilingual_text)
    assert isinstance(localized_text, list)
    assert len(localized_text) == 1
    assert localized_text[0][u'Text'] == result


@pytest.mark.parametrize('parameter', [
    params(),
    Parameter('reduced', 'json', False, True, 'BL0200002829', '1000', 'CH775979211712', 'de'),
    None
])
def test_render(config, parameter):
    date = datetime.datetime.now()
    assert isinstance(config._config, dict)
    with pyramid_oereb_test_config():
        view_service = ViewServiceRecord(u'http://geowms.bl.ch', u'http://geowms.bl.ch')
        real_estate = RealEstateRecord(u'RealEstate', u'BL', u'Liestal', 2829, 11395,
                                       MultiPolygon([Polygon([(0, 0), (1, 1), (1, 0)])]),
                                       u'http://www.geocat.ch', u'1000', u'BL0200002829', u'CH775979211712',
                                       plan_for_land_register=view_service)
        office_record = OfficeRecord({u'de': u'AGI'})
        resolver = DottedNameResolver()
        date_method_string = Config.get('extract').get('base_data').get('methods').get('date')
        date_method = resolver.resolve(date_method_string)
        av_update_date = date_method(real_estate)
        base_data = Config.get_base_data(av_update_date)

        av_provider_method_string = Config.get('extract').get('base_data').get('methods').get('provider')
        av_provider_method = resolver.resolve(av_provider_method_string)
        cadaster_state = date
        # TODO: Add real theme sources here
        theme_sources = []
        themes = [EmbeddableThemeRecord(u'TEST', {u'de': u'TEST TEXT'}, theme_sources)]
        plr_cadastre_authority = Config.get_plr_cadastre_authority()
        embeddable = EmbeddableRecord(
            cadaster_state,
            plr_cadastre_authority,
            av_provider_method(real_estate),
            av_update_date,
            themes
        )
        extract = ExtractRecord(
            real_estate,
            ImageRecord(bin(1)),
            ImageRecord(bin(2)),
            ImageRecord(bin(3)),
            ImageRecord(bin(4)),
            office_record,
            base_data,
            embeddable,
            exclusions_of_liability=[
                ExclusionOfLiabilityRecord({u'de': u'Haftungsausschluss'}, {u'de': u'Test'})
            ],
            glossaries=[GlossaryRecord({u'de': u'Glossar'}, {u'de': u'Test'})],
            general_information={u'de': u'Allgemeine Informationen'}
        )
        extract.qr_code = bin(1)
        extract.electronic_signature = 'Signature'
        renderer = Renderer(DummyRenderInfo())
        renderer._language = u'de'
        renderer._request = MockRequest()
        if parameter is None:
            with pytest.raises(TypeError):
                renderer._render(extract, None)
        else:
            result = renderer._render(extract, parameter)
            assert isinstance(result, dict)
            expected = {
                'ExtractIdentifier': unicode(extract.extract_identifier),
                'CreationDate': Base.date_time(extract.creation_date),
                'ConcernedTheme': [],
                'NotConcernedTheme': [],
                'ThemeWithoutData': [],
                'isReduced': True,
                'PLRCadastreAuthority': renderer.format_office(office_record),
                'BaseData': renderer.get_localized_text(Config.get_base_data(av_update_date)),
                'RealEstate': renderer.format_real_estate(real_estate),
                'GeneralInformation': [{'Language': 'de', 'Text': 'Allgemeine Informationen'}],
                'QRCode': bin(1),
                'ExclusionOfLiability': [{
                    'Title': [{'Language': 'de', 'Text': 'Haftungsausschluss'}],
                    'Content': [{'Language': 'de', 'Text': 'Test'}]
                }],
                'Glossary': [{
                    'Title': [{'Language': 'de', 'Text': 'Glossar'}],
                    'Content': [{'Language': 'de', 'Text': 'Test'}]
                }],
                'ElectronicSignature': 'Signature'
            }
            if parameter.images:
                expected.update({
                    'LogoPLRCadastre': unicode(base64.b64encode(bin(1))),
                    'FederalLogo': unicode(base64.b64encode(bin(2))),
                    'CantonalLogo': unicode(base64.b64encode(bin(3))),
                    'MunicipalityLogo': unicode(base64.b64encode(bin(4)))
                })
            else:
                expected.update({
                    'LogoPLRCadastreRef': u'http://example.com/image/logo/oereb',
                    'FederalLogoRef': u'http://example.com/image/logo/confederation',
                    'CantonalLogoRef': u'http://example.com/image/logo/canton',
                    'MunicipalityLogoRef': u'http://example.com/image/municipality/2829'
                })
            assert result == expected


def test_format_office(config):
    assert isinstance(config._config, dict)
    renderer = Renderer(DummyRenderInfo())
    renderer._language = u'de'
    office = OfficeRecord({u'de': u'Test'}, uid=u'test_uid', office_at_web=u'http://test.example.com',
                          line1=u'test_line1', line2=u'test_line2', street=u'test_street',
                          number=u'test_number', postal_code=1234, city=u'test_city')
    assert renderer.format_office(office) == {
        u'Name': renderer.get_localized_text('Test'),
        u'UID': u'test_uid',
        u'OfficeAtWeb': u'http://test.example.com',
        u'Line1': u'test_line1',
        u'Line2': u'test_line2',
        u'Street': u'test_street',
        u'Number': u'test_number',
        u'PostalCode': 1234,
        u'City': u'test_city'
    }


def test_format_real_estate(config):
    assert isinstance(config._config, dict)
    renderer = Renderer(DummyRenderInfo())
    renderer._language = u'de'
    renderer._params = Parameter(
        'reduced', 'json', True, False, 'BL0200002829', '1000', 'CH775979211712', 'de')
    geometry = MultiPolygon([Polygon([(0, 0), (1, 1), (1, 0)])])
    view_service = ViewServiceRecord(u'http://geowms.bl.ch', u'http://geowms.bl.ch')
    document = DocumentRecord(u'inForce', datetime.date.today(), {u'de': u'Test Dokument'},
                              OfficeRecord({u'de': u'BUD'}), {'de': 'http://mein.dokument.ch'})
    real_estate = RealEstateRecord(u'RealEstate', u'BL', u'Liestal', 2829, 11395,
                                   geometry, u'http://www.geocat.ch', u'1000', u'BL0200002829',
                                   u'CH775979211712', u'Subunit', [], plan_for_land_register=view_service,
                                   references=[document])
    result = renderer.format_real_estate(real_estate)
    assert isinstance(result, dict)
    assert result == {
        u'Type': u'RealEstate',
        u'Canton': u'BL',
        u'Municipality': u'Liestal',
        u'FosNr': 2829,
        u'LandRegistryArea': 11395,
        u'PlanForLandRegister': renderer.format_map(view_service),
        u'Limit': renderer.from_shapely(geometry),
        u'Number': u'1000',
        u'IdentDN': u'BL0200002829',
        u'EGRID': u'CH775979211712',
        u'SubunitOfLandRegister': u'Subunit',
        u'MetadataOfGeographicalBaseData': u'http://www.geocat.ch',
        u'Reference': [renderer.format_document(document)]
    }


@pytest.mark.parametrize('parameter', [
    params(),
    Parameter('reduced', 'json', False, True, 'BL0200002829', '1000', 'CH775979211712', 'de'),
    Parameter('full', 'json', False, False, 'BL0200002829', '1000', 'CH775979211712', 'de')
])
def test_format_plr(config, parameter):
    assert isinstance(config._config, dict)
    with pyramid_oereb_test_config():
        renderer = Renderer(DummyRenderInfo())
        renderer._language = 'de'
        renderer._params = parameter
        renderer._request = MockRequest()
        document = DocumentRecord(u'inForce', datetime.date.today(), {u'de': u'Test Dokument'},
                                  OfficeRecord({u'de': u'BUD'}), {'de': 'http://mein.dokument.ch'})
        if parameter.flavour == 'reduced':
            documents = [document]
        else:
            documents = None
        theme = ThemeRecord(u'Test', {u'de': u'Test theme'})
        office = OfficeRecord({'de': 'Test Office'})
        legend_entry = LegendEntryRecord(base64.b64encode(bin(1)), {'de': 'Test'}, 'test', 'TypeCodeList',
                                         theme)
        view_service = ViewServiceRecord('http://geowms.bl.ch', 'http://geowms.bl.ch', [legend_entry])
        plr = PlrRecord(
            theme,
            {'de': 'Test PLR'},
            'inForce',
            datetime.date.today(),
            office,
            ImageRecord(bin(1)),
            subtopic='Subtopic',
            additional_topic='Additional topic',
            type_code='test',
            type_code_list='TypeCodeList',
            view_service=view_service,
            documents=documents
        )
        plr.part_in_percent = 0.5
        if parameter.flavour == 'full':
            with pytest.raises(ValueError):
                renderer.format_plr([plr])
        else:
            result = renderer.format_plr([plr])
            assert isinstance(result, list)
            assert len(result) == 1
            assert isinstance(result[0], dict)
            expected = {
                'Information': renderer.get_localized_text(plr.content),
                'Theme': renderer.format_theme(plr.theme),
                'Lawstatus': 'inForce',
                'Area': None,
                'ResponsibleOffice': renderer.format_office(plr.responsible_office),
                'Map': renderer.format_map(plr.view_service),
                'SubTheme': 'Subtopic',
                'OtherTheme': 'Additional topic',
                'TypeCode': 'test',
                'TypeCodelist': 'TypeCodeList',
                'LegalProvisions': [renderer.format_document(document)],
                'PartInPercent': 0.5
            }
            if parameter.images:
                expected.update({
                    'Symbol': base64.b64encode(bin(1))
                })
            else:
                expected.update({
                    'SymbolRef': 'http://example.com/image/symbol/Test/test'
                })
            assert result[0] == expected


@pytest.mark.parametrize('document,result_dict', [
    (LegalProvisionRecord('inForce', datetime.date.today(), {'de': 'Test Rechtsvorschrift'},
                          OfficeRecord({'de': 'AGI'}), {'de': 'http://meine.rechtsvorschrift.ch'},
                          {'de': 'Test'}, 'rv.test.1', {'de': 'Rechtsvorschrift Test'}, 'BL', 'Liestal',
                          ['Art.1', 'Art.2', 'Art.3'], bin(1), [
                              ArticleRecord('inForce', datetime.date.today(), 'art.1')
                          ], [
                              DocumentRecord('inForce', datetime.date.today(), {'de': 'Test Dokument'},
                                             OfficeRecord({'de': 'BUD'}), {'de': 'http://mein.dokument.ch'})
                          ]), {
        'Lawstatus': 'inForce',
        'TextAtWeb': [{'Language': 'de', 'Text': 'http://meine.rechtsvorschrift.ch'}],
        'Title': [{'Language': 'de', 'Text': 'Test Rechtsvorschrift'}],
        'ResponsibleOffice': {
            'Name': [{'Language': 'de', 'Text': 'AGI'}]
        },
        'OfficialTitle': [{'Language': 'de', 'Text': 'Rechtsvorschrift Test'}],
        'Abbrevation': [{'Language': 'de', 'Text': 'Test'}],
        'OfficialNumber': 'rv.test.1',
        'Canton': 'BL',
        'Municipality': 'Liestal',
        'ArticleNumber': ['Art.1', 'Art.2', 'Art.3'],
        'Article': [{
            'Lawstatus': 'inForce',
            'Number': 'art.1'
        }],
        'Reference': [{
            'Lawstatus': 'inForce',
            'TextAtWeb': [{'Language': 'de', 'Text': 'http://mein.dokument.ch'}],
            'Title': [{'Language': 'de', 'Text': 'Test Dokument'}],
            'ResponsibleOffice': {
                'Name': [{'Language': 'de', 'Text': 'BUD'}]
            }
        }]
    }),
    (ArticleRecord(u'inForce', datetime.date.today(), u'art.2', {'de': 'http://mein.artikel.ch/2'},
                   {u'de': u'Test-Artikel'}), {
        'Lawstatus': 'inForce',
        'Number': 'art.2',
        'TextAtWeb': [{'Language': 'de', 'Text': 'http://mein.artikel.ch/2'}],
        'Text': [{'Language': 'de', 'Text': 'Test-Artikel'}]
    })
])
def test_format_document(config, params, document, result_dict):
    assert isinstance(config._config, dict)
    renderer = Renderer(DummyRenderInfo())
    renderer._language = u'de'
    renderer._params = params
    result = renderer.format_document(document)
    assert isinstance(result, dict)
    assert result == result_dict


@pytest.mark.parametrize('geometry,result_dict', [
    (GeometryRecord(u'inForce', datetime.date.today(), Point(0, 0), geo_metadata='http://www.geocat.ch',
                    office=OfficeRecord({u'de': u'AGI'})),  {
        'Lawstatus': 'inForce',
        'ResponsibleOffice': {
            'Name': [{'Language': 'de', 'Text': 'AGI'}]
        },
        'MetadataOfGeographicalBaseData': 'http://www.geocat.ch',
        'Point': {
            'crs': 'EPSG:2056',
            'coordinates': (0, 0)
        }
    }),
    (GeometryRecord(u'inForce', datetime.date.today(), LineString([(0, 0), (1, 1)]),
                    office=OfficeRecord({u'de': u'AGI'})),  {
        'Lawstatus': 'inForce',
        'ResponsibleOffice': {
            'Name': [{'Language': 'de', 'Text': 'AGI'}]
        },
        'Line': {
            'crs': 'EPSG:2056',
            'coordinates': ((0, 0), (1, 1))
        }
    }),
    (GeometryRecord(u'inForce', datetime.date.today(), Polygon([(0, 0), (1, 1), (1, 0)]),
                    office=OfficeRecord({u'de': u'AGI'})),  {
        'Lawstatus': 'inForce',
        'ResponsibleOffice': {
            'Name': [{'Language': 'de', 'Text': 'AGI'}]
        },
        'Surface': {
            'crs': 'EPSG:2056',
            'coordinates': (((0, 0), (1, 1), (1, 0), (0, 0)), )
        }
    })
])
def test_format_geometry(config, params, geometry, result_dict):
    assert isinstance(config._config, dict)
    renderer = Renderer(DummyRenderInfo())
    renderer._language = u'de'
    renderer._params = params
    result = renderer.format_geometry(geometry)
    assert isinstance(result, dict)
    assert result == result_dict


def test_format_theme(config, params):
    assert isinstance(config._config, dict)
    renderer = Renderer(DummyRenderInfo())
    renderer._language = u'de'
    renderer._params = params
    theme = ThemeRecord(u'TestTheme', {u'de': u'Test-Thema'})
    result = renderer.format_theme(theme)
    assert isinstance(result, dict)
    assert result == {
        'Code': 'TestTheme',
        'Text': renderer.get_localized_text({'de': 'Test-Thema'})
    }


def test_format_map(config, params):
    assert isinstance(config._config, dict)
    with pyramid_oereb_test_config():
        renderer = Renderer(DummyRenderInfo())
        renderer._language = u'de'
        renderer._params = params
        renderer._request = MockRequest()
        legend_entry = LegendEntryRecord(
            ImageRecord(bin(1)),
            {u'de': u'Legendeneintrag'},
            u'type1',
            u'type_code_list',
            ThemeRecord(u'test', {u'de': u'Test'})
        )
        view_service = ViewServiceRecord('http://my.wms.ch',
                                         'http://my.wms.ch?SERVICE=WMS&REQUEST=GetLegendGraphic',
                                         [legend_entry])
        view_service.image = ImageRecord(bin(1))
        result = renderer.format_map(view_service)
        assert isinstance(result, dict)
        assert result == {
            'Image': base64.b64encode(bin(1)),
            'ReferenceWMS': 'http://my.wms.ch',
            'LegendAtWeb': 'http://my.wms.ch?SERVICE=WMS&REQUEST=GetLegendGraphic',
            'OtherLegend': [renderer.format_legend_entry(legend_entry)]
        }


@pytest.mark.parametrize('parameter', [
    params(),
    Parameter('reduced', 'json', False, True, 'BL0200002829', '1000', 'CH775979211712', 'de')
])
def test_format_legend_entry(parameter, config):
    assert isinstance(config._config, dict)
    with pyramid_oereb_test_config():
        renderer = Renderer(DummyRenderInfo())
        renderer._language = u'de'
        renderer._params = parameter
        renderer._request = MockRequest()
        theme = ThemeRecord(u'test', {u'de': u'Test'})
        legend_entry = LegendEntryRecord(
            ImageRecord(bin(1)),
            {u'de': u'Legendeneintrag'},
            u'type1',
            u'type_code_list',
            theme,
            u'Subthema',
            u'Weiteres Thema'
        )
        result = renderer.format_legend_entry(legend_entry)
        expected = {
            'LegendText': renderer.get_localized_text({'de': 'Legendeneintrag'}),
            'TypeCode': 'type1',
            'TypeCodelist': 'type_code_list',
            'Theme': renderer.format_theme(theme),
            'SubTheme': 'Subthema',
            'OtherTheme': 'Weiteres Thema'
        }
        if parameter.images:
            expected.update({
                'Symbol': ImageRecord(bin(1)).encode()
            })
        else:
            expected.update({
                'SymbolRef': 'http://example.com/image/symbol/test/type1'
            })
        assert isinstance(result, dict)
        assert result == expected


def test_embeddable(params):
    renderer = Renderer(DummyRenderInfo())
    renderer._language = u'de'
    renderer._params = params
    date = datetime.datetime.now()
    view_service = ViewServiceRecord(u'http://geowms.bl.ch', u'http://geowms.bl.ch')
    real_estate = RealEstateRecord(
        u'RealEstate',
        u'BL',
        u'Liestal',
        2829,
        11395,
        MultiPolygon([Polygon([(0, 0), (1, 1), (1, 0)])]),
        u'http://www.geocat.ch', u'1000', u'BL0200002829', u'CH775979211712',
        plan_for_land_register=view_service
    )
    resolver = DottedNameResolver()
    date_method_string = Config.get('extract').get('base_data').get('methods').get('date')
    date_method = resolver.resolve(date_method_string)
    av_update_date = date_method(real_estate)

    av_provider_method_string = Config.get('extract').get('base_data').get('methods').get('provider')
    av_provider_method = resolver.resolve(av_provider_method_string)
    cadaster_state = date
    # TODO: Add real theme sources here
    theme_sources = []
    themes = [EmbeddableThemeRecord(u'TEST', {u'de': u'TEST TEXT'}, theme_sources)]
    plr_cadastre_authority = Config.get_plr_cadastre_authority()
    embeddable = EmbeddableRecord(
        cadaster_state,
        plr_cadastre_authority,
        av_provider_method(real_estate),
        av_update_date,
        themes
    )
    result = renderer.format_embeddable(embeddable)
    assert result == {
        u'cadasterOrganisationName': plr_cadastre_authority.name.get('de'),
        u'datasource': [{
            u'topic': {
                'Text': [{'Text': u'TEST TEXT', 'Language': 'de'}],
                'Code': 'TEST'
            },
            u'sources': []
        }],
        u'cadasterState': cadaster_state.strftime('%d-%m-%YT%H:%M:%S'),
        u'dataOwnerNameCadastralSurveying': u'This is only a dummy',
        u'transferFromSourceCadastralSurveying': av_update_date.strftime('%d-%m-%YT%H:%M:%S')
    }
