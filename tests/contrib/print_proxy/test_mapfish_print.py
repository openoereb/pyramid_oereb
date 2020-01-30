# -*- coding: utf-8 -*-
import os
import json
import codecs
from pyramid_oereb.contrib.print_proxy.mapfish_print import Renderer
from tests.renderer import DummyRenderInfo
from pyramid_oereb.contrib.print_proxy.sub_themes.sorting import AlphabeticSort, ListSort
from pyramid_oereb.contrib.print_proxy.toc_pages import TocPages


def coordinates():
    return [[[
        [2615122.772, 1266688.951], [2615119.443, 1266687.783], [2615116.098, 1266686.662],
        [2615112.738, 1266685.586], [2615109.363, 1266684.556], [2615105.975, 1266683.573],
        [2615102.573, 1266682.637], [2615098.859, 1266681.622], [2615095.13, 1266680.663],
        [2615122.772, 1266688.951]
    ]]]


def extract():
    with codecs.open(
            'tests/contrib/print_proxy/resources/test_extract.json'
    ) as f:
        return json.loads(f.read())


def expected_printable_extract():
    with codecs.open(
            'tests/contrib/print_proxy/resources/expected_getspec_extract.json'
    ) as f:
        return json.loads(f.read())


def sub_theme_extract():
    with codecs.open(
            'tests/contrib/print_proxy/resources/sub_theme_test_extract.json'
    ) as f:
        return json.loads(f.read())


def sub_theme_expected_printable_extract():
    with codecs.open(
            'tests/contrib/print_proxy/resources/sub_theme_expected_getspec_extract.json'
    ) as f:
        return json.loads(f.read())


def test_toc_pages():
    assert TocPages(extract()).getNbPages() == 1


def geometry():
    return {
        'type': 'MultiPolygon',
        'coordinates': coordinates()
    }


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


def test_legend():
    renderer = Renderer(DummyRenderInfo())
    pdf_to_join = set()
    printable_extract = extract()
    renderer.convert_to_printable_extract(printable_extract, geometry(), pdf_to_join)
    first_plr = printable_extract.get('RealEstate_RestrictionOnLandownership')[0]
    assert isinstance(first_plr, dict)


def test_mapfish_print_entire_extract():
    renderer = Renderer(DummyRenderInfo())
    pdf_to_join = set()
    printable_extract = extract()
    renderer.convert_to_printable_extract(printable_extract, geometry(), pdf_to_join)
    # Uncomment to print the result
    # f = open('/tmp/printable_extract.json', 'w')
    # f.write(json.dumps(printable_extract))
    # f.close()

    expected = expected_printable_extract()
    assert deepCompare(printable_extract, expected)
    # Do it twice, to test all keys in each reports
    assert deepCompare(expected, printable_extract)


def test_split_restrictions_by_theme_code():
    test_data = [
               {
                   "Theme_Code": "ContaminatedPublicTransportSites",
                   "SubTheme": "SubTheme1"
               },
               {
                   "Theme_Code": "ContaminatedPublicTransportSites",
                   "SubTheme": "SubTheme2"
               },
               {
                   "Theme_Code": "ContaminatedPublicTransportSites",
                   "SubTheme": "SubTheme3"
               },
               {
                   "Theme_Code": "GroundwaterProtectionZones",
                   "SubTheme": "SubTheme1a"
               },
               {
                   "Theme_Code": "GroundwaterProtectionZones",
                   "SubTheme": "SubTheme2a"
               }
    ]

    expected_result = {
        "ContaminatedPublicTransportSites": [
            {
                "Theme_Code": "ContaminatedPublicTransportSites",
                "SubTheme": "SubTheme1"
            },
            {
                "Theme_Code": "ContaminatedPublicTransportSites",
                "SubTheme": "SubTheme2"
            },
            {
                "Theme_Code": "ContaminatedPublicTransportSites",
                "SubTheme": "SubTheme3"
            }
        ],
        "GroundwaterProtectionZones": [
            {
                "Theme_Code": "GroundwaterProtectionZones",
                "SubTheme": "SubTheme1a"
            },
            {
                "Theme_Code": "GroundwaterProtectionZones",
                "SubTheme": "SubTheme2a"
            }
        ]
    }

    splitted = Renderer._split_restrictions_by_theme_code(test_data)
    for theme in splitted:
        for index in range(len(splitted[theme])):
            assert splitted[theme][index]["Theme_Code"] == expected_result[theme][index]["Theme_Code"]
            assert splitted[theme][index]["SubTheme"] == expected_result[theme][index]["SubTheme"]


