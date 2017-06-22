# -*- coding: utf-8 -*-
import base64
from json import loads

import datetime
import pytest
from shapely.geometry import MultiPolygon, Polygon, Point, LineString

from pyramid_oereb.lib.records.documents import LegalProvisionRecord, ArticleRecord, DocumentRecord
from pyramid_oereb.lib.records.exclusion_of_liability import ExclusionOfLiabilityRecord
from pyramid_oereb.lib.records.extract import ExtractRecord
from pyramid_oereb.lib.records.geometry import GeometryRecord
from pyramid_oereb.lib.records.glossary import GlossaryRecord
from pyramid_oereb.lib.records.image import ImageRecord
from pyramid_oereb.lib.records.office import OfficeRecord
from pyramid_oereb.lib.records.plr import PlrRecord
from pyramid_oereb.lib.records.real_estate import RealEstateRecord
from pyramid_oereb.lib.records.theme import ThemeRecord
from pyramid_oereb.lib.records.view_service import ViewServiceRecord, LegendEntryRecord
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
    renderer._language_ = u'de'
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
    renderer._language_ = language
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
    assert isinstance(config._config, dict)
    with pyramid_oereb_test_config():
        view_service = ViewServiceRecord(u'http://geowms.bl.ch', u'http://geowms.bl.ch')
        real_estate = RealEstateRecord(u'RealEstate', u'BL', u'Liestal', 2829, 11395,
                                       MultiPolygon([Polygon([(0, 0), (1, 1), (1, 0)])]),
                                       u'http://www.geocat.ch', u'1000', u'BL0200002829', u'CH775979211712',
                                       plan_for_land_register=view_service)
        office_record = OfficeRecord({u'de': u'AGI'})
        extract = ExtractRecord(real_estate, ImageRecord(bin(1)), ImageRecord(bin(2)), ImageRecord(bin(3)),
                                ImageRecord(bin(4)), office_record,
                                {u'de': u'Daten der amtlichen Vermessung'},
                                [ExclusionOfLiabilityRecord({'de': 'Haftungsausschluss'}, {'de': 'Test'})],
                                [GlossaryRecord({'de': 'Glossar'}, {'de': 'Test'})],
                                general_information={'de': 'Allgemeine Informationen'})
        extract.qr_code = bin(1)
        extract.electronic_signature = 'Signature'
        renderer = Renderer(DummyRenderInfo())
        renderer._language_ = u'de'
        renderer._params_ = parameter
        renderer._request = MockRequest()
        if parameter is None:
            with pytest.raises(TypeError):
                renderer._render(extract)
        else:
            result = loads(renderer._render(extract))
            assert isinstance(result, dict)
            assert u'GetExtractByIdResponse' in result
            expected = {
                u'ExtractIdentifier': unicode(extract.extract_identifier),
                u'CreationDate': unicode(datetime.date.today().isoformat() + 'T00:00:00'),
                u'ConcernedTheme': [],
                u'NotConcernedTheme': [],
                u'ThemeWithoutData': [],
                u'isReduced': True,
                u'PLRCadastreAuthority': renderer.format_office(office_record),
                u'BaseData': renderer.get_localized_text({u'de': u'Daten der amtlichen Vermessung'}),
                u'RealEstate': renderer.format_real_estate(real_estate),
                u'GeneralInformation': [{u'Language': u'de', u'Text': u'Allgemeine Informationen'}],
                u'QRCode': unicode(bin(1)),
                u'ExclusionOfLiability': [{
                    u'Title': [{u'Language': u'de', u'Text': u'Haftungsausschluss'}],
                    u'Content': [{u'Language': u'de', u'Text': u'Test'}]
                }],
                u'Glossary': [{
                    u'Title': [{u'Language': u'de', u'Text': u'Glossar'}],
                    u'Content': [{u'Language': u'de', u'Text': u'Test'}]
                }],
                u'ElectronicSignature': u'Signature'
            }
            if parameter.images:
                expected.update({
                    u'LogoPLRCadastre': unicode(base64.b64encode(bin(1))),
                    u'FederalLogo': unicode(base64.b64encode(bin(2))),
                    u'CantonalLogo': unicode(base64.b64encode(bin(3))),
                    u'MunicipalityLogo': unicode(base64.b64encode(bin(4)))
                })
            else:
                expected.update({
                    u'LogoPLRCadastreRef': u'http://example.com/image/logo/oereb',
                    u'FederalLogoRef': u'http://example.com/image/logo/confederation',
                    u'CantonalLogoRef': u'http://example.com/image/logo/canton',
                    u'MunicipalityLogoRef': u'http://example.com/image/municipality/2829'
                })
            assert result == {
                u'GetExtractByIdResponse': {
                    u'extract': expected
                }
            }


