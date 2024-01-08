# -*- coding: utf-8 -*-
import optparse
import logging

from pyramid_oereb.contrib.data_sources.create_tables import \
    create_tables_from_standard_configuration


logging.basicConfig()
log = logging.getLogger(__name__)


def create_standard_tables():
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
    parser.add_option(
        '-w', '--over-write',
        dest='append_to_sql',
        action='store_true',
        default=False,
        help='Setting this will overwrite the given sql-file (defaults to append to the file).'
    )

    options, args = parser.parse_args()
    if not options.configuration:
        parser.error('No configuration file set.')
    if not options.sql_file:
        parser.error('No sql filename specified.')

    config_source = 'pyramid_oereb.contrib.data_sources.standard.sources.plr.DatabaseSource'

    append_to_sql = 'w' if options.append_to_sql else 'a'
    with open(options.sql_file, append_to_sql) as sql_file:
        create_tables_from_standard_configuration(
            configuration_yaml_path=options.configuration,
            source_class=config_source,
            section=options.section,
            c2ctemplate_style=options.c2ctemplate_style,
            sql_file=sql_file
        )
