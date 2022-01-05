# -*- coding: utf-8 -*-
import os
import json
import codecs
import pytest
import responses
from tests.mockrequest import MockRequest
from unittest.mock import patch
import pyramid_oereb
from pyramid_oereb.core.config import Config
from pyramid_oereb.core.records.real_estate_type import RealEstateTypeRecord
from pyramid_oereb.core.records.logo import LogoRecord
from pyramid_oereb.core.records.theme import ThemeRecord
from pyramid_oereb.contrib.print_proxy.mapfish_print.mapfish_print import Renderer
from pyramid_oereb.contrib.print_proxy.mapfish_print.toc_pages import TocPages
from pyramid_oereb.core.views.webservice import PlrWebservice


@pytest.fixture
def coordinates():
    yield [[[
        [2615122.772, 1266688.951], [2615119.443, 1266687.783], [2615116.098, 1266686.662],
        [2615112.738, 1266685.586], [2615109.363, 1266684.556], [2615105.975, 1266683.573],
        [2615102.573, 1266682.637], [2615098.859, 1266681.622], [2615095.13, 1266680.663],
        [2615122.772, 1266688.951]
    ]]]


@pytest.fixture
def extract():
    with codecs.open(
            'tests/contrib.print_proxy.mapfish_print/resources/test_extract.json'
    ) as f:
        yield json.load(f)


@pytest.fixture
def expected_printable_extract():
    with codecs.open(
            'tests/contrib.print_proxy.mapfish_print/resources/expected_getspec_extract.json'
    ) as f:
        yield json.load(f)


@pytest.fixture
@pytest.mark.usefixtures('coordinates')
def geometry(coordinates):
    yield {
        'type': 'MultiPolygon',
        'coordinates': coordinates
    }


def test_toc_pages(extract):
    assert TocPages(extract).getNbPages() == 1


def getSameEntryInList(reference, objects):
    sameObject = None

    # List are not supported
    if isinstance(reference, list):
        for obj in objects:
            if reference == obj:
                return obj

    # Dict reference
    elif isinstance(reference, dict):
        for obj in objects:
            if isinstance(obj, dict):
                sameObject = obj
                for key in reference:
                    if key not in obj or not deepCompare(reference[key], obj[key], False):
                        sameObject = None
                        break
            if sameObject is not None:
                return sameObject

    # Naked value reference
    else:
        for obj in objects:
            if obj == reference:
                return obj

    return None


def deepCompare(value, valueToCompare, verbose=True):
    match = True
    # Go inside dict to compare values inside
    if isinstance(value, dict):
        if not isinstance(valueToCompare, dict):
            match = False
        else:
            for key in value:
                if not deepCompare(value[key], valueToCompare[key]):
                    match = False
                    break

    # Go inside list to compare values inside
    elif isinstance(value, list):
        if not isinstance(valueToCompare, list):
            match = False
        else:
            for index, element in enumerate(value):
                entry = value[index]
                # Index can change try to find the same entry
                matchEntry = getSameEntryInList(entry, valueToCompare)
                if not deepCompare(entry, matchEntry):
                    match = False
                    break

    # Compare values
    elif value != valueToCompare:
        match = False

    if not match and verbose and valueToCompare is not None:
        print(u"Error with value {} expected {}".format(value, valueToCompare))
    return match


def test_legend(pyramid_oereb_test_config, extract, geometry, DummyRenderInfo):
    renderer = Renderer(DummyRenderInfo)
    renderer.convert_to_printable_extract(extract, geometry)
    first_plr = extract.get('RealEstate_RestrictionOnLandownership')[0]
    assert isinstance(first_plr, dict)


def test_mapfish_print_entire_extract(extract, geometry, expected_printable_extract, DummyRenderInfo):
    renderer = Renderer(DummyRenderInfo())
    renderer.convert_to_printable_extract(extract, geometry)
    # Uncomment to print the result
    # with open('./printable_extract.json', 'w') as f:
    #     json.dump(extract, f, indent=2, ensure_ascii=False)

    assert extract == expected_printable_extract
    assert deepCompare(extract, expected_printable_extract)
    # Do it twice, to test all keys in each reports
    assert deepCompare(expected_printable_extract, extract)


