# -*- coding: utf-8 -*-
import os

import re

from mako.template import Template
from pyramid.path import AssetResolver, DottedNameResolver
from sqlalchemy import create_engine
from sqlalchemy.schema import CreateTable
from shutil import copyfile
from pyramid_oereb.lib.config import Config


def convert_camel_case_to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def convert_camel_case_to_text_form(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1)


def _create_standard_configuration_models_py_(code, geometry_type, absolute_path, schema=None,
                                              primary_key_is_string=False):
    """
    The simplest way to get a python file containing a database definition in sqlalchemy orm way. It will
     contain all necessary definitions to produce an extract as the specification defines for the new topic.

    Args:
        code (str): The unique Code for the new model (see oereb specification for more details)
        geometry_type (str): A valid geometry type.
        absolute_path (str): The absolute Path where the genderated python file will be placed. It
            must bewriteable by the user running this command.
        schema (str): The schema name. If not specified, "name" will be used.
        primary_key_is_string (bool): The type of the primary key. You can use this to switch between STRING
            type or INTEGER type. Standard is to INTEGER => False
    """
    if primary_key_is_string:
        template = Template(
            filename=AssetResolver('pyramid_oereb').resolve(
                'standard/templates/plr_string_primary_keys.py.mako'
            ).abspath()
        )
    else:
        template = Template(
            filename=AssetResolver('pyramid_oereb').resolve(
                'standard/templates/plr_integer_primary_keys.py.mako'
            ).abspath()
        )
    name = convert_camel_case_to_snake_case(code)
    content = template.render(**{
        'topic': convert_camel_case_to_text_form(code),
        'schema_name': schema or name,
        'geometry_type': geometry_type
    })
    models_path = '{path}/{name}.py'.format(
        path=absolute_path,
        name=name
    )
    models_path = os.path.abspath(models_path)
    if os.path.exists(models_path):
        os.remove(models_path)
    models_file = open(models_path, 'w+')
    models_file.write(content)
    models_file.close()


def create_tables_from_standard_configuration(
        configuration_yaml_path, section='pyramid_oereb', tables_only=False, sql_file=None):
    """
    Creates all schemas which are defined in the passed yaml file: <section>.<plrs>.[<plr>.<code>]. The code
    must be camel case. It will be transformed to snake case and used as schema name.
    Creates all tables inside the created schemas. This only affects the sqlalchemy models which are defined
    with the Base class from pyramid_oereb.standard.models.

    Args:
        configuration_yaml_path (str): The absolute path to the yaml file which contains the plr
            definitions.
        section (str): The section in yaml file where the plrs are configured in. Default is 'pyramid_oereb'.
        tables_only (bool): True to skip creation of schema. Default is False.
        sql_file (file): the file to generate. Default is None (in the database).
    """
    if Config.get_config() is None:
        Config.init(configuration_yaml_path, section)

    main_schema_engine = create_engine(Config.get('app_schema').get('db_connection'), echo=True)
    if sql_file is None:
        if not tables_only:
            main_schema_connection = main_schema_engine.connect()
            try:
                main_schema_connection.execute(
                    'CREATE SCHEMA IF NOT EXISTS {name};'.format(name=Config.get('app_schema').get('name'))
                )
            finally:
                main_schema_connection.close()
    else:
        sql_file.write('CREATE SCHEMA {name};\n'.format(name=Config.get('app_schema').get('name')))

    main_base_class = DottedNameResolver().maybe_resolve('{package}.Base'.format(
        package=Config.get('app_schema').get('models')
    ))
    if sql_file is None:
        main_base_class.metadata.create_all(main_schema_engine)
    else:
        for table in main_base_class.metadata.sorted_tables:
            create_table = str(CreateTable(table).compile(main_schema_engine))\
                .replace('DATETIME', 'timestamp')
            sql_file.write('{};\n'.format(create_table))

    for schema in Config.get('plrs'):

        plr_schema_engine = create_engine(schema.get('source').get('params').get('db_connection'), echo=True)

        if sql_file is None:
            if schema.get('standard'):

                if not tables_only:
                    plr_schema_connection = plr_schema_engine.connect()
                    try:
                        plr_schema_connection.execute('CREATE SCHEMA IF NOT EXISTS {name};'.format(
                            name=convert_camel_case_to_snake_case(schema.get('code')))
                        )
                    finally:
                        plr_schema_connection.close()

                plr_base = DottedNameResolver().maybe_resolve('{package}.Base'.format(
                    package=schema.get('source').get('params').get('models')
                ))
                plr_base.metadata.create_all(plr_schema_engine)

        else:
            plr_base = DottedNameResolver().maybe_resolve('{package}.Base'.format(
                package=schema.get('source').get('params').get('models')
            ))
            sql_file.write('CREATE SCHEMA {name};\n'.format(
                name=convert_camel_case_to_snake_case(schema.get('code')))
            )
            for table in plr_base.metadata.sorted_tables:
                create_table = str(CreateTable(table).compile(plr_schema_engine))\
                    .replace('DATETIME', 'timestamp')
                sql_file.write('{};\n'.format(create_table))


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
    main_schema_engine = create_engine(Config.get('app_schema').get('db_connection'), echo=True)
    main_schema_connection = main_schema_engine.connect()
    main_schema_connection.execute('DROP SCHEMA IF EXISTS {name} CASCADE;'.format(
        name=Config.get('app_schema').get('name'))
    )
    main_schema_connection.close()
    for schema in Config.get('plrs'):
        if schema.get('standard'):
            plr_schema_engine = create_engine(schema.get('source').get('params').get('db_connection'),
                                              echo=True)
            plr_schema_connection = plr_schema_engine.connect()
            plr_schema_connection.execute('DROP SCHEMA IF EXISTS {name} CASCADE;'.format(
                name=convert_camel_case_to_snake_case(schema.get('code')))
            )
            plr_schema_connection.close()


def _create_standard_yaml_config_(name='pyramid_oereb_standard.yml',
                                  database='postgresql://postgres:password@localhost/pyramid_oereb',
                                  print_backend='MapFishPrint'):
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
    config = template.render(sqlalchemy_url=database, png_root_dir='', print_backend=print_backend)
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
