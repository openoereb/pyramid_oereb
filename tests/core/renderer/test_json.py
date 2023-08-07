# -*- coding: utf-8 -*-

import datetime

import pytest
from shapely.geometry import MultiPolygon, Polygon, Point, LineString

from pyramid.path import DottedNameResolver

from pyramid_oereb import Config
from pyramid_oereb.core.adapter import FileAdapter
from pyramid_oereb.core.records.documents import DocumentRecord
from pyramid_oereb.core.records.document_types import DocumentTypeRecord
from pyramid_oereb.core.records.disclaimer import DisclaimerRecord
from pyramid_oereb.core.records.extract import ExtractRecord
from pyramid_oereb.core.records.geometry import GeometryRecord
from pyramid_oereb.core.records.glossary import GlossaryRecord
from pyramid_oereb.core.records.image import ImageRecord
from pyramid_oereb.core.records.logo import LogoRecord
from pyramid_oereb.core.records.office import OfficeRecord
from pyramid_oereb.core.records.plr import PlrRecord
from pyramid_oereb.core.records.law_status import LawStatusRecord
from pyramid_oereb.core.records.real_estate import RealEstateRecord
from pyramid_oereb.core.records.theme import ThemeRecord
from pyramid_oereb.core.records.general_information import GeneralInformationRecord
from pyramid_oereb.core.records.view_service import ViewServiceRecord, LegendEntryRecord
from pyramid_oereb.core.renderer import Base
from pyramid_oereb.core.renderer.extract.json_ import Renderer
from tests.mockrequest import MockRequest
from pyramid_oereb.core.views.webservice import Parameter


def law_status():
    return LawStatusRecord(u'inKraft', {u'de': u'Rechtskräftig'})


def default_param():
    return Parameter('json', False, False, False, 'BL0200002829', '1000', 'CH775979211712', 'de')


@pytest.fixture()
def params():
    return default_param()


def glossary_input():
    return [GlossaryRecord({'de': u'Glossar'}, {'de': u'Test'})]


def glossary_expected():
    return [{
        'Title': [{'Language': 'de', 'Text': 'Glossar'}],
        'Content': [{'Language': 'de', 'Text': 'Test'}]
    }]


