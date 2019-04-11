from pyramid_oereb.contrib.print_proxy.mapfish_print import Renderer
from tests.renderer import DummyRenderInfo


def test_default_wms_url_param_config():
    renderer = Renderer(DummyRenderInfo())
    config = renderer.get_wms_url_params()
    assert config == {'TRANSPARENT': 'true'}
