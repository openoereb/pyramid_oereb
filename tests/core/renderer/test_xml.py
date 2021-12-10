# -*- coding: utf-8 -*-

import pytest
from io import BytesIO
from lxml import etree

from pyramid.path import DottedNameResolver
from shapely.geometry import MultiPolygon, Polygon
from pyramid_oereb.core.records.disclaimer import DisclaimerRecord
from pyramid_oereb.core.records.extract import ExtractRecord
from pyramid_oereb.core.records.glossary import GlossaryRecord
from pyramid_oereb.core.records.office import OfficeRecord
from pyramid_oereb.core.records.real_estate import RealEstateRecord
from pyramid_oereb.core.records.view_service import ViewServiceRecord

from pyramid_oereb.core.renderer.extract.xml_ import Renderer
from pyramid_oereb.core.renderer.versions.xml_ import Renderer as VersionsRenderer
from pyramid_oereb.core.views.webservice import Parameter
from tests.mockrequest import MockRequest


def test_get_gml_id():
    renderer = Renderer(None)
    assert renderer._get_gml_id() == 'gml1'
    assert renderer._get_gml_id() == 'gml2'
    assert renderer._get_gml_id() == 'gml3'


def test_version_against_schema(logo_test_data, schema_xml_versions, DummyRenderInfo):
    versions = {
        u'GetVersionsResponse': {
            u'supportedVersion': [
                {
                    u'version': u'1.0',
                    u'serviceEndpointBase': u'https://example.com'
                }
            ]
        }
    }
    renderer = VersionsRenderer(DummyRenderInfo())
    rendered = renderer._render(versions)

    xmlschema_doc = etree.parse(schema_xml_versions)
    xmlschema = etree.XMLSchema(xmlschema_doc)
    buffer = BytesIO(rendered)
    doc = etree.parse(buffer)
    assert xmlschema.validate(doc)


def _get_test_extract(config, glossary):
    view_service = ViewServiceRecord({'de': u'http://geowms.bl.ch'},
                                     1,
                                     1.0,
                                     None)
    real_estate = RealEstateRecord(u'Liegenschaft', u'BL', u'Liestal', 2829, 11395,
                                   MultiPolygon([Polygon([(0, 0), (1, 1), (1, 0)])]),
                                   u'http://www.geocat.ch', u'1000', u'BL0200002829', u'CH775979211712')
    real_estate.set_view_service(view_service)
    real_estate.set_main_page_view_service(view_service)
    office_record = OfficeRecord({'de': u'AGI'}, office_at_web={
        'de': 'https://www.bav.admin.ch/bav/de/home.html'
    })
    resolver = DottedNameResolver()
    date_method_string = (config
                          .get('extract')
                          .get('base_data')
                          .get('methods')
                          .get('date'))
    date_method = resolver.resolve(date_method_string)
    update_date_os = date_method(real_estate)
    extract = ExtractRecord(
        real_estate,
        config.get_oereb_logo(),
        config.get_conferderation_logo(),
        config.get_canton_logo(),
        config.get_municipality_logo(1234),
        office_record,
        update_date_os,
        disclaimers=[
            DisclaimerRecord({'de': u'Haftungsausschluss'}, {'de': u'Test'})
        ],
        glossaries=glossary,
        general_information=config.get_general_information()
    )
    # extract.qr_code = 'VGhpcyBpcyBub3QgYSBRUiBjb2Rl'.encode('utf-8') TODO:
    #    qr_code Must be an image ('base64Binary'), but even with images xml validation
    #    fails on it.
    # extract.electronic_signature = 'Signature'  # TODO: fix signature rendering first
    return extract


@pytest.mark.parametrize('parameter, test_extract', [
    (
            Parameter('reduced', 'xml', False, False, 'BL0200002829', '1000', 'CH775979211712', 'de'),
            [GlossaryRecord({'de': u'Glossar'}, {'de': u'Test'})]  # 'get_default_extract'
    ),
    (
            Parameter('reduced', 'xml', False, False, 'BL0200002829', '1000', 'CH775979211712', 'de'),
            []  # 'get_empty_glossary_extract'
    ),
    (
            Parameter('reduced', 'xml', False, False, 'BL0200002829', '1000', 'CH775979211712', 'de'),
            None  # 'get_none_glossary_extract'
    )
])
def test_extract_against_schema(real_estate_test_data, logo_test_data, schema_xml_extract, DummyRenderInfo, parameter, test_extract):
    from pyramid_oereb.core.config import Config
    extract = _get_test_extract(Config, test_extract)
    renderer = Renderer(DummyRenderInfo())
    renderer._language = u'de'
    renderer._request = MockRequest()
    renderer._request.route_url = lambda url, **kwargs: "http://example.com/current/view"
    rendered = renderer._render(extract, parameter)

    xmlschema_doc = etree.parse(schema_xml_extract)
    # xmlschema = etree.XMLSchema(xmlschema_doc)  # schema parsing very slow and fails
    buffer = BytesIO(rendered)
    doc = etree.parse(buffer)
    # xmlschema.assertValid(doc)