def test_get_sorted_legend(DummyRenderInfo):
    renderer = Renderer(DummyRenderInfo())
    test_legend_list = [
        {
            'TypeCode': u'StaoTyp2',
            'Geom_Type': u'AreaShare',
            'TypeCodelist': '',
            'AreaShare': 11432,
            'PartInPercent': 32.6,
            'SymbolRef': u'http://localhost:6543/oereb/image/symbol/\
                        ch.BelasteteStandorteOeffentlicherVerkehr/1/StaoTyp2',
            'LegendText': u'Belastet, untersuchungsbedürftig'
        }, {
            'TypeCode': u'StaoTyp3',
            'Geom_Type': u'LengthShare',
            'TypeCodelist': '',
            'LengthShare': 164,
            'SymbolRef': u'http://localhost:6543/oereb/image/symbol/\
                        ch.BelasteteStandorteOeffentlicherVerkehr/1/StaoTyp3',
            'LegendText': u'Belastet, überwachungsbedürftig'
        }, {
            'TypeCode': u'StaoTyp1',
            'Geom_Type': u'NrOfPoints',
            'TypeCodelist': '',
            'NrOfPoints': 2,
            'SymbolRef': u'http://localhost:6543/oereb/image/symbol/\
                        ch.BelasteteStandorteOeffentlicherVerkehr/1/StaoTyp1',
            'LegendText': u'Belastet, keine schädlichen oder lästigen Einwirkungen zu erwarten'
        }, {
            'TypeCode': u'StaoTyp3',
            'Geom_Type': u'LengthShare',
            'TypeCodelist': '',
            'LengthShare': 2000,
            'SymbolRef': u'http://localhost:6543/oereb/image/symbol/\
                        ch.BelasteteStandorteOeffentlicherVerkehr/1/StaoTyp3',
            'LegendText': u'Belastet, untersuchungsbedürftig'
        }, {
            'TypeCode': u'StaoTyp2',
            'Geom_Type': u'AreaShare',
            'TypeCodelist': '',
            'AreaShare': 114,
            'PartInPercent': 32.6,
            'SymbolRef': u'http://localhost:6543/oereb/image/symbol/\
                        ch.BelasteteStandorteOeffentlicherVerkehr/1/StaoTyp2',
            'LegendText': u'Belastet, untersuchungsbedürftig'
        }
    ]
    sorted_list = renderer.sort_dict_list(test_legend_list, renderer.sort_legend_elem)
    expected_result = [
        {
            'TypeCode': u'StaoTyp2',
            'Geom_Type': u'AreaShare',
            'TypeCodelist': '',
            'AreaShare': 11432,
            'PartInPercent': 32.6,
            'SymbolRef': u'http://localhost:6543/oereb/image/symbol/\
                        ch.BelasteteStandorteOeffentlicherVerkehr/1/StaoTyp2',
            'LegendText': u'Belastet, untersuchungsbedürftig'
        }, {
            'TypeCode': u'StaoTyp2',
            'Geom_Type': u'AreaShare',
            'TypeCodelist': '',
            'AreaShare': 114,
            'PartInPercent': 32.6,
            'SymbolRef': u'http://localhost:6543/oereb/image/symbol/\
                        ch.BelasteteStandorteOeffentlicherVerkehr/1/StaoTyp2',
            'LegendText': u'Belastet, untersuchungsbedürftig'
        }, {
            'TypeCode': u'StaoTyp3',
            'Geom_Type': u'LengthShare',
            'TypeCodelist': '',
            'LengthShare': 2000,
            'SymbolRef': u'http://localhost:6543/oereb/image/symbol/\
                        ch.BelasteteStandorteOeffentlicherVerkehr/1/StaoTyp3',
            'LegendText': u'Belastet, untersuchungsbedürftig'
        }, {
            'TypeCode': u'StaoTyp3',
            'Geom_Type': u'LengthShare',
            'TypeCodelist': '',
            'LengthShare': 164,
            'SymbolRef': u'http://localhost:6543/oereb/image/symbol/\
                        ch.BelasteteStandorteOeffentlicherVerkehr/1/StaoTyp3',
            'LegendText': u'Belastet, überwachungsbedürftig'
        }, {
            'TypeCode': u'StaoTyp1',
            'Geom_Type': u'NrOfPoints',
            'TypeCodelist': '',
            'NrOfPoints': 2,
            'SymbolRef': u'http://localhost:6543/oereb/image/symbol/\
                        ch.BelasteteStandorteOeffentlicherVerkehr/1/StaoTyp1',
            'LegendText': u'Belastet, keine schädlichen oder lästigen Einwirkungen zu erwarten'
        }
    ]
    assert sorted_list == expected_result


