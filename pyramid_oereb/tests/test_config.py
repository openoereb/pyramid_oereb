# -*- coding: utf-8 -*-
import pytest
from pyramid.config import ConfigurationError

from pyramid_oereb.lib.config import parse, ConfigReader
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
    config_reader = ConfigReader('./pyramid_oereb/tests/resources/test_config.yml', 'pyramid_oereb')
    plr_cadastre_authority = config_reader.get_plr_cadastre_authority()
    assert isinstance(plr_cadastre_authority, OfficeRecord)
    assert plr_cadastre_authority.to_extract() == {
        'name': 'PLR cadastre authority',
        'office_at_web': 'https://www.cadastre.ch/en/oereb.html',
        'street': 'Seftigenstrasse',
        'number': 264,
        'postal_code': 3084,
        'city': 'Wabern'
    }


def test_get_logos_config():
    config_reader = ConfigReader('./pyramid_oereb/tests/resources/test_config.yml', 'pyramid_oereb')
    logos = config_reader.get_logo_config()
    assert isinstance(logos, dict)
