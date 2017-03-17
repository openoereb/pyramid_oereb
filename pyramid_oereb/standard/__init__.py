# -*- coding: utf-8 -*-
import os
from mako.template import Template
from pyramid.path import AssetResolver
from sqlalchemy import create_engine
from pyramid_oereb.lib.config import parse


__author__ = 'Clemens Rudert'
__create_date__ = '15.03.17'


def create_models_py(configuration_yaml_path, section='pyramid_oereb'):
    template = Template(
        filename=AssetResolver('pyramid_oereb').resolve('standard/templates/models.py.mako').abspath()
    )
    content = template.render(**parse(configuration_yaml_path, section))
    models_path = '{path}/models.py'.format(
        path=AssetResolver('pyramid_oereb').resolve('').abspath()
    )
    if os.path.exists(models_path):
        os.remove(models_path)
    models_file = open(models_path, 'w')
    models_file.write(content)
    models_file.close()


def create_tables(configuration_yaml_path, section='pyramid_oereb'):
    from pyramid_oereb.models import Base
    config = parse(configuration_yaml_path, section)
    engine = create_engine(config.get('db_connection'), echo=True)
    connection = engine.connect()
    for schema in config.get('plrs'):
        connection.execute('CREATE SCHEMA {name};'.format(name=schema.get('name')))
    connection.close()
    Base.metadata.create_all(engine)


def drop_tables(configuration_yaml_path, section='pyramid_oereb'):
    from pyramid_oereb.models import Base
    config = parse(configuration_yaml_path, section)
    engine = create_engine(config.get('db_connection'), echo=True)
    Base.metadata.drop_all(engine)
    connection = engine.connect()
    for schema in config.get('plrs'):
        connection.execute('DROP SCHEMA IF EXISTS {name};'.format(name=schema.get('name')))
    connection.close()