def test_get_sorted_legal_provisions(DummyRenderInfo):
    renderer = Renderer(DummyRenderInfo())
    expected_result = [
        {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inKraft",
            "Lawstatus_Text": "Rechtskräftig",
            "OfficialNumber": "3891.100",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/197"}],
            "Title": "Baugesetz"
        }, {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inKraft",
            "Lawstatus_Text": "Rechtskräftig",
            "OfficialNumber": "3891.100",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/198"}],
            "Title": "Baugesetz"
        }, {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inKraft",
            "Lawstatus_Text": "Rechtskräftig",
            "OfficialNumber": "07.447",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/214"}],
            "Title": "Revision Ortsplanung"
        }, {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inKraft",
            "Lawstatus_Text": "Rechtskräftig",
            "OfficialNumber": "07.447",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/213"}],
            "Title": "Revision Ortsplanung"
        }
    ]
    test_legal_provisions = [
        {
           "Canton": "BL",
           "DocumentType": "LegalProvision",
           "Lawstatus_Code": "inKraft",
           "Lawstatus_Text": "Rechtskräftig",
           "OfficialNumber": "07.447",
           "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
           "ResponsibleOffice_OfficeAtWeb": "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
           "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/214"}],
           "Title": "Revision Ortsplanung"
        }, {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inKraft",
            "Lawstatus_Text": "Rechtskräftig",
            "OfficialNumber": "3891.100",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/197"}],
            "Title": "Baugesetz"
        }, {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inKraft",
            "Lawstatus_Text": "Rechtskräftig",
            "OfficialNumber": "07.447",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/213"}],
            "Title": "Revision Ortsplanung"
        }, {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inKraft",
            "Lawstatus_Text": "Rechtskräftig",
            "OfficialNumber": "3891.100",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/198"}],
            "Title": "Baugesetz"
        }
    ]
    assert expected_result == renderer.sort_dict_list(test_legal_provisions, renderer.sort_legal_provision)


def test_get_sorted_hints(DummyRenderInfo):
    renderer = Renderer(DummyRenderInfo())
    test_hints = [{
        "Canton": "BL",
        "DocumentType": "Hint",
        "Lawstatus_Code": "inKraft",
        "Lawstatus_Text": "Rechtskräftig",
        "OfficialNumber": "3891.100",
        "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
        "ResponsibleOffice_OfficeAtWeb": "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
        "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/197"}],
        "Title": "Revision Ortsplanung"
    }, {
        "Canton": "BL",
        "DocumentType": "Hint",
        "Lawstatus_Code": "inKraft",
        "Lawstatus_Text": "Rechtskräftig",
        "index": 1,
        "OfficialNumber": "3891.100",
        "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
        "ResponsibleOffice_OfficeAtWeb": "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
        "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/198"}],
    }, {
        "Canton": "BL",
        "DocumentType": "Hint",
        "Lawstatus_Code": "inKraft",
        "Lawstatus_Text": "Rechtskräftig",
        "index": 2,
        "OfficialNumber": "3891.100",
        "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
        "ResponsibleOffice_OfficeAtWeb": "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
        "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/198"}],
        "Title": "Baugesetz"

    }]

    expected_result = [{
        "Canton": "BL",
        "DocumentType": "Hint",
        "Lawstatus_Code": "inKraft",
        "Lawstatus_Text": "Rechtskräftig",
        "index": 1,
        "OfficialNumber": "3891.100",
        "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
        "ResponsibleOffice_OfficeAtWeb": "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
        "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/198"}],
    }, {
        "Canton": "BL",
        "DocumentType": "Hint",
        "Lawstatus_Code": "inKraft",
        "Lawstatus_Text": "Rechtskräftig",
        "index": 2,
        "OfficialNumber": "3891.100",
        "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
        "ResponsibleOffice_OfficeAtWeb": "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
        "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/198"}],
        "Title": "Baugesetz"
    }, {
        "Canton": "BL",
        "DocumentType": "Hint",
        "Lawstatus_Code": "inKraft",
        "Lawstatus_Text": "Rechtskräftig",
        "OfficialNumber": "3891.100",
        "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
        "ResponsibleOffice_OfficeAtWeb": "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
        "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/197"}],
        "Title": "Revision Ortsplanung"
    }]

    assert expected_result == renderer.sort_dict_list(test_hints, renderer.sort_hints_laws)


