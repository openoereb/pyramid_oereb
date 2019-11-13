from pyramid_oereb.lib.records.geometry import GeometryRecord
from pyramid_oereb.lib.records.image import ImageRecord
from pyramid_oereb.lib.records.law_status import LawStatusRecord
from pyramid_oereb.lib.records.office import OfficeRecord
from pyramid_oereb.lib.records.plr import PlrRecord
from pyramid_oereb.lib.records.theme import ThemeRecord
from pyramid_oereb.lib.records.view_service import ViewServiceRecord
from pyramid_oereb.lib.renderer.extract.xml_ import Renderer
from pyramid_oereb.views.webservice import Parameter
from tests.mockrequest import MockRequest
from tests.renderer import DummyRenderInfo
from tests.renderer.xml import xml_templates
from datetime import datetime
from shapely.geometry import Polygon

template = xml_templates().get_template('public_law_restriction.xml')


def test_sub_theme():
    parameters = Parameter(
        response_format='xml',
        flavour='reduced',
        with_geometry=False,
        images=True,
        identdn='BL0200002829',
        number='1000',
        egrid='CH775979211712',
        language='de')
    renderer = Renderer(DummyRenderInfo())
    renderer._language = u'de'
    renderer._request = MockRequest()
    renderer._request.route_url = lambda url, **kwargs: "http://example.com/current/view"
    office = OfficeRecord(name={'de': 'office de'})
    law_status = LawStatusRecord(
        code='runningModifications',
        text={'de': 'law status de'}
    )
    geometry = GeometryRecord(law_status, datetime.now(), Polygon(), 'test', office=office)
    public_law_restriction = PlrRecord(
        theme=ThemeRecord(u'LandUsePlans', {'de': 'Theme 1'}),
        information={'de': 'information de'},
        law_status=law_status,
        published_from=datetime.now(),
        responsible_office=office,
        symbol=ImageRecord('1'.encode('utf-8')),
        view_service=ViewServiceRecord(
            reference_wms='',
            layer_index=0,
            layer_opacity=1.0),
        geometries=[geometry],
        sub_theme={'de': 'sub theme de'}
    )
    content = template.render(**{
        'params': parameters,
        'localized': renderer.get_localized_text,
        'multilingual': renderer.get_multilingual_text,
        'public_law_restriction': public_law_restriction
    }).decode('utf-8').split('\n')
    no_empty_lines = list(filter(lambda line: line != '', content))
    assert no_empty_lines[18] == '    <data:SubTheme>sub theme de</data:SubTheme>'
    assert len(no_empty_lines) == 72
