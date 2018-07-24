# -*- coding: utf-8 -*-
import datetime
import pytest
from pyramid.config import ConfigurationError

from pyramid_oereb.lib.config import parse, merge_dicts, Config
from pyramid_oereb.lib.records.office import OfficeRecord


def test_missing_configuration_file():
    with pytest.raises(ConfigurationError):
        parse(None, None)


def test_missing_configuration_section():
    with pytest.raises(ConfigurationError):
        parse('myconfig.yml', None)


def test_wrong_configuration_section():
    with pytest.raises(ConfigurationError):
        parse('./tests/resources/test_config.yml', 'invalidsection')


def test_configuration_file_not_found():
    with pytest.raises(IOError) as excinfo:
        parse('not_existing_config.yml', 'invalidsection')
    assert ', Current working directory is ' in str(excinfo.value)


def test_parse_configuration():
    cfg = parse('./tests/resources/test_config.yml', 'section2')
    assert cfg.get('param1') == 1
    assert len(cfg.get('param2')) == 2
    assert cfg.get('param2')[0] == 'first'
    assert cfg.get('param2')[1] == 'second'


def test_merge_dicts():
    base = {
        'a': 1,
        'b': 'b value',
        'c': {
            'd': 2,
            'keep': 'asdf',
            'e': {
                'f': [1, 2, 3]
            }
        },
        'g': [],
        'h': {
            'i': 123,
            'h': 'abcde'
        }
    }
    overwrite = {
        'b': 'new b value',
        'c': {
            'd': 3,
            'e': {
                'f': []
            }
        }

    }
    expected = {
        'a': 1,
        'b': 'new b value',
        'c': {
            'd': 3,
            'keep': 'asdf',
            'e': {
                'f': []
            }
        },
        'g': [],
        'h': {
            'i': 123,
            'h': 'abcde'
        }
    }
    merged = merge_dicts(base, overwrite)
    assert merged == expected


def test_get_plr_cadastre_authority():
    Config._config = None
    Config.init('./tests/resources/test_config.yml', 'pyramid_oereb')
    plr_cadastre_authority = Config.get_plr_cadastre_authority()
    assert isinstance(plr_cadastre_authority, OfficeRecord)


def test_get_logos_config():
    Config._config = None
    Config.init('./tests/resources/test_config.yml', 'pyramid_oereb')
    logos = Config.get_logo_config()
    assert isinstance(logos, dict)


def test_get_all_federal():
    Config._config = None
    Config.init('./pyramid_oereb/standard/pyramid_oereb.yml', 'pyramid_oereb')
    all_federal = Config.get_all_federal()
    assert isinstance(all_federal, list)
    assert len(all_federal) == 10
    assert 'RailwaysProjectPlanningZones' in all_federal


def test_get_base_data():
    Config._config = None
    Config.init('./pyramid_oereb/standard/pyramid_oereb.yml', 'pyramid_oereb')
    date = datetime.datetime(2017, 2, 1)
    base_data = Config.get_base_data(date)
    assert isinstance(base_data, dict)
    assert base_data.get('de') == 'Daten der amtlichen Vermessung, Stand 01.02.2017.'


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


def test_get_layer_config():
    Config._config = None
    Config.init('./tests/resources/test_config.yml', 'pyramid_oereb')
    layer_index, layer_opacity = Config.get_layer_config('LandUsePlans')
    assert layer_index == 1
    assert layer_opacity == 0.25
    layer_index, layer_opacity = Config.get_layer_config('MotorwaysProjectPlaningZones')
    assert layer_index is None
    assert layer_opacity is None


def test_get_real_estate_main_page_config():
    Config._config = None
    Config.init('./tests/resources/test_config.yml', 'pyramid_oereb')
    plan_for_land_register_main_page_config = Config.get_plan_for_land_register_main_page_config()
    assert plan_for_land_register_main_page_config.get('reference_wms') == 'https://wms.ch/?BBOX=2475000,' \
                                                                           '1065000,2850000,1300000'
    assert plan_for_land_register_main_page_config.get('layer_index') == 2
    assert plan_for_land_register_main_page_config.get('layer_opacity') == 0.5