def test_get_sorted_law(DummyRenderInfo):
    renderer = Renderer(DummyRenderInfo())
    test_law = [
        {
            'DocumentType': 'Law',
            'TextAtWeb': [{'URL': 'http://www.admin.ch/ch/d/sr/c814_01.html'}],
            'Title': 'Raumplanungsverordnung für den Kanton Graubünden',
            'Abbreviation': 'KRVO',
            'OfficialNumber': 'BR 801.110',
            'index': 5,
            'Canton': 'GR',
            'Lawstatus_Code': 'inKraft',
            'Lawstatus_Text': 'Rechtskräftig',
            'ResponsibleOffice_Name': u'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb':
                'https://www.gr-lex.gr.ch/frontend/versions/pdf_file_with_annex/2934?locale=de'
        }, {
            'DocumentType': u'Law',
            'TextAtWeb': [{'URL': u'http://www.admin.ch/ch/d/sr/c814_680.html'}],
            'Title': u'Raumplanungsgesetz für den Kanton Graubünden',
            'Abbreviation': u'KRG',
            'index': 3,
            'Canton': u'GR',
            'Lawstatus_Code': u'inKraft',
            'Lawstatus_Text': u'Rechtskräftig',
            'ResponsibleOffice_Name': u'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb':
                u'https://www.gr-lex.gr.ch/frontend/versions/pdf_file_with_annex/2936?locale=de'
        }, {
            'DocumentType': u'Law',
            'TextAtWeb': [{'URL': u'http://www.admin.ch/ch/d/sr/c814_680.html'}],
            'Title': u'Raumplanungsgesetz für den Kanton Graubünden2',
            'Abbreviation': u'KRG',
            'OfficialNumber': u'BR 801.100',
            'index': 1,
            'Canton': u'GR',
            'Lawstatus_Code': u'inKraft',
            'Lawstatus_Text': u'Rechtskräftig',
            'ResponsibleOffice_Name': u'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb':
                u'https://www.gr-lex.gr.ch/frontend/versions/pdf_file_with_annex/2936?locale=de'
        }, {
            'DocumentType': 'Law',
            'TextAtWeb': [{'URL': u'http://www.admin.ch/ch/d/sr/c814_680.html'}],
            'Title': 'Bundesgesetz über die Raumplanung',
            'Abbreviation': 'RPG',
            'OfficialNumber': 'SR 700',
            'index': 4,
            'Canton': 'GR',
            'Lawstatus_Code': 'inKraft',
            'Lawstatus_Text': 'Rechtskräftig',
            'ResponsibleOffice_Name': u'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb': 'http://www.lexfind.ch/dtah/167348/2'
        }, {
            'DocumentType': u'Law',
            'TextAtWeb': [{'URL': u'http://www.admin.ch/ch/d/sr/c814_680.html'}],
            'Title': u'Raumplanungsgesetz für den Kanton Graubünden',
            'Abbreviation': u'KRG',
            'OfficialNumber': u'BR 801.100',
            'index': 2,
            'Canton': u'GR',
            'Lawstatus_Code': u'inKraft',
            'Lawstatus_Text': u'Rechtskräftig',
            'ResponsibleOffice_Name': u'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb':
                u'https://www.gr-lex.gr.ch/frontend/versions/pdf_file_with_annex/2936?locale=de'
        }
    ]

    expected_result = [
        {
            'DocumentType': u'Law',
            'TextAtWeb': [{'URL': u'http://www.admin.ch/ch/d/sr/c814_680.html'}],
            'Title': u'Raumplanungsgesetz für den Kanton Graubünden2',
            'Abbreviation': u'KRG',
            'OfficialNumber': u'BR 801.100',
            'index': 1,
            'Canton': u'GR',
            'Lawstatus_Code': u'inKraft',
            'Lawstatus_Text': u'Rechtskräftig',
            'ResponsibleOffice_Name': u'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb':
                u'https://www.gr-lex.gr.ch/frontend/versions/pdf_file_with_annex/2936?locale=de'
        }, {
            'DocumentType': u'Law',
            'TextAtWeb': [{'URL': u'http://www.admin.ch/ch/d/sr/c814_680.html'}],
            'Title': u'Raumplanungsgesetz für den Kanton Graubünden',
            'Abbreviation': u'KRG',
            'OfficialNumber': u'BR 801.100',
            'index': 2,
            'Canton': u'GR',
            'Lawstatus_Code': u'inKraft',
            'Lawstatus_Text': u'Rechtskräftig',
            'ResponsibleOffice_Name': u'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb':
                u'https://www.gr-lex.gr.ch/frontend/versions/pdf_file_with_annex/2936?locale=de'
        }, {
            'DocumentType': u'Law',
            'TextAtWeb': [{'URL': u'http://www.admin.ch/ch/d/sr/c814_680.html'}],
            'Title': u'Raumplanungsgesetz für den Kanton Graubünden',
            'Abbreviation': u'KRG',
            'index': 3,
            'Canton': u'GR',
            'Lawstatus_Code': u'inKraft',
            'Lawstatus_Text': u'Rechtskräftig',
            'ResponsibleOffice_Name': u'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb':
                u'https://www.gr-lex.gr.ch/frontend/versions/pdf_file_with_annex/2936?locale=de'
        }, {
            'DocumentType': 'Law',
            'TextAtWeb': [{'URL': u'http://www.admin.ch/ch/d/sr/c814_680.html'}],
            'Title': 'Bundesgesetz über die Raumplanung',
            'Abbreviation': 'RPG',
            'OfficialNumber': 'SR 700',
            'index': 4,
            'Canton': 'GR',
            'Lawstatus_Code': 'inKraft',
            'Lawstatus_Text': 'Rechtskräftig',
            'ResponsibleOffice_Name': u'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb': 'http://www.lexfind.ch/dtah/167348/2'
        }, {
            'DocumentType': 'Law',
            'TextAtWeb': [{'URL': 'http://www.admin.ch/ch/d/sr/c814_01.html'}],
            'Title': 'Raumplanungsverordnung für den Kanton Graubünden',
            'Abbreviation': 'KRVO',
            'OfficialNumber': 'BR 801.110',
            'index': 5,
            'Canton': 'GR',
            'Lawstatus_Code': 'inKraft',
            'Lawstatus_Text': 'Rechtskräftig',
            'ResponsibleOffice_Name': u'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb':
                'https://www.gr-lex.gr.ch/frontend/versions/pdf_file_with_annex/2934?locale=de'
        }
    ]
    assert expected_result == renderer.sort_dict_list(test_law, renderer.sort_hints_laws)