def test_load_sorter():
    module_name = "pyramid_oereb.contrib.print_proxy.sub_themes.sorting"
    class_alphabetic_sort = "AlphabeticSort"
    class_list_sort = "ListSort"
    alphabetic_sort = Renderer._load_sorter(module_name, class_alphabetic_sort)
    assert alphabetic_sort == AlphabeticSort
    list_sort = Renderer._load_sorter(module_name, class_list_sort)
    assert list_sort == ListSort


def test_get_sorted_legend():
    renderer = Renderer(DummyRenderInfo())
    test_legend_list = [
        {
            'TypeCode': u'StaoTyp2',
            'Geom_Type': u'AreaShare',
            'TypeCodelist': '',
            'AreaShare': 11432,
            'PartInPercent': 32.6,
            'SymbolRef': u'http://localhost:6543/oereb/image/symbol/\
                        ContaminatedPublicTransportSites/1/StaoTyp2',
            'Information': u'Belastet, untersuchungsbedürftig'
        }, {
            'TypeCode': u'StaoTyp3',
            'Geom_Type': u'LengthShare',
            'TypeCodelist': '',
            'LengthShare': 164,
            'SymbolRef': u'http://localhost:6543/oereb/image/symbol/\
                        ContaminatedPublicTransportSites/1/StaoTyp3',
            'Information': u'Belastet, überwachungsbedürftig'
        }, {
            'TypeCode': u'StaoTyp1',
            'Geom_Type': u'NrOfPoints',
            'TypeCodelist': '',
            'NrOfPoints': 2,
            'SymbolRef': u'http://localhost:6543/oereb/image/symbol/\
                        ContaminatedPublicTransportSites/1/StaoTyp1',
            'Information': u'Belastet, keine schädlichen oder lästigen Einwirkungen zu erwarten'
        }, {
            'TypeCode': u'StaoTyp3',
            'Geom_Type': u'LengthShare',
            'TypeCodelist': '',
            'LengthShare': 2000,
            'SymbolRef': u'http://localhost:6543/oereb/image/symbol/\
                        ContaminatedPublicTransportSites/1/StaoTyp3',
            'Information': u'Belastet, untersuchungsbedürftig'
        }, {
            'TypeCode': u'StaoTyp2',
            'Geom_Type': u'AreaShare',
            'TypeCodelist': '',
            'AreaShare': 114,
            'PartInPercent': 32.6,
            'SymbolRef': u'http://localhost:6543/oereb/image/symbol/\
                        ContaminatedPublicTransportSites/1/StaoTyp2',
            'Information': u'Belastet, untersuchungsbedürftig'
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
                        ContaminatedPublicTransportSites/1/StaoTyp2',
            'Information': u'Belastet, untersuchungsbedürftig'
        }, {
            'TypeCode': u'StaoTyp2',
            'Geom_Type': u'AreaShare',
            'TypeCodelist': '',
            'AreaShare': 114,
            'PartInPercent': 32.6,
            'SymbolRef': u'http://localhost:6543/oereb/image/symbol/\
                        ContaminatedPublicTransportSites/1/StaoTyp2',
            'Information': u'Belastet, untersuchungsbedürftig'
        }, {
            'TypeCode': u'StaoTyp3',
            'Geom_Type': u'LengthShare',
            'TypeCodelist': '',
            'LengthShare': 2000,
            'SymbolRef': u'http://localhost:6543/oereb/image/symbol/\
                        ContaminatedPublicTransportSites/1/StaoTyp3',
            'Information': u'Belastet, untersuchungsbedürftig'
        }, {
            'TypeCode': u'StaoTyp3',
            'Geom_Type': u'LengthShare',
            'TypeCodelist': '',
            'LengthShare': 164,
            'SymbolRef': u'http://localhost:6543/oereb/image/symbol/\
                        ContaminatedPublicTransportSites/1/StaoTyp3',
            'Information': u'Belastet, überwachungsbedürftig'
        }, {
            'TypeCode': u'StaoTyp1',
            'Geom_Type': u'NrOfPoints',
            'TypeCodelist': '',
            'NrOfPoints': 2,
            'SymbolRef': u'http://localhost:6543/oereb/image/symbol/\
                        ContaminatedPublicTransportSites/1/StaoTyp1',
            'Information': u'Belastet, keine schädlichen oder lästigen Einwirkungen zu erwarten'
        }
    ]
    assert sorted_list == expected_result


