# -*- coding: utf-8 -*-
import json
import codecs
import pytest
from pyramid_oereb.contrib.print_proxy.mapfish_print import Renderer
from tests.renderer import DummyRenderInfo


@pytest.fixture()
def coordinates():
    return [[[
        [2615122.772, 1266688.951], [2615119.443, 1266687.783], [2615116.098, 1266686.662],
        [2615112.738, 1266685.586], [2615109.363, 1266684.556], [2615105.975, 1266683.573],
        [2615102.573, 1266682.637], [2615098.859, 1266681.622], [2615095.13, 1266680.663],
        [2615122.772, 1266688.951]
    ]]]


@pytest.fixture()
def extract():
    with codecs.open(
            'tests/contrib/print_proxy/resources/test_extract.json'
    ) as f:
        return json.loads(f.read())


@pytest.fixture()
def expected_printable_extract():
    with codecs.open(
            'tests/contrib/print_proxy/resources/expected_getspec_extract.json'
    ) as f:
        return json.loads(f.read())


@pytest.fixture()
def geometry():
    return {
        'type': 'MultiPolygon',
        'coordinates': coordinates()
    }


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
    assert printable_extract == expected_printable_extract()
