# -*- coding: utf-8 -*-
import optparse

from mako.template import Template
from pyramid.path import AssetResolver


def _create_yaml_config_(
        name='pyramid_oereb.yml',
        database='postgresql://postgres:password@localhost/pyramid_oereb',
        print_backend='MapFishPrint',
        print_url='http://oereb-print:8080/print/oereb'):
    """
    Creates the specified YAML file using a template. This YAML file contains the standard
    configuration to run a oereb server out of the box.

    Args:
        (str): The name of the new file. Default
        database (str): The database connection string.Default:
            'postgresql://postgres:password@localhost/pyramid_oereb'
    """

    # Create pyramid_oereb.yml from template
    template = Template(
        filename=AssetResolver('dev').resolve('config/pyramid_oereb.yml.mako').abspath(),
        input_encoding='utf-8',
        output_encoding='utf-8'
    )
    config = template.render(
        sqlalchemy_url=database,
        print_backend=print_backend,
        print_url=print_url
    )
    pyramid_oereb_yml = open(name, 'wb+')
    pyramid_oereb_yml.write(config)
    pyramid_oereb_yml.close()


def create_yaml():
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
        default='postgresql://postgres:password@oereb-db:5432/pyramid_oereb',
        help='The database connection string (default is: '
             'postgresql://postgres:password@oereb-db:5432/pyramid_oereb).'
    )
    parser.add_option(
        '-p', '--print_backend',
        dest='print_backend',
        metavar='PRINT_BACKEND',
        type='string',
        default='MapFishPrint',
        help='The print backend (for PDF generation) to use (default is: MapFishPrint)'
    )
    parser.add_option(
        '-u', '--print_url',
        dest='print_url',
        metavar='PRINT_URL',
        type='string',
        default='http://oereb-print:8080/print/oereb',
        help='The URL of the print server'
    )
    options, args = parser.parse_args()
    _create_yaml_config_(
        name=options.name,
        database=options.database,
        print_backend=options.print_backend,
        print_url=options.print_url
    )