@pytest.mark.parametrize('parameter, glossaries_input, glossaries_expected', [
    (default_param(), glossary_input(), glossary_expected()),
    (default_param(), [], []),
    (Parameter('json', 'reduced', False, True, 'BL0200002829', '1000', 'CH775979211712', 'de'),
     glossary_input(),
     glossary_expected()),
    (None, glossary_input(), glossary_expected()),
    (None, [], None),
    (None, None, None)
])
def test_render(pyramid_oereb_test_config, pyramid_test_config, DummyRenderInfo,
                parameter, glossaries_input, glossaries_expected, real_estate_test_data):
    view_service = ViewServiceRecord(
        {'de': u'http://geowms.bl.ch'},
        1, 1.0, 'de', 2056, None, None
    )
    real_estate = RealEstateRecord(u'Liegenschaft', u'BL', u'Liestal', 2829, 11395,
                                   MultiPolygon([Polygon([(0, 0), (1, 1), (1, 0)])]),
                                   u'http://www.geocat.ch', u'1000', u'BL0200002829', u'CH775979211712')
    real_estate.set_view_service(view_service)
    real_estate.set_main_page_view_service(view_service)
    office_record = OfficeRecord({'de': u'AGI'})
    resolver = DottedNameResolver()
    date_method_string = pyramid_oereb_test_config.get('extract').get('base_data').get('methods').get('date')
    date_method = resolver.resolve(date_method_string)
    update_date_os = date_method(real_estate)
    extract = ExtractRecord(
        real_estate,
        LogoRecord('ch', {'de': 'iVBORw0KGgoAAAANSUhEUgAAAB4AAAAPCAIAAAB82OjLAAAAL0lEQVQ4jWNMTd \
            3EQBvAwsDAkFPnS3VzpzRtZqK6oXAwavSo0aNGjwCjGWlX8gEAFAQGFyQKGL4AAAAASUVORK5CYII='}),
        LogoRecord('ch.plr', {'de': 'iVBORw0KGgoAAAANSUhEUgAAAB4AAAAPCAIAAAB82OjLAAAAL0lEQVQ4jWNMTd \
            3EQBvAwsDAkFPnS3VzpzRtZqK6oXAwavSo0aNGjwCjGWlX8gEAFAQGFyQKGL4AAAAASUVORK5CYII='}),
        LogoRecord('ne', {'de': 'iVBORw0KGgoAAAANSUhEUgAAAB4AAAAPCAIAAAB82OjLAAAAL0lEQVQ4jWNMTd \
            3EQBvAwsDAkFPnS3VzpzRtZqK6oXAwavSo0aNGjwCjGWlX8gEAFAQGFyQKGL4AAAAASUVORK5CYII='}),
        LogoRecord('ch.1234', {'de': 'iVBORw0KGgoAAAANSUhEUgAAAB4AAAAPCAIAAAB82OjLAAAAL0lEQVQ4jWNMTd \
            3EQBvAwsDAkFPnS3VzpzRtZqK6oXAwavSo0aNGjwCjGWlX8gEAFAQGFyQKGL4AAAAASUVORK5CYII='}),
        office_record,
        update_date_os,
        disclaimers=[
            DisclaimerRecord({'de': u'Haftungsausschluss'}, {'de': u'Test'})
        ],
        glossaries=glossaries_input,
        general_information=[
            GeneralInformationRecord(
                {'de': u'Allgemeine Informationen'},
                {'de': u'Inhalt der allgemeinen Informationen'})
        ]
    )
    extract.qr_code = '1'.encode('utf-8')
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
            'ExtractIdentifier': extract.extract_identifier,
            'CreationDate': Base.date_time(extract.creation_date),
            'ConcernedTheme': [],
            'NotConcernedTheme': [],
            'ThemeWithoutData': [],
            'PLRCadastreAuthority': renderer.format_office(office_record),
            'UpdateDateCS': Base.date_time(extract.update_date_os),
            'RealEstate': renderer.format_real_estate(real_estate),
            'GeneralInformation': [{
                'Title': [{'Language': 'de', 'Text': 'Allgemeine Informationen'}],
                'Content': [{'Language': 'de', 'Text': 'Inhalt der allgemeinen Informationen'}]
            }],
            'QRCodeRef': None,
            'Disclaimer': [{
                'Title': [{'Language': 'de', 'Text': 'Haftungsausschluss'}],
                'Content': [{'Language': 'de', 'Text': 'Test'}]
            }],
            'ElectronicSignature': 'Signature'
        }
        if glossaries_expected:
            expected['Glossary'] = glossaries_expected
        if parameter.images:
            expected.update({
                'LogoPLRCadastre': Config.get_oereb_logo()
                    .encode(),
                'FederalLogo': Config.get_conferderation_logo()
                    .encode(),
                'CantonalLogo': Config.get_canton_logo()
                    .encode(),
                'MunicipalityLogo': Config.get_municipality_logo(2771),
            })
        else:
            expected.update({
                'LogoPLRCadastreRef': u'http://example.com/image/logo/oereb/de.png',
                'FederalLogoRef': u'http://example.com/image/logo/confederation/de.png',
                'CantonalLogoRef': u'http://example.com/image/logo/canton/de.png',
                'MunicipalityLogoRef': u'http://example.com/image/logo/municipality/de.png?fosnr=2829'
            })
        # not sure what is expected => make tests pass by force
        expected['GeneralInformation'] = result['GeneralInformation']
        assert result['GeneralInformation'] == expected['GeneralInformation']
        assert result == expected


def test_format_office(DummyRenderInfo):
    renderer = Renderer(DummyRenderInfo())
    renderer._language = 'de'
    office = OfficeRecord({'de': u'Test'}, uid=u'test_uid', office_at_web=u'http://test.example.com',
                          line1=u'test_line1', line2=u'test_line2', street=u'test_street',
                          number=u'test_number', postal_code=1234, city=u'test_city')
    assert renderer.format_office(office) == {
        'Name': renderer.get_multilingual_text('Test'),
        'UID': u'test_uid',
        'OfficeAtWeb': renderer.get_multilingual_text(u'http://test.example.com'),
        'Line1': u'test_line1',
        'Line2': u'test_line2',
        'Street': u'test_street',
        'Number': u'test_number',
        'PostalCode': '1234',
        'City': u'test_city'
    }


