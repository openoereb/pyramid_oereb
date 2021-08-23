# -*- coding: utf-8 -*-
import optparse
import os

from mako.template import Template
from pyramid.path import AssetResolver
from shutil import copyfile


def _create_standard_yaml_config_(name='pyramid_oereb_standard.yml',
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

    # File names
    logo_oereb_name_de = 'logo_oereb_de.png'
    logo_oereb_name_fr = 'logo_oereb_fr.png'
    logo_oereb_name_it = 'logo_oereb_it.png'
    logo_confederation_name = 'logo_confederation.png'
    logo_canton_name = 'logo_canton.png'

    # Create pyramid_oereb.yml from template
    template = Template(
        filename=AssetResolver('pyramid_oereb').resolve('standard/pyramid_oereb.yml.mako').abspath(),
        input_encoding='utf-8',
        output_encoding='utf-8'
    )
    config = template.render(
        sqlalchemy_url=database,
        png_root_dir='',
        print_backend=print_backend,
        print_url=print_url
    )
    pyramid_oereb_yml = open(name, 'wb+')
    pyramid_oereb_yml.write(config)
    pyramid_oereb_yml.close()

    # Copy static files
    logo_oereb_path_de = AssetResolver('pyramid_oereb').resolve(
        'standard/{name}'.format(name=logo_oereb_name_de)
    ).abspath()
    logo_oereb_path_fr = AssetResolver('pyramid_oereb').resolve(
        'standard/{name}'.format(name=logo_oereb_name_fr)
    ).abspath()
    logo_oereb_path_it = AssetResolver('pyramid_oereb').resolve(
        'standard/{name}'.format(name=logo_oereb_name_it)
    ).abspath()
    logo_confederation_path = AssetResolver('pyramid_oereb').resolve(
        'standard/{name}'.format(name=logo_confederation_name)
    ).abspath()
    logo_sample_path = AssetResolver('pyramid_oereb').resolve(
        'standard/{name}'.format(name=logo_canton_name)
    ).abspath()
    target_path = os.path.abspath('{path}{sep}{name}'.format(
        path=os.getcwd(), name=logo_oereb_name_de, sep=os.sep)
    )
    copyfile(logo_oereb_path_de, target_path)
    target_path = os.path.abspath('{path}{sep}{name}'.format(
        path=os.getcwd(), name=logo_oereb_name_fr, sep=os.sep)
    )
    copyfile(logo_oereb_path_fr, target_path)
    target_path = os.path.abspath('{path}{sep}{name}'.format(
        path=os.getcwd(), name=logo_oereb_name_it, sep=os.sep)
    )
    copyfile(logo_oereb_path_it, target_path)
    target_path = os.path.abspath('{path}{sep}{name}'.format(
        path=os.getcwd(), name=logo_confederation_name, sep=os.sep)
    )
    copyfile(logo_confederation_path, target_path)
    target_path = os.path.abspath('{path}{sep}{name}'.format(
        path=os.getcwd(), name=logo_canton_name, sep=os.sep)
    )
    copyfile(logo_sample_path, target_path)


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
    _create_standard_yaml_config_(name=options.name, database=options.database,
                                  print_backend=options.print_backend)
