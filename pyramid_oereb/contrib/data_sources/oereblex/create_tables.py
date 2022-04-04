# -*- coding: utf-8 -*-
import optparse
import logging

from pyramid_oereb.contrib.data_sources.standard.create_tables import \
    create_tables_from_standard_configuration


logging.basicConfig()
log = logging.getLogger(__name__)


def create_oereblex_tables():
    parser = optparse.OptionParser(
        usage='usage: %prog [options]',
        description='Create all content for the standard database'
    )
    parser.add_option(
        '-c', '--configuration',
        dest='configuration',
        metavar='YAML',
        type='string',
        help='The absolute path to the configuration yaml file.'
    )
    parser.add_option(
        '-s', '--section',
        dest='section',
        metavar='SECTION',
        type='string',
        default='pyramid_oereb',
        help='The section which contains configuration (default is: pyramid_oereb).'
    )
    parser.add_option(
        '-T', '--tables-only',
        dest='tables_only',
        action='store_true',
        default=False,
        help='Use this flag to skip the creation of the schema.'
    )
    parser.add_option(
        '--sql-file',
        type='string',
        help='Generate an SQL file.'
    )
    parser.add_option(
        '--c2ctemplate-style',
        dest='c2ctemplate_style',
        action='store_true',
        default=False,
        help='Is the yaml file using a c2ctemplate style (starting with vars)'
    )
    options, args = parser.parse_args()
    if not options.configuration:
        parser.error('No configuration file set.')

    if options.sql_file is None:
        create_tables_from_standard_configuration(
            configuration_yaml_path=options.configuration,
            source_class='pyramid_oereb.contrib.data_sources.oereblex.sources.plr_oereblex.DatabaseOEREBlexSource',
            section=options.section,
            c2ctemplate_style=options.c2ctemplate_style,
            tables_only=options.tables_only
        )
    else:
        with open(options.sql_file, 'w') as sql_file:
            create_tables_from_standard_configuration(
                configuration_yaml_path=options.configuration,
                source_class='pyramid_oereb.contrib.data_sources.oereblex.sources.plr_oereblex.DatabaseOEREBlexSource',
                section=options.section,
                c2ctemplate_style=options.c2ctemplate_style,
                sql_file=sql_file
            )
