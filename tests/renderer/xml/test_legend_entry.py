from tests.renderer import DummyRenderInfo
from tests.renderer.xml import xml_templates
from pyramid_oereb.lib.records.image import ImageRecord
from pyramid_oereb.lib.records.theme import ThemeRecord
from pyramid_oereb.lib.records.view_service import LegendEntryRecord
from pyramid_oereb.lib.renderer.extract.xml_ import Renderer
from pyramid_oereb.views.webservice import Parameter
from tests.mockrequest import MockRequest

template = xml_templates().get_template('legend_entry.xml')


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
    legend_entry = LegendEntryRecord(
        symbol=ImageRecord('1'.encode('utf-8')),
        legend_text={'de': 'legend1'},
        type_code='LandUsePlans',
        type_code_list='bla',
        theme=ThemeRecord(u'LandUsePlans', {'de': 'Theme 1'}),
        sub_theme={'de': 'sub theme de'}
    )
    content = template.render(**{
        'params': parameters,
        'localized': renderer.get_localized_text,
        'multilingual': renderer.get_multilingual_text,
        'legend_entry': legend_entry
    }).decode('utf-8').split('\n')
    no_empty_lines = list(filter(lambda line: line != '', content))
    assert no_empty_lines[19] == '<data:SubTheme>sub theme de</data:SubTheme>'
    assert len(no_empty_lines) == 20