def test_group_legal_provisions(DummyRenderInfo):
    renderer = Renderer(DummyRenderInfo())
    test_legal_provisions = [
        {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inKraft",
            "Lawstatus_Text": "Rechtskräftig",
            "OfficialNumber": "3891.100",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/197"}],
            "Title": "Baugesetz"
        }, {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inKraft",
            "Lawstatus_Text": "Rechtskräftig",
            "OfficialNumber": "3891.100",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/198"}],
            "Title": "Baugesetz"
        }, {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inKraft",
            "Lawstatus_Text": "Rechtskräftig",
            "OfficialNumber": "07.447",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/213"}],
            "Title": "Revision Ortsplanung"
        }, {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inKraft",
            "Lawstatus_Text": "Rechtskräftig",
            "OfficialNumber": "07.447",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/214"}],
            "Title": "Revision Ortsplanung"
        }
    ]
    expected_results = [
        {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inKraft",
            "Lawstatus_Text": "Rechtskräftig",
            "OfficialNumber": "3891.100",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [
                {"URL": "https://oereb-gr-preview.000.ch/api/attachments/197"},
                {"URL": "https://oereb-gr-preview.000.ch/api/attachments/198"},
            ],
            "Title": "Baugesetz"
        }, {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inKraft",
            "Lawstatus_Text": "Rechtskräftig",
            "OfficialNumber": "07.447",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [
                {"URL": "https://oereb-gr-preview.000.ch/api/attachments/213"},
                {"URL": "https://oereb-gr-preview.000.ch/api/attachments/214"},
            ],
            "Title": "Revision Ortsplanung"
        }
    ]

    assert expected_results == renderer.group_legal_provisions(test_legal_provisions)


