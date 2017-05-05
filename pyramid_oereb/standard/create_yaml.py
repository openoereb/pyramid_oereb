# -*- coding: utf-8 -*-
import optparse

from pyramid_oereb.standard import _create_standard_yaml_config_


def create_standard_yaml():
    parser = optparse.OptionParser(
        usage='usage: %prog [options]',
        description='Create all content for the standard database'
    )
    parser.add_option(
        '-n', '--name',
        dest='name',
        metavar='YAML',
        type='string',
        help='The name for the new configuration yaml file (standard is: pyramid_oereb_standard.yml).'
    )
    options, args = parser.parse_args()
    if not options.name:
        _create_standard_yaml_config_()
    else:
        _create_standard_yaml_config_(name=options.name)