def test_get_sorted_legal_provisions():
    renderer = Renderer(DummyRenderInfo())
    expected_result = [
        {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inForce",
            "Lawstatus_Text": "in Kraft",
            "OfficialNumber": "3891.100",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/197"}],
            "Title": "Baugesetz"
        }, {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inForce",
            "Lawstatus_Text": "in Kraft",
            "OfficialNumber": "3891.100",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/198"}],
            "Title": "Baugesetz"
        }, {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inForce",
            "Lawstatus_Text": "in Kraft",
            "OfficialNumber": "07.447",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/214"}],
            "Title": "Revision Ortsplanung"
        }, {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inForce",
            "Lawstatus_Text": "in Kraft",
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
           "Lawstatus_Code": "inForce",
           "Lawstatus_Text": "in Kraft",
           "OfficialNumber": "07.447",
           "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
           "ResponsibleOffice_OfficeAtWeb": "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
           "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/214"}],
           "Title": "Revision Ortsplanung"
        }, {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inForce",
            "Lawstatus_Text": "in Kraft",
            "OfficialNumber": "3891.100",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/197"}],
            "Title": "Baugesetz"
        }, {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inForce",
            "Lawstatus_Text": "in Kraft",
            "OfficialNumber": "07.447",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/213"}],
            "Title": "Revision Ortsplanung"
        }, {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inForce",
            "Lawstatus_Text": "in Kraft",
            "OfficialNumber": "3891.100",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/198"}],
            "Title": "Baugesetz"
        }
    ]
    assert expected_result == renderer.sort_dict_list(test_legal_provisions, renderer.sort_legal_provision)


def test_get_sorted_hints():
    renderer = Renderer(DummyRenderInfo())
    test_hints = [{
        "Canton": "BL",
        "DocumentType": "LegalProvision",
        "Lawstatus_Code": "inForce",
        "Lawstatus_Text": "in Kraft",
        "OfficialNumber": "3891.100",
        "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
        "ResponsibleOffice_OfficeAtWeb": "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
        "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/197"}],
        "Title": "Revision Ortsplanung"
    }, {
        "Canton": "BL",
        "DocumentType": "LegalProvision",
        "Lawstatus_Code": "inForce",
        "Lawstatus_Text": "in Kraft",
        "OfficialNumber": "3891.100",
        "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
        "ResponsibleOffice_OfficeAtWeb": "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
        "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/198"}],
    }, {
        "Canton": "BL",
        "DocumentType": "LegalProvision",
        "Lawstatus_Code": "inForce",
        "Lawstatus_Text": "in Kraft",
        "OfficialNumber": "3891.100",
        "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
        "ResponsibleOffice_OfficeAtWeb": "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
        "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/198"}],
        "Title": "Baugesetz"

    }]

    expected_result = [{
        "Canton": "BL",
        "DocumentType": "LegalProvision",
        "Lawstatus_Code": "inForce",
        "Lawstatus_Text": "in Kraft",
        "OfficialNumber": "3891.100",
        "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
        "ResponsibleOffice_OfficeAtWeb": "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
        "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/198"}],
    }, {
        "Canton": "BL",
        "DocumentType": "LegalProvision",
        "Lawstatus_Code": "inForce",
        "Lawstatus_Text": "in Kraft",
        "OfficialNumber": "3891.100",
        "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
        "ResponsibleOffice_OfficeAtWeb": "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
        "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/198"}],
        "Title": "Baugesetz"
    }, {
        "Canton": "BL",
        "DocumentType": "LegalProvision",
        "Lawstatus_Code": "inForce",
        "Lawstatus_Text": "in Kraft",
        "OfficialNumber": "3891.100",
        "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
        "ResponsibleOffice_OfficeAtWeb": "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
        "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/197"}],
        "Title": "Revision Ortsplanung"
    }]

    assert expected_result == renderer.sort_dict_list(test_hints, renderer.sort_hints)


