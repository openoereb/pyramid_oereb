# -*- coding: utf-8 -*-

# Copyright (c) 2012 - 2016, GIS-Fachstelle des Amtes für Geoinformation des Kantons Basel-Landschaft
# All rights reserved.
#
# This program is free software and completes the GeoMapFish License for the geoview.bl.ch specific
# parts of the code. You can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# The above copyright notice and this permission notice shall be included in all copies or substantial
# portions of the Software.
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
