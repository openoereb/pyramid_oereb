# -*- coding: utf-8 -*-
import pytest
from pyramid.config import ConfigurationError

from pyramid_oereb.lib.config import parse, Config
from pyramid_oereb.lib.records.office import OfficeRecord


def test_missing_configuration_file():
    with pytest.raises(ConfigurationError):
        parse(None, None)


def test_missing_configuration_section():
    with pytest.raises(ConfigurationError):
        parse('myconfig.yml', None)


def test_wrong_configuration_section():
    with pytest.raises(ConfigurationError):
        parse('./pyramid_oereb/tests/resources/test_config.yml', 'invalidsection')


def test_configuration_file_not_found():
    with pytest.raises(IOError) as excinfo:
        parse('not_existing_config.yml', 'invalidsection')
    assert ', Current working directory is ' in str(excinfo.value)


def test_parse_configuration():
    cfg = parse('./pyramid_oereb/tests/resources/test_config.yml', 'section2')
    assert cfg.get('param1') == 1
    assert len(cfg.get('param2')) == 2
    assert cfg.get('param2')[0] == 'first'
    assert cfg.get('param2')[1] == 'second'


def test_get_plr_cadastre_authority():
    Config._config = None
    Config.init('./pyramid_oereb/tests/resources/test_config.yml', 'pyramid_oereb')
    plr_cadastre_authority = Config.get_plr_cadastre_authority()
    assert isinstance(plr_cadastre_authority, OfficeRecord)


def test_get_logos_config():
    Config._config = None
    Config.init('./pyramid_oereb/tests/resources/test_config.yml', 'pyramid_oereb')
    logos = Config.get_logo_config()
    assert isinstance(logos, dict)


def test_get_all_federal():
    Config._config = None
    Config.init('./pyramid_oereb/standard/pyramid_oereb.yml', 'pyramid_oereb')
    all_federal = Config.get_all_federal()
    assert isinstance(all_federal, list)
    assert len(all_federal) == 17
    assert 'RailwaysProjectPlanningZones' in all_federal
