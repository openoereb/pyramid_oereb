from pyramid_oereb.core.records.image import ImageRecord
from pyramid_oereb.core.records.theme import ThemeRecord
from pyramid_oereb.core.records.view_service import LegendEntryRecord
from pyramid_oereb.core.renderer.extract.xml_ import Renderer
from pyramid_oereb.core.views.webservice import Parameter
from tests.mockrequest import MockRequest


def test_sub_theme(DummyRenderInfo, xml_templates, pyramid_oereb_test_config):
    template = xml_templates.get_template('legend_entry.xml')
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
    legend_entry = LegendEntryRecord(
        symbol=ImageRecord('1'.encode('utf-8')),
        legend_text={'de': 'legend1'},
        type_code='ch.Nutzungsplanung',
        type_code_list='bla',
        theme=ThemeRecord(
            u'ch.Nutzungsplanung',
            {'de': 'Theme 1 with sub-theme'}, 20, u'ch.NutzungsplanungSubCode'
        ),
    )
    content = template.render(**{
        'params': parameters,
        'localized': renderer.get_localized_text,
        'multilingual': renderer.get_multilingual_text,
        'legend_entry': legend_entry
    }).decode('utf-8').split('\n')
    no_empty_lines = list(filter(lambda line: line != '', content))
    no_empty_lines = [no_space.strip() for no_space in no_empty_lines]
    assert '<data:Text>Theme 1 with sub-theme</data:Text>' in no_empty_lines
    assert '<data:SubCode>ch.NutzungsplanungSubCode</data:SubCode>' in no_empty_lines
    assert '<data:Code>ch.Nutzungsplanung</data:Code>' in no_empty_lines
    assert len(no_empty_lines) == 22