def test_format_office(config):
    assert isinstance(config._config, dict)
    renderer = Renderer(DummyRenderInfo())
    renderer._language_ = u'de'
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
    renderer._language_ = u'de'
    renderer._params_ = Parameter('reduced', 'json', True, False, 'BL0200002829', '1000', 'CH775979211712',
                                  'de')
    geometry = MultiPolygon([Polygon([(0, 0), (1, 1), (1, 0)])])
    view_service = ViewServiceRecord(u'http://geowms.bl.ch', u'http://geowms.bl.ch')
    document = DocumentRecord('inForce', datetime.date.today(), {'de': 'Test Dokument'},
                              OfficeRecord({'de': 'BUD'}), {'de': 'http://mein.dokument.ch'})
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
    with pyramid_oereb_test_config():
        assert isinstance(config._config, dict)
        renderer = Renderer(DummyRenderInfo())
        renderer._language_ = 'de'
        renderer._params_ = parameter
        renderer._request = MockRequest()
        document = DocumentRecord('inForce', datetime.date.today(), {'de': 'Test Dokument'},
                                  OfficeRecord({'de': 'BUD'}), {'de': 'http://mein.dokument.ch'})
        if parameter.flavour == 'reduced':
            documents = [document]
        else:
            documents = None
        theme = ThemeRecord('Test', {'de': 'Test theme'})
        office = OfficeRecord({'de': 'Test Office'})
        legen_entry = LegendEntryRecord(base64.b64encode(bin(1)), {'de': 'Test'}, 'test', 'TypeCodeList',
                                        theme)
        view_service = ViewServiceRecord('http://geowms.bl.ch', 'http://geowms.bl.ch', [legen_entry])
        plr = PlrRecord(theme, {'de': 'Test PLR'}, 'inForce', datetime.date.today(), office, 'Subtopic',
                        'Additional topic', 'test', 'TypeCodeList', view_service, documents=documents,
                        symbol=base64.b64encode(bin(1)))
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
    (ArticleRecord('inForce', datetime.date.today(), 'art.2', {'de': 'http://mein.artikel.ch/2'},
                   {'de': 'Test-Artikel'}), {
        'Lawstatus': 'inForce',
        'Number': 'art.2',
        'TextAtWeb': [{'Language': 'de', 'Text': 'http://mein.artikel.ch/2'}],
        'Text': [{'Language': 'de', 'Text': 'Test-Artikel'}]
    })
])
def test_format_document(config, params, document, result_dict):
    assert isinstance(config._config, dict)
    renderer = Renderer(DummyRenderInfo())
    renderer._language_ = u'de'
    renderer._params_ = params
    result = renderer.format_document(document)
    assert isinstance(result, dict)
    assert result == result_dict


@pytest.mark.parametrize('geometry,result_dict', [
    (GeometryRecord('inForce', datetime.date.today(), Point(0, 0), geo_metadata='http://www.geocat.ch',
                    office=OfficeRecord({'de': 'AGI'})),  {
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
    (GeometryRecord('inForce', datetime.date.today(), LineString([(0, 0), (1, 1)]),
                    office=OfficeRecord({'de': 'AGI'})),  {
        'Lawstatus': 'inForce',
        'ResponsibleOffice': {
            'Name': [{'Language': 'de', 'Text': 'AGI'}]
        },
        'Line': {
            'crs': 'EPSG:2056',
            'coordinates': ((0, 0), (1, 1))
        }
    }),
    (GeometryRecord('inForce', datetime.date.today(), Polygon([(0, 0), (1, 1), (1, 0)]),
                    office=OfficeRecord({'de': 'AGI'})),  {
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
    renderer._language_ = u'de'
    renderer._params_ = params
    result = renderer.format_geometry(geometry)
    assert isinstance(result, dict)
    assert result == result_dict


def test_format_theme(config, params):
    assert isinstance(config._config, dict)
    renderer = Renderer(DummyRenderInfo())
    renderer._language_ = u'de'
    renderer._params_ = params
    theme = ThemeRecord('TestTheme', {'de': 'Test-Thema'})
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
        renderer._language_ = u'de'
        renderer._params_ = params
        renderer._request = MockRequest()
        legend_entry = LegendEntryRecord(bin(1), {'de': 'Legendeneintrag'}, 'type1', 'type_code_list',
                                         ThemeRecord('test', {'de': 'Test'}))
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
        renderer._language_ = u'de'
        renderer._params_ = parameter
        renderer._request = MockRequest()
        theme = ThemeRecord('test', {'de': 'Test'})
        legend_entry = LegendEntryRecord(bin(1), {'de': 'Legendeneintrag'}, 'type1', 'type_code_list', theme,
                                         'Subthema', 'Weiteres Thema')
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
                'Symbol': bin(1)
            })
        else:
            expected.update({
                'SymbolRef': 'http://example.com/image/symbol/test/type1'
            })
        assert isinstance(result, dict)
        assert result == expected
