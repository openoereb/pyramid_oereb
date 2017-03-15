# -*- coding: utf-8 -*-


import yaml
from pyramid.config import ConfigurationError


def parse(cfg_file, cfg_section):
    """
    Parses the defined YAML file and returns the defined section as dictionary.
    :param cfg_file: The YAML file to be parsed.
    :param cfg_section: The section to be returned.
    :return: The parsed section as dictionary.
    """
    if cfg_file is None:
        raise ConfigurationError('Missing configuration parameter "pyramid_oereb.cfg.file".')
    if cfg_section is None:
        raise ConfigurationError('Missing configuration parameter "pyramid_oereb.cfg.section".')
    with open(cfg_file) as f:
        content = yaml.safe_load(f.read())
    cfg = content.get(cfg_section)
    if cfg is None:
        raise ConfigurationError('YAML file contains no section "{0}"'.format(cfg_section))
    return cfg
