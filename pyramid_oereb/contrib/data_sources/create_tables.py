# -*- coding: utf-8 -*-
import optparse
import logging

from pyramid.path import DottedNameResolver

from pyramid_oereb.core.config import Config
from pyramid_oereb.contrib.data_sources.standard.sources.plr import StandardThemeConfigParser
from pyramid_oereb.contrib.data_sources.standard import tables, create_sql, create_tables_sql

logging.basicConfig()
log = logging.getLogger(__name__)


def create_theme_tables_(theme_config, source_class, tables_only=False, sql_file=None, if_not_exists=False):
    """
    Create the tables for a specific theme.

    Args:
        theme_config (dict): The configuration section for the specific theme.
        source_class (): The source from which the table is created.
                         This can be the standard source or the oereblex source.
                         Only the Themes configured with this source are created.
        tables_only (bool): True to skip creation of schema. Default is False.
        sql_file (file): The file to generate. Default is None (in the database).
        if_not_exists (bool): create Schema with the flag `IF NOT EXISTS`
    """
    if theme_config['source']['class'] == source_class:
        config_parser = StandardThemeConfigParser(**theme_config)
        models = config_parser.get_models()
        theme_schema_name = models.schema_name
        theme_tables = tables(models.Base)
        if tables_only:
            sql = create_tables_sql(theme_tables, if_not_exists)
        else:
            sql = create_sql(theme_schema_name, theme_tables, if_not_exists)

        sql_file.write(sql)


def create_tables_from_standard_configuration(
        configuration_yaml_path,
        source_class,
        section='pyramid_oereb',
        c2ctemplate_style=False,
        tables_only=False,
        sql_file=None,
        if_not_exists=False):
    """
    Creates all schemas which are defined in the passed yaml file: <section>.<plrs>.[<plr>.<code>]. The code
    must be camel case. It will be transformed to snake case and used as schema name.
    Creates all tables inside the created schemas. This only affects the sqlalchemy models which are defined
    with the Base class from pyramid_oereb.standard.models.

    Args:
        configuration_yaml_path (str): The absolute path to the yaml file which contains the plr
            definitions.
        section (str): The section in yaml file where the plrs are configured in. Default is 'pyramid_oereb'.
        c2ctemplate_style (bool): True if the yaml use a c2c template style (vars.[section]).
            Default is False.
        tables_only (bool): True to skip creation of schema. Default is False.
        sql_file (file): the file to generate. Default is None (in the database).
        if_not_exists (bool): create Schema with the flag `IF NOT EXISTS`
    """
    if Config.get_config() is None:
        Config.init(configuration_yaml_path, section, c2ctemplate_style)

    for theme_config in Config.get('plrs'):
        create_theme_tables_(
            theme_config,
            source_class,
            tables_only=tables_only,
            sql_file=sql_file,
            if_not_exists=if_not_exists
        )


def create_main_schema_from_configuration_(
        configuration_yaml_path,
        section='pyramid_oereb',
        c2ctemplate_style=False,
        tables_only=False,
        sql_file=None,
        if_not_exists=False):
    """
    Creates all schemas which are defined in the passed yaml file: <section>.<plrs>.[<plr>.<code>]. The code
    must be camel case. It will be transformed to snake case and used as schema name.
    Creates all tables inside the created schemas. This only affects the sqlalchemy models which are defined
    with the Base class from pyramid_oereb.standard.models.

    Args:
        configuration_yaml_path (str): The absolute path to the yaml file which contains the plr
            definitions.
        section (str): The section in yaml file where the plrs are configured in. Default is 'pyramid_oereb'.
        c2ctemplate_style (bool): True if the yaml use a c2c template style (vars.[section]).
            Default is False.
        tables_only (bool): True to skip creation of schema. Default is False.
        sql_file (file): the file to generate. Default is None (in the database).
        if_not_exists (bool): create Schema with the flag `IF NOT EXISTS`
    """
    if Config.get_config() is None:
        Config.init(configuration_yaml_path, section, c2ctemplate_style)

    main_base_class = DottedNameResolver().maybe_resolve('{package}.Base'.format(
        package=Config.get('app_schema').get('models')
    ))
    main_schema_name = Config.get('app_schema').get('name')
    main_tables = tables(main_base_class)
    if tables_only:
        sql = create_tables_sql(main_tables, if_not_exists)
    else:
        sql = create_sql(main_schema_name, main_tables, if_not_exists)

    sql_file.write(sql)


def create_main_schema_tables():
    parser = optparse.OptionParser(
        usage='usage: %prog [options]',
        description='Create the main schema with table and its content \
            used in the standard database'
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

    if Config.get_config() is None:
        Config.init(
            options.configuration,
            options.section,
            options.c2ctemplate_style
        )

    main_config = Config.get('app_schema').get('name')
    if main_config is None:
        parser.error('The main config is not found in configuration.')

    if options.sql_file is None:
        create_main_schema_from_configuration_(
            configuration_yaml_path=options.configuration,
            section=options.section,
            c2ctemplate_style=options.c2ctemplate_style,
            tables_only=options.tables_only
        )
    else:
        append_to_sql = 'w' if options.append_to_sql else 'a'
        with open(options.sql_file, append_to_sql) as sql_file:
            create_main_schema_from_configuration_(
                configuration_yaml_path=options.configuration,
                section=options.section,
                c2ctemplate_style=options.c2ctemplate_style,
                sql_file=sql_file
            )


def create_theme_tables():
    parser = optparse.OptionParser(
        usage='usage: %prog [options]',
        description='Create theme tables SQL'
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
        '-t', '--theme',
        dest='theme',
        metavar='CODE',
        type='string',
        help='The code of the theme to be created.'
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
        '--config-source',
        type='string',
        default='pyramid_oereb.contrib.data_sources.standard.sources.plr.DatabaseSource',
        help='Config source to use, it must be an implementation corresponding to the standard schema.'
        'Note: parameter must match the actual config; a default value is provided.'
    )
    options, args = parser.parse_args()
    if not options.configuration:
        parser.error('No configuration file set.')
    if not options.theme:
        parser.error('No theme code specified.')
    if not options.sql_file:
        parser.error('No sql filename specified.')

    if Config.get_config() is None:
        Config.init(
            options.configuration,
            options.section,
            options.c2ctemplate_style
        )

    theme_config = Config.get_theme_config_by_code(options.theme)
    if theme_config is None:
        parser.error('Specified theme not found in configuration.')

    with open(options.sql_file, 'w') as sql_file:
        create_theme_tables_(
            theme_config,
            options.config_source,
            tables_only=options.tables_only,
            sql_file=sql_file
        )
