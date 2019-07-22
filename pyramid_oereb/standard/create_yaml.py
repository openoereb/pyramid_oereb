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
        default='pyramid_oereb_standard.yml',
        help='The name for the new configuration yaml file (default is: pyramid_oereb_standard.yml).'
    )
    parser.add_option(
        '-d', '--database',
        dest='database',
        metavar='DATABASE',
        type='string',
        default='postgresql://postgres:password@db:5432/pyramid_oereb',
        help='The database connection string (default is: '
             'postgresql://postgres:password@db:5432/pyramid_oereb).'
    )
    parser.add_option(
        '-p', '--print_backend',
        dest='print_backend',
        metavar='PRINT_BACKEND',
        type='string',
        default='MapFishPrint',
        help='The print backend (for PDF generation) to use (default is: MapFishPrint)'
    )
    options, args = parser.parse_args()
    _create_standard_yaml_config_(name=options.name, database=options.database,
                                  print_backend=options.print_backend)
