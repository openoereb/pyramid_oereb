# -*- coding: utf-8 -*-
import inspect
import optparse
import logging

from pyramid.config import ConfigurationError
from pyramid.path import DottedNameResolver
from sqlalchemy import create_engine

from pyramid_oereb.lib.config import Config
from pyramid_oereb.standard import create_tables_from_standard_configuration

logging.basicConfig()
log = logging.getLogger(__name__)


def _create_theme_tables(configuration_yaml_path, theme, section='pyramid_oereb', tables_only=False):
    """
    Create all tables defined in the specified module.

    Args:
        configuration_yaml_path (str): Path to the configuration file.
        theme (str): Code of the theme to create the tables for.
        section (str): Section within the specified configuration file used for pyramid_oereb. Default is
            'pyramid_oereb'.
        tables_only (bool): True to skip creation of schema. Default is False.
    """

    # Parse themes from configuration
    Config.init(configuration_yaml_path, section)
    themes = Config.get('plrs')
    if not isinstance(themes, list):
        raise ConfigurationError('No list of themes found.')

    # Find the specified theme
    found = False
    for t in themes:
        if t.get('code') == theme:

            # Check required configuration parameters
            params = t.get('source').get('params')
            if not isinstance(params, dict):
                raise ConfigurationError('Missing params property in source definition.')
            if not ('db_connection' in params and 'models' in params):
                raise ConfigurationError('Params has to contain "db_connection" and "models" properties.')

            # Create sqlalchemy engine for configured connection and load module containing models
            engine = create_engine(params.get('db_connection'), echo=True)
            models = DottedNameResolver().resolve(params.get('models'))

            if not tables_only:
                # Iterate over contained classes to collect needed schemas
                classes = inspect.getmembers(models, inspect.isclass)
                schemas = []
                create_schema_sql = 'CREATE SCHEMA IF NOT EXISTS {schema};'
                for c in classes:
                    class_ = c[1]
                    if hasattr(class_, '__table__') and class_.__table__.schema not in schemas:
                        schemas.append(class_.__table__.schema)

                # Try to create missing schemas
                connection = engine.connect()
                try:
                    for schema in schemas:
                        connection.execute(create_schema_sql.format(schema=schema))
                finally:
                    connection.close()

            # Create tables
            models.Base.metadata.create_all(engine)
            found = True
            break

    if not found:
        raise ValueError('Specified theme "{theme}" not found in configuration.'.format(theme=theme))


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
    options, args = parser.parse_args()
    if not options.configuration:
        parser.error('No configuration file set.')

    if options.sql_file is None:
        create_tables_from_standard_configuration(
            configuration_yaml_path=options.configuration,
            section=options.section,
            tables_only=options.tables_only
        )
    else:
        with open(options.sql_file, 'w') as sql_file:
            create_tables_from_standard_configuration(
                configuration_yaml_path=options.configuration,
                section=options.section,
                sql_file=sql_file
            )


def create_theme_tables():
    parser = optparse.OptionParser(
        usage='usage: %prog [options]',
        description='Create all tables for the specified theme.'
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
        metavar='THEME_CODE',
        type='string',
        help='The theme code. Has to be available in configuration!'
    )
    parser.add_option(
        '-T', '--tables-only',
        dest='tables_only',
        action='store_true',
        default=False,
        help='Use this flag to skip the creation of the schema.'
    )
    options, args = parser.parse_args()
    if not options.configuration:
        parser.error('No configuration file set.')
    if not options.theme:
        parser.error('No theme code defined.')
    try:
        _create_theme_tables(
            options.configuration,
            options.theme,
            section=options.section,
            tables_only=options.tables_only
        )
    except Exception as e:
        log.error(e)