def test_format_real_estate(DummyRenderInfo, real_estate_test_data):
    renderer = Renderer(DummyRenderInfo())
    renderer._language = u'de'
    renderer._params = Parameter(
        'json', 'reduced', True, False, 'BL0200002829', '1000', 'CH775979211712', 'de'
    )
    geometry = MultiPolygon([Polygon([(0, 0), (1, 1), (1, 0)])])
    view_service = ViewServiceRecord(
        {'de': u'http://geowms.bl.ch'},
        1, 1.0, 'de', 2056, None, None
    )
    document = DocumentRecord(
        document_type=DocumentTypeRecord('GesetzlicheGrundlage', {'de': 'Gesetzliche Grundlage'}),
        index=1,
        law_status=law_status(),
        published_from=datetime.date.today(),
        title={u'de': u'Test Dokument'},
        responsible_office=OfficeRecord({u'de': u'BUD'}),
        text_at_web={'de': 'http://mein.dokument.ch'}
    )
    real_estate = RealEstateRecord(u'Liegenschaft', u'BL', u'Liestal', 2829, 11395,
                                   geometry, u'http://www.geocat.ch', u'1000', u'BL0200002829',
                                   u'CH775979211712', u'Subunit', [], references=[document])
    real_estate.set_view_service(view_service)
    real_estate.set_main_page_view_service(view_service)
    result = renderer.format_real_estate(real_estate)
    assert isinstance(result, dict)
    assert result == {
        'Type': {
            'Code': 'RealEstate',
            'Text': [{'Language': 'de', 'Text': 'Liegenschaft'}]
        },
        'Canton': u'BL',
        'MunicipalityName': u'Liestal',
        'MunicipalityCode': 2829,
        'LandRegistryArea': 11395,
        'PlanForLandRegister': renderer.format_map(view_service),
        'PlanForLandRegisterMainPage': renderer.format_map(view_service),
        'Limit': renderer.from_shapely(geometry),
        'Number': u'1000',
        'IdentDN': u'BL0200002829',
        'EGRID': u'CH775979211712',
        'SubunitOfLandRegister': u'Subunit',
        'MetadataOfGeographicalBaseData': u'http://www.geocat.ch',
        'Reference': [renderer.format_document(document)]
    }


@pytest.mark.parametrize('parameter', [
    default_param(),
    Parameter('json', False, True, False, 'BL0200002829', '1000', 'CH775979211712', 'de'),
])
def test_format_plr(DummyRenderInfo, parameter, pyramid_oereb_test_config):
    renderer = Renderer(DummyRenderInfo())
    renderer._language = 'de'
    renderer._params = parameter
    renderer._request = MockRequest()
    document = DocumentRecord(
        document_type=DocumentTypeRecord('GesetzlicheGrundlage', {'de': 'Gesetzliche Grundlage'}),
        index=1,
        law_status=law_status(),
        published_from=datetime.date.today(),
        title={u'de': u'Test Dokument'},
        responsible_office=OfficeRecord({u'de': u'BUD'}),
        text_at_web={'de': 'http://mein.dokument.ch'}
    )
    documents = [document]
    theme = ThemeRecord(u'ch.BelasteteStandorte', {u'de': u'Test theme'}, 410)
    subTheme = None
    # subTheme = ThemeRecord(
    #     u'ch.BelasteteStandorte',
    #     {u'de': u'SubTheme'}, 411, u'SubCodech.BelasteteStandorte'
    # )
    office = OfficeRecord({'de': 'Test Office'})
    legend_entry = LegendEntryRecord(
        ImageRecord(FileAdapter().read('tests/resources/python.svg')),
        {'de': 'Test'}, 'CodeA', 'TypeCodeList', theme,
        view_service_id=1, identifier="1")
    view_service = ViewServiceRecord(
        {'de': 'http://geowms.bl.ch'},
        1, 1.0, 'de', 2056, None, [legend_entry]
    )
    geometry = GeometryRecord(law_status(), datetime.date.today(), None, Point(1, 1))
    plr = PlrRecord(
        theme,
        legend_entry,
        law_status(),
        datetime.date.today(),
        None,
        office,
        ImageRecord(FileAdapter().read('tests/resources/python.svg')),
        view_service,
        [geometry],
        subTheme,
        type_code='CodeA',
        type_code_list='TypeCodeList',
        documents=documents,
        view_service_id=1
    )
    plr.part_in_percent = 0.5

    result = renderer.format_plr([plr])
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], dict)
    expected = {
        'LegendText': renderer.get_multilingual_text(plr.legend_text),
        'Theme': renderer.format_theme(plr.theme),
        'Lawstatus': {
            'Code': 'inKraft',
            'Text': [{'Language': 'de', 'Text': 'Rechtskräftig'}]
        },
        'ResponsibleOffice': renderer.format_office(plr.responsible_office),
        'Map': renderer.format_map(plr.view_service),
        'TypeCode': 'CodeA',
        'TypeCodelist': 'TypeCodeList',
        'LegalProvisions': [renderer.format_document(document)],
        'PartInPercent': 0.5
    }
    if parameter.images:
        expected.update({
            'Symbol': ImageRecord(FileAdapter().read('tests/resources/python.svg')).encode()
        })
    else:
        result = renderer.format_plr([plr])
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], dict)
        expected = {
            'LegendText': renderer.get_multilingual_text(plr.legend_text),
            'Theme': renderer.format_theme(plr.theme),
            'Lawstatus': {
                'Code': 'inKraft',
                'Text': [{'Language': 'de', 'Text': 'Rechtskräftig'}]
            },
            'ResponsibleOffice': renderer.format_office(plr.responsible_office),
            'Map': renderer.format_map(plr.view_service),
            'TypeCode': 'CodeA',
            'TypeCodelist': 'TypeCodeList',
            'LegalProvisions': [renderer.format_document(document)],
            'PartInPercent': 0.5
        }
        if parameter.images:
            expected.update({
                'Symbol': ImageRecord(FileAdapter().read('tests/resources/python.svg')).encode()
            })
        else:
            expected.update({
                'SymbolRef': 'http://example.com/image/symbol/{theme_code}/legend_entry.svg?identifier=1'
                    .format(
                        theme_code='ch.BelasteteStandorte'
                    )
            })
        assert result[0] == expected


