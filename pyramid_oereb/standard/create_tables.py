# -*- coding: utf-8 -*-
import optparse
from pyramid_oereb.standard import _create_tables_


__author__ = 'Clemens Rudert'
__create_date__ = '15.03.17'


def create_tables():
    parser = optparse.OptionParser(
        usage='usage: %prog [options]',
        description='Create all content for the standard database'
    )
    parser.add_option(
        '-c', '--configuration',
        dest='configuration',
        metavar='YAML',
        type='string',
        help='The absolute path to the configuration yaml file (standard is: pyramid_oereb.yml).'
    )
    parser.add_option(
        '-s', '--section',
        dest='section',
        metavar='SECTION',
        type='string',
        default='pyramid_oereb',
        help='The section which contains configruation (default is: pyramid_oereb).'
    )
    options, args = parser.parse_args()
    if not options.configuration:
        parser.error('No configuration file set.')
    _create_tables_(configuration_yaml_path=options.configuration, section=options.section)
