from pyramid_oereb.lib.records.geometry import GeometryRecord
from pyramid_oereb.lib.records.image import ImageRecord
from pyramid_oereb.lib.records.law_status import LawStatusRecord
from pyramid_oereb.lib.records.office import OfficeRecord
from pyramid_oereb.lib.records.plr import PlrRecord
from pyramid_oereb.lib.records.theme import ThemeRecord
from pyramid_oereb.lib.records.view_service import ViewServiceRecord, LegendEntryRecord
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
        with_geometry=False,
        images=True,
        signed=False,
        identdn='BL0200002829',
        number='1000',
        egrid='CH775979211712',
        language='de')
    renderer = Renderer(DummyRenderInfo())
    renderer._language = u'de'
    renderer._request = MockRequest()
    renderer._request.route_url = lambda url, **kwargs: "http://example.com/current/view"
    theme = ThemeRecord(u'ch.Nutzungsplanung', {'de': 'Theme 1'}, 1)
    subtheme = ThemeRecord(u'ch.Nutzungsplanung', {'de': 'sub-Theme 1'}, 2, u'ch.NutzungsplanungSubCode')
    office = OfficeRecord(name={'de': 'office de'})
    law_status = LawStatusRecord(
        code='AenderungMitVorwirkung',
        title={'de': 'law status de'}
    )
    geometry = GeometryRecord(law_status, datetime.now(), datetime.now(), Polygon(), 'test')
    public_law_restriction = PlrRecord(
        theme=theme,
        legend_entry=LegendEntryRecord(
                        ImageRecord('1'.encode('utf-8')),
                        {'de': 'information de'},
                        'CodeA',
                        None,
                        theme,
                        view_service_id=1
        ),
        law_status=law_status,
        published_from=datetime.now(),
        published_until=None,
        responsible_office=office,
        symbol=ImageRecord('1'.encode('utf-8')),
        view_service=ViewServiceRecord(
            reference_wms=dict(),
            layer_index=0,
            layer_opacity=1.0),
        geometries=[geometry],
        sub_theme=subtheme
    )
    content = template.render(**{
        'params': parameters,
        'localized': renderer.get_localized_text,
        'multilingual': renderer.get_multilingual_text,
        'get_localized_image': renderer.get_localized_image,
        'public_law_restriction': public_law_restriction
    }).decode('utf-8').split('\n')
    no_empty_lines = list(filter(lambda line: line != '', content))
    no_empty_lines = [no_space.strip() for no_space in no_empty_lines]

    assert '<data:SubTheme>' in no_empty_lines
    assert '<data:Text>sub-Theme 1</data:Text>' in no_empty_lines
    assert '<data:SubCode>ch.NutzungsplanungSubCode</data:SubCode>' in no_empty_lines
    assert '<data:Code>ch.Nutzungsplanung</data:Code>' in no_empty_lines
    assert len(no_empty_lines) == 78