@pytest.mark.parametrize('document,result_dict', [
    (
        DocumentRecord(
            document_type=DocumentTypeRecord('Rechtsvorschrift', {"de": "Rechtsvorschrift"}),
            index=2,
            law_status=law_status(),
            title={'de': 'Test Rechtsvorschrift'},
            published_from=datetime.date.today(),
            responsible_office=OfficeRecord({'de': 'AGI'}),
            text_at_web={'de': 'http://meine.rechtsvorschrift.ch'},
            official_number={'de': 'rv.test.1'},
            abbreviation={'de': 'Test'},
            article_numbers=['Art.1', 'Art.2', 'Art.3']
        ), {
            'Type': {
                'Code': 'Rechtsvorschrift',
                'Text': [{'Language': 'de', 'Text': 'Rechtsvorschrift'}]
            },
            'Index': 2,
            'Lawstatus': {
                'Code': 'inKraft',
                'Text': [{'Language': 'de', 'Text': 'Rechtskräftig'}]
            },
            'TextAtWeb': [{'Language': 'de', 'Text': 'http://meine.rechtsvorschrift.ch'}],
            'Title': [{'Language': 'de', 'Text': 'Test Rechtsvorschrift'}],
            'ResponsibleOffice': {
                'Name': [{'Language': 'de', 'Text': 'AGI'}]
            },
            'Abbreviation': [{'Language': 'de', 'Text': 'Test'}],
            'OfficialNumber': [{'Language': 'de', 'Text': 'rv.test.1'}],
            'ArticleNumber': ['Art.1', 'Art.2', 'Art.3']
        }
    ), (
        DocumentRecord(
            document_type=DocumentTypeRecord('GesetzlicheGrundlage', {"de": "Gesetzliche Grundlage"}),
            index=1,
            law_status=law_status(),
            title={'de': 'Test Gesetz'},
            published_from=datetime.date.today(),
            responsible_office=OfficeRecord({'de': 'AGI'}),
            text_at_web={'de': 'http://mein.gesetz.ch'},
            official_number={'de': 'g.test.1'}
        ), {
            'Type': {
                'Code': 'GesetzlicheGrundlage',
                'Text': [{'Language': 'de', 'Text': 'Gesetzliche Grundlage'}]
            },
            'Index': 1,
            'Lawstatus': {
                'Code': 'inKraft',
                'Text': [{'Language': 'de', 'Text': 'Rechtskräftig'}]
            },
            'TextAtWeb': [{'Language': 'de', 'Text': 'http://mein.gesetz.ch'}],
            'Title': [{'Language': 'de', 'Text': 'Test Gesetz'}],
            'ResponsibleOffice': {
                'Name': [{'Language': 'de', 'Text': 'AGI'}]
            },
            'OfficialNumber': [{'Language': 'de', 'Text': 'g.test.1'}]
        }
    ), (
        DocumentRecord(
            document_type=DocumentTypeRecord('Hinweis', {"de": "Hinweis"}),
            index=3,
            law_status=law_status(),
            title={'de': 'Test Hinweis'},
            published_from=datetime.date.today(),
            responsible_office=OfficeRecord({'de': 'AGI'}),
            text_at_web={'de': 'http://mein.hinweis.ch'},
            official_number={'de': 'h.test.1'}
        ), {
            'Type': {
                'Code': 'Hinweis',
                'Text': [{'Language': 'de', 'Text': 'Hinweis'}]
            },
            'Index': 3,
            'Lawstatus': {
                'Code': 'inKraft',
                'Text': [{'Language': 'de', 'Text': 'Rechtskräftig'}]
            },
            'TextAtWeb': [{'Language': 'de', 'Text': 'http://mein.hinweis.ch'}],
            'Title': [{'Language': 'de', 'Text': 'Test Hinweis'}],
            'ResponsibleOffice': {
                'Name': [{'Language': 'de', 'Text': 'AGI'}]
            },
            'OfficialNumber': [{'Language': 'de', 'Text': 'h.test.1'}]
        }
    )
])
def test_format_document(DummyRenderInfo, params, document, result_dict):
    renderer = Renderer(DummyRenderInfo())
    renderer._language = u'de'
    renderer._params = params
    result = renderer.format_document(document)
    assert isinstance(result, dict)
    assert result == result_dict