def test_archive_pdf(DummyRenderInfo):
    renderer = Renderer(DummyRenderInfo())
    extract = {'RealEstate_EGRID': 'CH113928077734'}
    path_and_filename = renderer.archive_pdf_file('/tmp', bytes(), extract)
    assert os.path.isfile(path_and_filename)


@pytest.fixture
def mock_responses(dummy_pdf):
    """
    Activate responses only if API is True.
    """
    rsps = responses.RequestsMock(assert_all_requests_are_fired=False)

    rsps.add(
        responses.POST,
        "http://oereb-print:8080/print/oereb/buildreport.pdf",
        body=dummy_pdf,
        # body=(  # minimal pdf file
        #     b"%PDF-1.0\n"
        #     b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 "
        #     b"obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 "
        #     b"obj<</Type/Page/MediaBox[0 0 3 3]>>endobj\n"
        #     b"xref\n"
        #     b"0 4\n"
        #     b"0000000000 65535 f\n"
        #     b"0000000010 00000 n\n"
        #     b"0000000053 00000 n\n"
        #     b"0000000102 00000 n\n"
        #     b"trailer<</Size 4/Root 1 0 R>>\n"
        #     b"startxref\n"
        #     b"149\n"
        #     b"%EOF"
        #     #
        #     b"%PDF-1.2 \n"
        #     b"9 0 obj\n<<\n>>\nstream\nBT/ 32 Tf(  DUMMY PDF   )' ET\nendstream\nendobj\n"
        #     b"4 0 obj\n<<\n/Type /Page\n/Parent 5 0 R\n/Contents 9 0 R\n>>\nendobj\n"
        #     b"5 0 obj\n<<\n/Kids [4 0 R ]\n/Count 1\n/Type /Pages\n/MediaBox [ 0 0 250 50 ]\n>>\nendobj\n"
        #     b"3 0 obj\n<<\n/Pages 5 0 R\n/Type /Catalog\n>>\nendobj\n"
        #     b"trailer\n<<\n/Root 3 0 R\n>>\n"
        #     b"%%EOF"
        # ),
        content_type="application/pdf",
        status=200,
    )

    with rsps:
        yield rsps


@pytest.fixture
def municipalities(pyramid_oereb_test_config, dbsession, transact):
    del transact

    from pyramid_oereb.contrib.data_sources.standard.models import main

    # Add dummy municipality
    municipalities = [main.Municipality(**{
        'fosnr': 1234,
        'name': u'Test',
        'published': True,
        'geom': 'SRID=2056;MULTIPOLYGON(((0 0, 0 10, 10 10, 10 0, 0 0)))'
    })]
    dbsession.add_all(municipalities)


@pytest.fixture
def address(pyramid_oereb_test_config, dbsession, transact):
    del transact

    from pyramid_oereb.contrib.data_sources.standard.models import main

    # Add dummy address
    addresses = [main.Address(**{
        'street_name': u'test',
        'street_number': u'10',
        'zip_code': 4410,
        'geom': 'SRID=2056;POINT(1 1)'
    })]
    dbsession.add_all(addresses)


@pytest.fixture
def real_estate_types_test_data(pyramid_oereb_test_config):
    with patch.object(Config, 'real_estate_types', [RealEstateTypeRecord(
            'Liegenschaft',
            {
                "de": "Liegenschaft",
                "fr": "Bien-fonds",
                "it": "Bene immobile",
                "rm": "Bain immobigliar",
                "en": "Property"
            }
    )]):
        yield pyramid_oereb_test_config


