# -*- coding: utf-8 -*-
import datetime
from shapely.geometry import LineString, Point, Polygon

from pyramid_oereb.lib.records.documents import DocumentRecord, LegalProvisionRecord
from pyramid_oereb.lib.records.law_status import LawStatusRecord
from pyramid_oereb.lib.records.office import OfficeRecord
from pyramid_oereb.lib.renderer.extract.xml_ import Renderer
from tests.conftest import params
import pytest


def test_get_gml_id():
    renderer = Renderer(None)
    assert renderer._get_gml_id() == 'gml1'
    assert renderer._get_gml_id() == 'gml2'
    assert renderer._get_gml_id() == 'gml3'


def test_get_document_type():
    document = DocumentRecord(LawStatusRecord.from_config('inForce'), datetime.date.today(),
                              {'de': 'Test'}, OfficeRecord({'de': 'Test'}))
    legal_provision = LegalProvisionRecord(LawStatusRecord.from_config('inForce'), datetime.date.today(),
                                           {'de': 'Test'}, OfficeRecord({'de': 'Test'}))
    assert Renderer._get_document_type(document) == 'data:Document'
    assert Renderer._get_document_type(legal_provision) == 'data:LegalProvisions'


@pytest.mark.parametrize('parameters', params)
def test_line(parameters, xml_templates):
    line = LineString(((0, 0), (1, 1)))
    template = xml_templates.get_template('geometry/line.xml')

    def get_gml_id():
        return 'gml1'

    content = template.render(**{
        'params': parameters,
        'default_language': 'de',
        'line': line,
        'get_gml_id': get_gml_id
    }).decode('utf-8').split('\n')
    expected_content = """
    <gml:LineString gml:id="gml1">
        <gml:pos>0.0 0.0</gml:pos>
        <gml:pos>1.0 1.0</gml:pos>
    </gml:LineString>
    """.split('\n')
    expected_lines = []
    for line in expected_content:
        expected_lines.append(line.strip())
    content_lines = []
    for line in content:
        content_lines.append(line.strip())
    assert expected_lines == content_lines


@pytest.mark.parametrize('parameters', params)
def test_point(parameters, xml_templates):
    point = Point((0, 0))
    template = xml_templates.get_template('geometry/point.xml')
    content = template.render(**{
        'params': parameters,
        'default_language': 'de',
        'point': point
    }).decode('utf-8').split('\n')
    expected_content = """
    <gml:pos>0.0 0.0</gml:pos>""".split('\n')
    expected_lines = []
    for line in expected_content:
        expected_lines.append(line.strip())
    content_lines = []
    for line in content:
        content_lines.append(line.strip())
    assert expected_lines == content_lines


@pytest.mark.parametrize('parameters', params)
def test_polygon(parameters, xml_templates):
    polygon = Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)))
    template = xml_templates.get_template('geometry/polygon.xml')

    def get_gml_id():
        return 'gml1'

    content = template.render(**{
        'params': parameters,
        'default_language': 'de',
        'polygon': polygon,
        'get_gml_id': get_gml_id
    }).decode('utf-8').split('\n')
    expected_content = """
    <gml:Polygon gml:id="gml1">
        <gml:exterior>
            <gml:LinearRing>
                <gml:pos>0.0 0.0</gml:pos>
                <gml:pos>0.0 1.0</gml:pos>
                <gml:pos>1.0 1.0</gml:pos>
                <gml:pos>1.0 0.0</gml:pos>
                <gml:pos>0.0 0.0</gml:pos>
            </gml:LinearRing>
        </gml:exterior>
        <gml:interior>
            <gml:LinearRing>
                <gml:pos>0.0 0.0</gml:pos>
                <gml:pos>0.0 1.0</gml:pos>
                <gml:pos>1.0 1.0</gml:pos>
                <gml:pos>1.0 0.0</gml:pos>
                <gml:pos>0.0 0.0</gml:pos>
            </gml:LinearRing>
        </gml:interior>
    </gml:Polygon>""".split('\n')
    expected_lines = []
    for line in expected_content:
        expected_lines.append(line.strip())
    content_lines = []
    for line in content:
        content_lines.append(line.strip())
    assert expected_lines == content_lines