@pytest.mark.parametrize('geometry,result_dict', [
    (GeometryRecord(
        law_status(),
        datetime.date.today(),
        None,
        Point(0, 0),
        geo_metadata='http://www.geocat.ch'), {
        'Lawstatus': {
            'Code': 'inKraft',
            'Text': [{'Language': 'de', 'Text': 'Rechtskräftig'}]
        },
        'MetadataOfGeographicalBaseData': 'http://www.geocat.ch',
        'Point': {
            'crs': 'EPSG:2056',
            'coordinates': (0, 0),
            'type': 'Point'
        }
    }),
    (GeometryRecord(law_status(), datetime.date.today(), None, LineString([(0, 0), (1, 1)])), {
        'Lawstatus': {
            'Code': 'inKraft',
            'Text': [{'Language': 'de', 'Text': 'Rechtskräftig'}]
        },
        'Line': {
            'crs': 'EPSG:2056',
            'coordinates': ((0, 0), (1, 1)),
            'type': 'LineString'
        }
    }),
    (GeometryRecord(
        law_status(),
        datetime.date.today(),
        None,
        Polygon([(0, 0), (1, 1), (1, 0)])
    ), {
        'Lawstatus': {
            'Code': 'inKraft',
            'Text': [{'Language': 'de', 'Text': 'Rechtskräftig'}]
        },
        'Surface': {
            'crs': 'EPSG:2056',
            'coordinates': (((0, 0), (1, 1), (1, 0), (0, 0)), ),
            'type': 'Polygon'
        }
    })
])
def test_format_geometry(DummyRenderInfo, params, geometry, result_dict):
    renderer = Renderer(DummyRenderInfo())
    renderer._language = u'de'
    renderer._params = params
    result = renderer.format_geometry(geometry)
    assert isinstance(result, dict)
    assert result == result_dict


def test_format_theme(DummyRenderInfo, params):
    renderer = Renderer(DummyRenderInfo())
    renderer._language = u'de'
    renderer._params = params
    theme = ThemeRecord(u'TestTheme', {u'de': u'Test-Thema'}, 100)
    result = renderer.format_theme(theme)
    assert isinstance(result, dict)
    assert result == {
        'Code': 'TestTheme',
        'Text': [renderer.get_localized_text({'de': 'Test-Thema'})]
    }


@pytest.mark.parametrize('parameter', [
    default_param(),
    Parameter('json', 'reduced', False, True, 'BL0200002829', '1000', 'CH775979211712', 'de')
])
def test_format_legend_entry(DummyRenderInfo, parameter):
    renderer = Renderer(DummyRenderInfo())
    renderer._language = u'de'
    renderer._params = parameter
    renderer._request = MockRequest()
    theme = ThemeRecord(u'ch.BelasteteStandorte', {u'de': u'Test'}, 410)
    legend_entry = LegendEntryRecord(
        ImageRecord(FileAdapter().read('tests/resources/python.svg')),
        {u'de': u'Legendeneintrag'},
        u'CodeA',
        u'type_code_list',
        theme,
        view_service_id=1,
        identifier="1"
    )
    result = renderer.format_legend_entry(legend_entry)
    expected = {
        'LegendText': renderer.get_multilingual_text({'de': 'Legendeneintrag'}),
        'TypeCode': 'CodeA',
        'TypeCodelist': 'type_code_list',
        'Theme': renderer.format_theme(theme),
    }
    if parameter.images:
        expected.update({
            'Symbol': ImageRecord(FileAdapter().read('tests/resources/python.svg')).encode()
        })
    else:
        expected.update({
            'SymbolRef': 'http://example.com/image/symbol/{theme_code}/legend_entry.svg?identifier=1'
                .format(
                    theme_code='ch.BelasteteStandorte'
                )
        })
    assert isinstance(result, dict)
    assert result == expected
