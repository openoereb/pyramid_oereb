# -*- coding: utf-8 -*-
import pytest
from pyramid.config import ConfigurationError

from pyramid_oereb import parse


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
