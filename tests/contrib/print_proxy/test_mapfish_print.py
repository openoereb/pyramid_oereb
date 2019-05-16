# -*- coding: utf-8 -*-
import sys
import json
import codecs
from pyramid_oereb.contrib.print_proxy.mapfish_print import Renderer
from tests.renderer import DummyRenderInfo
from pyramid_oereb.contrib.print_proxy.sub_themes.sorting import AlphabeticSort, ListSort


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
    # FIXME Do the test only in python 2 because order of item are different
    # in some cases with python 3. The Error will not be possible anymore with
    # https://github.com/openoereb/pyramid_oereb/issues/651
    if sys.version_info.major == 2:
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
    sorted_list = renderer._get_sorted_legend(test_legend_list)
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
            'SymbolRef': u'http://localhost:6543/oereb/image/symbol/\
                        ContaminatedPublicTransportSites/1/StaoTyp1',
            'Information': u'Belastet, keine schädlichen oder lästigen Einwirkungen zu erwarten'
        }
    ]
    assert sorted_list == expected_result
