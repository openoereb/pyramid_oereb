# -*- coding: utf-8 -*-
import base64
from json import loads

import datetime
import pytest
from shapely.geometry import MultiPolygon, Polygon

from pyramid_oereb.lib.records.extract import ExtractRecord
from pyramid_oereb.lib.records.image import ImageRecord
from pyramid_oereb.lib.records.office import OfficeRecord
from pyramid_oereb.lib.records.real_estate import RealEstateRecord
from pyramid_oereb.lib.records.view_service import ViewServiceRecord
from pyramid_oereb.lib.renderer.extract.json_ import Renderer
from pyramid_oereb.tests.renderer import DummyRenderInfo
from pyramid_oereb.views.webservice import Parameter


@pytest.fixture()
def params():
    return Parameter(u'reduced', u'json', False, False, u'BL0200002829', u'1000', u'CH775979211712', u'de')


def test_get_localized_text_from_str(config):
    assert isinstance(config._config, dict)
    renderer = Renderer(DummyRenderInfo())
    renderer._language_ = u'de'
    assert renderer.get_localized_text(u'test') == [
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


def test_render(config, params):
    assert isinstance(config._config, dict)
    view_service = ViewServiceRecord(u'http://geowms.bl.ch', u'http://geowms.bl.ch')
    real_estate = RealEstateRecord(u'RealEstate', u'BL', u'Liestal', 2829, 11395,
                                   MultiPolygon([Polygon([(0, 0), (1, 1), (1, 0)])]), u'http://www.geocat.ch',
                                   u'1000', u'BL0200002829', u'CH775979211712',
                                   plan_for_land_register=view_service)
    office_record = OfficeRecord({u'de': u'AGI'})
    extract = ExtractRecord(real_estate, ImageRecord(bin(1)), ImageRecord(bin(2)), ImageRecord(bin(3)),
                            ImageRecord(bin(4)), office_record, {u'de': u'Daten der amtlichen Vermessung'})
    renderer = Renderer(DummyRenderInfo())
    renderer._language_ = u'de'
    renderer._params_ = params
    result = loads(renderer._render(extract))
    assert isinstance(result, dict)
    assert u'GetExtractByIdResponse' in result
    assert result == {
        u'GetExtractByIdResponse': {
            u'extract': {
                u'ExtractIdentifier': unicode(extract.extract_identifier),
                u'CreationDate': unicode(datetime.date.today().isoformat() + 'T00:00:00'),
                u'ConcernedTheme': [],
                u'NotConcernedTheme': [],
                u'ThemeWithoutData': [],
                u'isReduced': True,
                u'LogoPLRCadastre': unicode(base64.b64encode(bin(1))),
                u'FederalLogo': unicode(base64.b64encode(bin(2))),
                u'CantonalLogo': unicode(base64.b64encode(bin(3))),
                u'MunicipalityLogo': unicode(base64.b64encode(bin(4))),
                u'PLRCadastreAuthority': renderer.format_office(office_record),
                u'BaseData': renderer.get_localized_text({u'de': u'Daten der amtlichen Vermessung'}),
                u'RealEstate': renderer.format_real_estate(real_estate)
            }
        }
    }


def test_format_office(config):
    assert isinstance(config._config, dict)
    office = OfficeRecord({u'de': u'Test'}, uid=u'test_uid', office_at_web=u'http://test.example.com',
                          line1=u'test_line1', line2=u'test_line2', street=u'test_street',
                          number=u'test_number', postal_code=1234, city=u'test_city')
    renderer = Renderer(DummyRenderInfo())
    renderer._language_ = u'de'
    assert renderer.format_office(office) == {
        u'Name': renderer.get_localized_text(u'Test'),
        u'UID': u'test_uid',
        u'OfficeAtWeb': u'http://test.example.com',
        u'Line1': u'test_line1',
        u'Line2': u'test_line2',
        u'Street': u'test_street',
        u'Number': u'test_number',
        u'PostalCode': 1234,
        u'City': u'test_city'
    }


# def test_format_real_estate(config):
#     assert isinstance(config._config, dict)
#     record = RealEstateRecord()