def test_get_sorted_law():
    renderer = Renderer(DummyRenderInfo())
    test_law = [
        {
            'DocumentType': 'Law',
            'TextAtWeb': [{'URL': 'http://www.admin.ch/ch/d/sr/c814_01.html'}],
            'Title': 'Raumplanungsverordnung für den Kanton Graubünden',
            'Abbreviation': 'KRVO',
            'OfficialNumber': 'BR 801.110',
            'Canton': 'GR',
            'Lawstatus_Code': 'inForce',
            'Lawstatus_Text': 'in Kraft',
            'ResponsibleOffice_Name': u'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb':
                'https://www.gr-lex.gr.ch/frontend/versions/pdf_file_with_annex/2934?locale=de'
        }, {
            'DocumentType': u'Law',
            'TextAtWeb': [{'URL': u'http://www.admin.ch/ch/d/sr/c814_680.html'}],
            'Title': u'Raumplanungsgesetz für den Kanton Graubünden',
            'Abbreviation': u'KRG',
            'Canton': u'GR',
            'Lawstatus_Code': u'inForce',
            'Lawstatus_Text': u'in Kraft',
            'ResponsibleOffice_Name': u'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb':
                u'https://www.gr-lex.gr.ch/frontend/versions/pdf_file_with_annex/2936?locale=de'
        }, {
            'DocumentType': u'Law',
            'TextAtWeb': [{'URL': u'http://www.admin.ch/ch/d/sr/c814_680.html'}],
            'Title': u'Raumplanungsgesetz für den Kanton Graubünden2',
            'Abbreviation': u'KRG',
            'OfficialNumber': u'BR 801.100',
            'Canton': u'GR',
            'Lawstatus_Code': u'inForce',
            'Lawstatus_Text': u'in Kraft',
            'ResponsibleOffice_Name': u'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb':
                u'https://www.gr-lex.gr.ch/frontend/versions/pdf_file_with_annex/2936?locale=de'
        }, {
            'DocumentType': 'Law',
            'TextAtWeb': [{'URL': u'http://www.admin.ch/ch/d/sr/c814_680.html'}],
            'Title': 'Bundesgesetz über die Raumplanung',
            'Abbreviation': 'RPG',
            'OfficialNumber': 'SR 700',
            'Canton': 'GR',
            'Lawstatus_Code': 'inForce',
            'Lawstatus_Text': 'in Kraft',
            'ResponsibleOffice_Name': u'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb': 'http://www.lexfind.ch/dtah/167348/2'
        }, {
            'DocumentType': u'Law',
            'TextAtWeb': [{'URL': u'http://www.admin.ch/ch/d/sr/c814_680.html'}],
            'Title': u'Raumplanungsgesetz für den Kanton Graubünden',
            'Abbreviation': u'KRG',
            'OfficialNumber': u'BR 801.100',
            'Canton': u'GR',
            'Lawstatus_Code': u'inForce',
            'Lawstatus_Text': u'in Kraft',
            'ResponsibleOffice_Name': u'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb':
                u'https://www.gr-lex.gr.ch/frontend/versions/pdf_file_with_annex/2936?locale=de'
        }
    ]

    expected_result = [
        {
            'DocumentType': u'Law',
            'TextAtWeb': [{'URL': u'http://www.admin.ch/ch/d/sr/c814_680.html'}],
            'Title': u'Raumplanungsgesetz für den Kanton Graubünden',
            'Abbreviation': u'KRG',
            'OfficialNumber': u'BR 801.100',
            'Canton': u'GR',
            'Lawstatus_Code': u'inForce',
            'Lawstatus_Text': u'in Kraft',
            'ResponsibleOffice_Name': u'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb':
                u'https://www.gr-lex.gr.ch/frontend/versions/pdf_file_with_annex/2936?locale=de'
        }, {
            'DocumentType': u'Law',
            'TextAtWeb': [{'URL': u'http://www.admin.ch/ch/d/sr/c814_680.html'}],
            'Title': u'Raumplanungsgesetz für den Kanton Graubünden2',
            'Abbreviation': u'KRG',
            'OfficialNumber': u'BR 801.100',
            'Canton': u'GR',
            'Lawstatus_Code': u'inForce',
            'Lawstatus_Text': u'in Kraft',
            'ResponsibleOffice_Name': u'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb':
                u'https://www.gr-lex.gr.ch/frontend/versions/pdf_file_with_annex/2936?locale=de'
        }, {
            'DocumentType': 'Law',
            'TextAtWeb': [{'URL': 'http://www.admin.ch/ch/d/sr/c814_01.html'}],
            'Title': 'Raumplanungsverordnung für den Kanton Graubünden',
            'Abbreviation': 'KRVO',
            'OfficialNumber': 'BR 801.110',
            'Canton': 'GR',
            'Lawstatus_Code': 'inForce',
            'Lawstatus_Text': 'in Kraft',
            'ResponsibleOffice_Name': u'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb':
                'https://www.gr-lex.gr.ch/frontend/versions/pdf_file_with_annex/2934?locale=de'
        }, {
            'DocumentType': 'Law',
            'TextAtWeb': [{'URL': u'http://www.admin.ch/ch/d/sr/c814_680.html'}],
            'Title': 'Bundesgesetz über die Raumplanung',
            'Abbreviation': 'RPG',
            'OfficialNumber': 'SR 700',
            'Canton': 'GR',
            'Lawstatus_Code': 'inForce',
            'Lawstatus_Text': 'in Kraft',
            'ResponsibleOffice_Name': u'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb': 'http://www.lexfind.ch/dtah/167348/2'
        }, {
            'DocumentType': u'Law',
            'TextAtWeb': [{'URL': u'http://www.admin.ch/ch/d/sr/c814_680.html'}],
            'Title': u'Raumplanungsgesetz für den Kanton Graubünden',
            'Abbreviation': u'KRG',
            'Canton': u'GR',
            'Lawstatus_Code': u'inForce',
            'Lawstatus_Text': u'in Kraft',
            'ResponsibleOffice_Name': u'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb':
                u'https://www.gr-lex.gr.ch/frontend/versions/pdf_file_with_annex/2936?locale=de'

        }
    ]
    assert expected_result == renderer.sort_dict_list(test_law, renderer.sort_laws)


def test_group_legal_provisions():
    renderer = Renderer(DummyRenderInfo())
    test_legal_provisions = [
        {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inForce",
            "Lawstatus_Text": "in Kraft",
            "OfficialNumber": "3891.100",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/197"}],
            "Title": "Baugesetz"
        }, {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inForce",
            "Lawstatus_Text": "in Kraft",
            "OfficialNumber": "3891.100",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/198"}],
            "Title": "Baugesetz"
        }, {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inForce",
            "Lawstatus_Text": "in Kraft",
            "OfficialNumber": "07.447",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/213"}],
            "Title": "Revision Ortsplanung"
        }, {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inForce",
            "Lawstatus_Text": "in Kraft",
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
            "Lawstatus_Code": "inForce",
            "Lawstatus_Text": "in Kraft",
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
            "Lawstatus_Code": "inForce",
            "Lawstatus_Text": "in Kraft",
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


def test_archive_pdf():
    renderer = Renderer(DummyRenderInfo())
    extract = {'RealEstate_EGRID': 'CH113928077734'}
    path_and_filename = renderer.archive_pdf_file('/tmp', bytes(), extract)
    assert os.path.isfile(path_and_filename)
