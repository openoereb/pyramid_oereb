# -*- coding: utf-8 -*-
import os

import re

from mako.template import Template
from pyramid.path import AssetResolver, DottedNameResolver
from sqlalchemy import create_engine
from shutil import copyfile
from pyramid_oereb.lib.config import parse


def convert(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def _create_standard_configuration_models_py_(code, geometry_type, absolute_path):
    """
    The simplest way to get a python file containing a database definition in sqlalchemy orm way. It will
     contain all necessary definitions to produce an extract as the specification defines for the new topic.
    :param code: The unique Code for the new model (see oereb specification for more details)
    :type code: str
    :param geometry_type: A valid geometry type.
    :type geometry_type: str
    :param absolute_path: The absolute Path where the genderated python file will be placed. It must be
    writeable by the user running this command.
    :type absolute_path: str
    """
    template = Template(
        filename=AssetResolver('pyramid_oereb').resolve('standard/templates/plr.py.mako').abspath()
    )
    name = convert(code)
    content = template.render(**{
        'schema_name': name,
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


def _create_all_standard_models_by_yaml_(configuration_yaml_path, section='pyramid_oereb'):
    """
    This method is more a developer method. It is used to create the models python files out of the parsed
    config yaml. This is handy in developing time. Of cause it can be used for other things. But keep in mind:
    It will loop over all configured plrs in the passed config yaml and will create the desired model files in
    the packages standard folder (pyramid_oereb/standard/models/...).
    :param configuration_yaml_path: The absolute path to the yaml file which contains the plr definitions.
    :type configuration_yaml_path: str
    :param section: The section in yaml file where the plrs are configured in. Standard is 'pyramid:oereb'
    :type section: str
    """
    config = parse(configuration_yaml_path, section)
    absolute_path = AssetResolver('pyramid_oereb.standard.models').resolve('').abspath()
    for plr in config.get('plrs'):
        if plr.get('standard'):
            _create_standard_configuration_models_py_(
                plr.get('code'),
                plr.get('geometry_type'),
                absolute_path
            )


def _create_tables_from_standard_configuration_(configuration_yaml_path, section='pyramid_oereb'):
    """
    Creates all schemas which are defined in the passed yaml file: <section>.<plrs>.[<plr>.<code>]. The code
    must be camel case. It will be transformed to snake case and used as schema name.
    Creates all tables inside the created schemas. This only affects the sqlalchemy models which are defined
    with the Base class from pyramid_oereb.standard.models.
    :param configuration_yaml_path: The absolute path to the yaml file which contains the plr definitions.
    :type configuration_yaml_path: str
    :param section: The section in yaml file where the plrs are configured in. Standard is 'pyramid:oereb'
    :type section: str
    """
    config = parse(configuration_yaml_path, section)
    main_schema_engine = create_engine(config.get('app_schema').get('db_connection'), echo=True)
    main_schema_connection = main_schema_engine.connect()
    main_schema_connection.execute('CREATE SCHEMA {name};'.format(name=config.get('app_schema').get('name')))
    main_base_class = DottedNameResolver().maybe_resolve('{package}.Base'.format(
        package=config.get('app_schema').get('models')
    ))
    main_base_class.metadata.create_all(main_schema_engine)
    for schema in config.get('plrs'):
        plr_schema_engine = create_engine(schema.get('source').get('params').get('db_connection'), echo=True)
        plr_schema_connection = plr_schema_engine.connect()
        plr_schema_connection.execute('CREATE SCHEMA {name};'.format(name=convert(schema.get('code'))))
        plr_base = DottedNameResolver().maybe_resolve('{package}.Base'.format(
            package=schema.get('source').get('params').get('models')
        ))
        plr_schema_connection.close()
        plr_base.metadata.create_all(plr_schema_engine)


def _drop_tables_from_standard_configuration_(configuration_yaml_path, section='pyramid_oereb'):
    """
    Drops all schemas which are defined in the passed yaml file: <section>.<plrs>.[<plr>.<code>]. The code
    must be camel case. It will be transformed to snake case and used as schema name.
    Drops all tables inside the created schemas.
    :param configuration_yaml_path: The absolute path to the yaml file which contains the plr definitions.
    :type configuration_yaml_path: str
    :param section: The section in yaml file where the plrs are configured in. Standard is 'pyramid:oereb'
    :type section: str
    """
    config = parse(configuration_yaml_path, section)
    main_schema_engine = create_engine(config.get('app_schema').get('db_connection'), echo=True)
    main_schema_connection = main_schema_engine.connect()
    main_schema_connection.execute('DROP SCHEMA IF EXISTS {name} CASCADE;'.format(
        name=config.get('app_schema').get('name'))
    )
    main_schema_connection.close()
    for schema in config.get('plrs'):
        plr_schema_engine = create_engine(schema.get('source').get('params').get('db_connection'), echo=True)
        plr_schema_connection = plr_schema_engine.connect()
        plr_schema_connection.execute('DROP SCHEMA IF EXISTS {name} CASCADE;'.format(
            name=convert(schema.get('code')))
        )
        plr_schema_connection.close()


# TODO: remove this method after everyone switched to the new way
def _create_tables_(configuration_yaml_path, section='pyramid_oereb'):
    from pyramid_oereb.models import Base
    config = parse(configuration_yaml_path, section)
    engine = create_engine(config.get('db_connection'), echo=True)
    connection = engine.connect()
    connection.execute('CREATE SCHEMA {name};'.format(name=config.get('app_schema').get('name')))
    for schema in config.get('plrs'):
        connection.execute('CREATE SCHEMA {name};'.format(name=schema.get('name')))
    connection.close()
    Base.metadata.create_all(engine)


# TODO: remove this method after everyone switched to the new way
def _drop_tables_(configuration_yaml_path, section='pyramid_oereb'):
    from pyramid_oereb.models import Base
    config = parse(configuration_yaml_path, section)
    engine = create_engine(config.get('db_connection'), echo=True)
    Base.metadata.drop_all(engine)
    connection = engine.connect()
    connection.execute('DROP SCHEMA IF EXISTS {name};'.format(name=config.get('app_schema').get('name')))
    for schema in config.get('plrs'):
        connection.execute('DROP SCHEMA IF EXISTS {name};'.format(name=schema.get('name')))
    connection.close()


def _create_standard_yaml_config_(name='pyramid_oereb_standard.yml'):

    """
    Creates a new YAML file in the directory where it was called. This YAML file contains the standard
    configuration to run a oereb server out of the box.
    :param name: The name of the new file. Default: 'pyramid_oereb_standard.yml'
    :type: str
    """
    logo_oereb_name = 'logo_oereb.png'
    logo_confederation_name = 'logo_confederation.png'
    pyramid_oereb_yaml_name = 'pyramid_oereb.yml'
    yaml_path = AssetResolver('pyramid_oereb').resolve(
        'standard/{name}'.format(name=pyramid_oereb_yaml_name)
    ).abspath()
    logo_oereb_path = AssetResolver('pyramid_oereb').resolve(
        'standard/{name}'.format(name=logo_oereb_name)
    ).abspath()
    logo_confederation_path = AssetResolver('pyramid_oereb').resolve(
        'standard/{name}'.format(name=logo_confederation_name)
    ).abspath()
    target_path = os.path.abspath('{path}{sep}{name}'.format(path=os.getcwd(), name=name, sep=os.sep))
    copyfile(yaml_path, target_path)
    target_path = os.path.abspath('{path}{sep}{name}'.format(
        path=os.getcwd(), name=logo_oereb_name, sep=os.sep)
    )
    copyfile(logo_oereb_path, target_path)
    target_path = os.path.abspath('{path}{sep}{name}'.format(
        path=os.getcwd(), name=logo_confederation_name, sep=os.sep)
    )
    copyfile(logo_confederation_path, target_path)
