# -*- coding: utf-8 -*-
import pytest

from pyramid.config import ConfigurationError

# from pyramid_oereb.core.adapter import FileAdapter
from pyramid_oereb.core.config import Config
from pyramid_oereb.core.records.office import OfficeRecord


# order=-1 to run them after all and don't screw the configuration in Config
@pytest.mark.run(order=-1)
def test_missing_configuration_file():
    Config._config = None
    with pytest.raises(ConfigurationError):
        Config.init(None, None)


@pytest.mark.run(order=-1)
def test_missing_configuration_section():
    Config._config = None
    with pytest.raises(ConfigurationError):
        Config.init('myconfig.yml', None)


@pytest.mark.run(order=-1)
def test_wrong_configuration_section():
    Config._config = None
    with pytest.raises(ConfigurationError):
        Config.init('./tests/resources/test_config.yml', 'invalidsection')


@pytest.mark.run(order=-1)
def test_configuration_file_not_found():
    Config._config = None
    with pytest.raises(IOError) as excinfo:
        Config.init('not_existing_config.yml', 'invalidsection')
    assert ', Current working directory is ' in str(excinfo.value)


@pytest.mark.run(order=-1)
def test_parse_configuration():
    Config._config = None
    Config.init('./tests/resources/test_config.yml', 'section2')
    assert Config.get('param1') == 1
    assert len(Config.get('param2')) == 2
    assert Config.get('param2')[0] == 'first'
    assert Config.get('param2')[1] == 'second'


@pytest.mark.run(order=-1)
def test_get_plr_cadastre_authority():
    Config._config = None
    Config.init('./tests/resources/test_config.yml', 'pyramid_oereb')
    plr_cadastre_authority = Config.get_plr_cadastre_authority()
    assert isinstance(plr_cadastre_authority, OfficeRecord)


@pytest.mark.run(order=-1)
def test_get_logo_config():
    Config._config = None
    Config.init('./tests/resources/test_config.yml', 'pyramid_oereb')
    logo_config = Config.get_logo_config()
    assert isinstance(logo_config, dict)
    source = logo_config.get('source')
    assert isinstance(source, dict)
    class_config = source.get('class')
    assert isinstance(class_config, str)
    params = source.get('params')
    assert isinstance(params, dict)
    db_connection = params.get('db_connection')
    assert isinstance(db_connection, str)
    model = params.get('model')
    assert isinstance(model, str)


@pytest.mark.run(order=-1)
def test_get_all_federal():
    Config._config = None
    Config.init('./pyramid_oereb/standard/pyramid_oereb.yml', 'pyramid_oereb')
    all_federal = Config.get_all_federal()
    assert isinstance(all_federal, list)
    assert len(all_federal) == 10
    assert 'ch.ProjektierungszonenEisenbahnanlagen' in all_federal


@pytest.mark.run(order=-1)
def test_get_oereblex_config():
    Config._config = None
    Config.init('./tests/resources/test_config.yml', 'pyramid_oereb')
    cfg = Config.get_oereblex_config()
    assert isinstance(cfg, dict)
    assert cfg == {
        'host': 'http://oereblex.example.com',
        'language': 'de',
        'proxy': {
            'http': 'http://my.proxy.org',
            'https': None
        }
    }


@pytest.mark.run(order=-1)
def test_get_layer_config():
    Config._config = None
    Config.init('./tests/resources/test_config.yml', 'pyramid_oereb')
    layer_index, layer_opacity = Config.get_layer_config('ch.Nutzungsplanung')
    assert layer_index == 1
    assert layer_opacity == 0.25
    layer_index, layer_opacity = Config.get_layer_config('ch.ProjektierungszonenNationalstrassen')
    assert layer_index is None
    assert layer_opacity is None


@pytest.mark.run(order=-1)
def test_get_real_estate_main_page_config():
    Config._config = None
    Config.init('./tests/resources/test_config.yml', 'pyramid_oereb')
    lang = Config.get('default_language')
    plan_for_land_register_main_page_config = Config.get_plan_for_land_register_main_page_config()
    assert plan_for_land_register_main_page_config.get('reference_wms')[lang] == \
        'https://wms.ch/?BBOX=2475000,1065000,2850000,1300000'
    assert plan_for_land_register_main_page_config.get('layer_index') == 2
    assert plan_for_land_register_main_page_config.get('layer_opacity') == 0.5
