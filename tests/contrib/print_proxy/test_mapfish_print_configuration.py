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


def test_get_custom_wms_params_false():
    Config._config = None
    Config.init('./tests/contrib/print_proxy/resources/test_config.yml', 'pyramid_oereb')
    renderer = Renderer(DummyRenderInfo())
    params = {
        'TRANSPARENT': ['true'],
        'OTHERCUSTOM': ['myvalue'],
        'epoch': ['2018-11-29T15:13:31']
    }
    config = renderer.get_custom_wms_params(params)

    # Restore normal config
    Config._config = None
    Config.init('./pyramid_oereb/standard/pyramid_oereb.yml', 'pyramid_oereb')

    assert config == {
        'OTHERCUSTOM': 'myvalue',
        'TRANSPARENT': 'true'
    }


def test_get_custom_wms_params_true():
    Config._config = None
    Config.init('./tests/contrib/print_proxy/resources/test_custom_config.yml', 'pyramid_oereb')
    renderer = Renderer(DummyRenderInfo())
    # Define different test cases
    params1 = {
        'TRANSPARENT': ['true'],
        'OTHERCUSTOM': ['myvalue'],
        'epoch': ['2018-11-29T15:13:31']
    }
    params2 = {
        'OTHERCUSTOM': ['myvalue'],
        'epoch': ['2018-11-29T15:13:31']
    }
    params3 = {
        'epoch': '2018-11-29T15:13:31'
    }
    params4 = {
        'epoch': ['2018-11-29T15:13:31', '2020-11-29T17:13:50']
    }

    config1 = renderer.get_custom_wms_params(params1)
    config2 = renderer.get_custom_wms_params(params2)
    config3 = renderer.get_custom_wms_params(params3)
    config4 = renderer.get_custom_wms_params(params4)

    # Restore normal config
    Config._config = None
    Config.init('./pyramid_oereb/standard/pyramid_oereb.yml', 'pyramid_oereb')

    # Do the check for the different test cases. Value should match the ones from the YAML configuration.
    assert config1 == {
        'TRANSPARENT': 'true',
        'epoch': '2018-11-29T15:13:31'
    }
    assert config2 == {
        'epoch': '2018-11-29T15:13:31'
    }
    assert config3 == {
        'epoch': '2018-11-29T15:13:31'
    }
    assert config4 == {
        'epoch': '2018-11-29T15:13:31,2020-11-29T17:13:50'
    }


def test_default_wms_url_param_config():
    renderer = Renderer(DummyRenderInfo())
    config = renderer.get_wms_url_params()
    # Do the check for this test. Value should be the default setting.
    assert config == {'TRANSPARENT': 'true'}
