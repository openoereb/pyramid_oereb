import pytest
from pyramid.config import ConfigurationError

from pyramid_oereb import parse


def test_missing_configuration_file():
    with pytest.raises(ConfigurationError):
        parse(None, None)


def test_missing_configuration_section():
    with pytest.raises(ConfigurationError):
        parse('myconfig.yaml', None)


def test_wrong_configuration_section():
    with pytest.raises(ConfigurationError):
        parse('./pyramid_oereb/tests/test_config.yaml', 'invalidsection')


def test_parse_configuration():
    cfg = parse('./pyramid_oereb/tests/test_config.yaml', 'section2')
    assert cfg.get('param1') == 1
    assert len(cfg.get('param2')) == 2
    assert cfg.get('param2')[0] == 'first'
    assert cfg.get('param2')[1] == 'second'
