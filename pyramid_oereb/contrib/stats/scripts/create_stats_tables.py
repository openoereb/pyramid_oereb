# -*- coding: utf-8 -*-
from c2cwsgiutils.sqlalchemylogger.handlers import SQLAlchemyHandler
from pyramid_oereb.core.config import Config
import configparser
import ast
from mako.template import Template
import os
import optparse

SCRIPT_FOLDER = os.path.dirname(os.path.abspath(__file__))


def create_stats_tables():
    parser = optparse.OptionParser(
        usage='usage: %prog [options]',
        description='creates database and views for sqlalchemylogger'
    )
    parser.add_option(
        '-c', '--config',
        dest='configfile',
        metavar='INI_FILE',
        type='string',
        help='The same config .ini file used to initialize the sqlalchemylogger handler'
    )
    parser.add_option(
        '-s', '--section',
        dest='config_section',
        metavar='SECTION_NAME',
        default='handler_sqlalchemylogger',
        help='section in the ini-file. Default = "handler_sqlalchemylogger"'
    )
    parser.add_option(
        '-a', '--args',
        dest='config_sql_args',
        metavar='SUBSECTION',
        default='args',
        help='subsection in the ini-file. Default = "args"'
    )
    options, _ = parser.parse_args()
    if not options.configfile:
        parser.error('No configfile set')
    _create_views(config_file=options.configfile,
                  config_section=options.config_section,
                  config_sql_args=options.config_sql_args)


def _create_views(config_file,
                  config_section='handler_sqlalchemylogger',
                  config_sql_args='args'):
    config = configparser.ConfigParser(Config.get_db_vars_from_env())
    config.read(config_file)
    schema_name = ast.literal_eval(config[config_section][config_sql_args])[0]['tableargs']['schema']
    tablename = ast.literal_eval(config[config_section][config_sql_args])[0]['tablename']
    fake_handler = SQLAlchemyHandler(ast.literal_eval(config[config_section][config_sql_args])[0])
    fake_handler.create_db()
    create_view_sql = Template(filename='{}/templates/views.sql.mako'.format(SCRIPT_FOLDER))
    fake_handler.session.execute(create_view_sql.render(schema_name=schema_name, tablename=tablename))
    fake_handler.session.commit()