@pytest.fixture
def logos(pyramid_oereb_test_config):
    with patch.object(Config, 'logos', [
            LogoRecord('ch', {'de': 'iVBORw0KGgoAAAANSUhEUgAAAB4AAAAPCAIAAAB82OjLAAAAL0lEQVQ4jWNMTd3EQ \
            BvAwsDAkFPnS3VzpzRtZqK6oXAwavSo0aNGjwCjGWlX8gEAFAQGFyQKGL4AAAAASUVORK5CYII='}),
            LogoRecord('ch.plr', {'de': 'iVBORw0KGgoAAAANSUhEUgAAAB4AAAAPCAIAAAB82OjLAAAAL0lEQVQ4jWNMTd3EQ \
            BvAwsDAkFPnS3VzpzRtZqK6oXAwavSo0aNGjwCjGWlX8gEAFAQGFyQKGL4AAAAASUVORK5CYII='}),
            LogoRecord('ne', {'de': 'iVBORw0KGgoAAAANSUhEUgAAAB4AAAAPCAIAAAB82OjLAAAAL0lEQVQ4jWNMTd3EQ \
            BvAwsDAkFPnS3VzpzRtZqK6oXAwavSo0aNGjwCjGWlX8gEAFAQGFyQKGL4AAAAASUVORK5CYII='}),
            LogoRecord('ch.1234', {'de': 'iVBORw0KGgoAAAANSUhEUgAAAB4AAAAPCAIAAAB82OjLAAAAL0lEQVQ4jWNMTd3EQ \
            BvAwsDAkFPnS3VzpzRtZqK6oXAwavSo0aNGjwCjGWlX8gEAFAQGFyQKGL4AAAAASUVORK5CYII='}),
    ]):
        yield pyramid_oereb_test_config


@pytest.fixture
def themes(pyramid_oereb_test_config):
    with patch.object(Config, 'themes', [
            ThemeRecord(**{
                'code': 'ch.Nutzungsplanung',
                'sub_code': None,
                'title': {"de": "Nutzungsplanung (kantonal/kommunal)",
                          "fr": "Plans d’affectation (cantonaux/communaux)",
                          "it": "Piani di utilizzazione (cantonali/comunali)",
                          "rm": "Planisaziun d''utilisaziun (chantunal/communal)",
                          "en": "Land use plans (cantonal/municipal)"},
                'extract_index': 20
            }),
            ThemeRecord(**{
                'code': 'ch.StatischeWaldgrenzen',
                'title': {"de": "Statische Waldgrenzen",
                          "fr": "Limites forestières statiques",
                          "it": "Margini statici della foresta",
                          "rm": "Cunfins statics dal guaud",
                          "en": "Static forest perimeters"},
                'extract_index': 710
            }),
            ThemeRecord(**{
                'code': 'ch.ProjektierungszonenNationalstrassen',
                'title': {"de": "Projektierungszonen Nationalstrassen",
                          "fr": "Zones réservées des routes nationales",
                          "it": "Zone riservate per le strade nazionali",
                          "rm": "Zonas da projectaziun da las vias naziunalas",
                          "en": "Reserved zones for motorways"},
                'extract_index': 110
            }),
            ThemeRecord(**{
                'code': 'ch.BelasteteStandorte',
                'title': {"de": "Kataster der belasteten Standorte",
                          "fr": "Cadastre des sites pollués",
                          "it": "Catasto dei siti inquinati",
                          "rm": "Cataster dals lieus contaminads",
                          "en": "Cadastre of contaminated sites"},
                'extract_index': 410
            }),
    ]):
        yield pyramid_oereb_test_config


@pytest.fixture
def dummy_pdf():
    with open('./tests/contrib.print_proxy.mapfish_print/resources/dummy.pdf', 'rb') as f:
        return f.read()


@patch.object(pyramid_oereb.core.views.webservice, 'route_prefix', 'oereb')
@patch.object(pyramid_oereb.core.renderer.extract.json_, 'route_prefix', 'oereb')
def test_mfp_service(mock_responses, pyramid_test_config,
                     real_estate_data,
                     municipalities, themes, real_estate_types_test_data, logos,
                     general_information
                     ):
    request = MockRequest()
    request.matchdict.update({
        'format': 'PDF'
    })
    request.params.update({
        # 'GEOMETRY': 'true',
        'EGRID': 'TEST',
        # 'TOPICS': topics
    })
    from pyramid_oereb.core.config import Config
    pyramid_test_config.add_renderer('pyramid_oereb_extract_print',
                                     Config.get('print').get('renderer'))
    service = PlrWebservice(request)
    response = service.get_extract_by_id()
    assert response.status_code == 200
