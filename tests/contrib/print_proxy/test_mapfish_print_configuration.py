from pyramid_oereb.contrib.print_proxy.mapfish_print import Renderer
from pyramid_oereb.lib.config import Config
from tests.renderer import DummyRenderInfo


def test_config_wms_url_params():
    Config._config = None
    Config.init('./tests/contrib/print_proxy/resources/test_config.yml', 'pyramid_oereb')
    renderer = Renderer(DummyRenderInfo())
    config = renderer.get_wms_url_params()
    # Restore normal config
    Config._config = None
    Config.init('./pyramid_oereb/standard/pyramid_oereb.yml', 'pyramid_oereb')
    # Do the check for this test. Value should match the one from the YAML configuration.
    assert config == {'TRANSPARENT': 'true', 'OTHERCUSTOM': 'myvalue'}


def test_bad_config_wms_url_params():
    Config._config = None
    Config.init('./tests/contrib/print_proxy/resources/test_bad_config.yml', 'pyramid_oereb')
    renderer = Renderer(DummyRenderInfo())
    config = renderer.get_wms_url_params()
    # Restore normal config
    Config._config = None
    Config.init('./pyramid_oereb/standard/pyramid_oereb.yml', 'pyramid_oereb')
    # Do the check for this test. Value should be empty.
    assert config == {}


def test_custom_config_wms_url_params():
    Config._config = None
    Config.init('./tests/contrib/print_proxy/resources/test_custom_config.yml', 'pyramid_oereb')
    renderer = Renderer(DummyRenderInfo())
    wms_url_keep_params = Config.get('print', {}).get('wms_url_keep_params', False)
    params = {
        'TRANSPARENT': ['true'],
        'OTHERCUSTOM': ['myvalue'],
        'epoch': ['2018-11-29T15:13:31']
    }
    config = renderer.get_wms_url_params(params if wms_url_keep_params else None)
    # Restore normal config
    Config._config = None
    Config.init('./pyramid_oereb/standard/pyramid_oereb.yml', 'pyramid_oereb')
    # Do the check for this test. Value should match the one from the YAML configuration.
    assert config == {
        'TRANSPARENT': 'true',
        'OTHERCUSTOM': 'myvalue',
        'epoch': '2018-11-29T15:13:31'
    }


def test_default_wms_url_param_config():
    renderer = Renderer(DummyRenderInfo())
    config = renderer.get_wms_url_params()
    # Do the check for this test. Value should be the default setting.
    assert config == {'TRANSPARENT': 'true'}
