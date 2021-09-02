# -*- coding: utf-8 -*-
import optparse

from pyramid_oereb.lib.config import Config
from pyramid_oereb.standard.sources.plr import StandardThemeConfigParser
from pyramid_oereb.standard import drop_sql, execute_sql


def drop_tables_from_standard_configuration(configuration_yaml_path, section='pyramid_oereb'):
    """
    Drops all schemas which are defined in the passed yaml file: <section>.<plrs>.[<plr>.<code>]. The code
    must be camel case. It will be transformed to snake case and used as schema name.
    Drops all tables inside the created schemas.

    Args:
        configuration_yaml_path (str): The absolute path to the yaml file which contains the plr
            definitions.
        section (str): The section in yaml file where the plrs are configured in. Default is 'pyramid_oereb'.
    """
    if Config.get_config() is None:
        Config.init(configuration_yaml_path, section)

    main_db_connection = Config.get('app_schema').get('db_connection')
    main_schema_name = Config.get('app_schema').get('name')
    sql = drop_sql(main_schema_name)
    execute_sql(main_db_connection, sql)

    for theme_config in Config.get('plrs'):
        if theme_config.get('standard'):
            config_parser = StandardThemeConfigParser(**theme_config)
            models = config_parser.get_models()
            theme_db_connection = models.db_connection
            theme_schema_name = models.schema_name
            sql = drop_sql(theme_schema_name)
            execute_sql(theme_db_connection, sql)


def drop_standard_tables():
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
    drop_tables_from_standard_configuration(
        configuration_yaml_path=options.configuration,
        section=options.section
    )
