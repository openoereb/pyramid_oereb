# -*- coding: iso-8859-1 -*-

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


__author__ = 'Clemens Rudert'
__create_date__ = '15.03.17'

config = {
    'schemas': [
        {
            'name': 'plr73',
            'geometry_type': 'LINESTRING',
            'label': u'Nutzungsplanung'
        }, {
            'name': 'plr87',
            'geometry_type': 'LINESTRING',
            'label': u'Projektierungszonen Nationalstrassen'
        }, {
            'name': 'plr88',
            'geometry_type': 'LINESTRING',
            'label': u'Baulinien Nationalstrassen'
        }, {
            'name': 'plr97',
            'geometry_type': 'LINESTRING',
            'label': u'Baulinien Eisenbahnanlagen'
        }, {
            'name': 'plr96',
            'geometry_type': 'POLYGON',
            'label': u'Projektierungszonen Eisenbahnanlagen'
        }, {
            'name': 'plr103',
            'geometry_type': 'POLYGON',
            'label': u'Projektierungszonen Flughafenanlagen'
        }, {
            'name': 'plr104',
            'geometry_type': 'POLYGON',
            'label': u'Baulinien Flughafenanlagen'
        }, {
            'name': 'plr108',
            'geometry_type': 'POLYGON',
            'label': u'Sicherheitszonenplan Flughafen'
        }, {
            'name': 'plr116',
            'geometry_type': 'POLYGON',
            'label': u'Belastete Standorte'
        }, {
            'name': 'plr117',
            'geometry_type': 'POLYGON',
            'label': u'Belastete Standorte Militär'
        }, {
            'name': 'plr118',
            'geometry_type': 'POLYGON',
            'label': u'Belastete Standorte Zivile Flugplätze'
        }, {
            'name': 'plr119',
            'geometry_type': 'POLYGON',
            'label': u'Belastete Standorte Öeffentlicher Verkehr'
        }, {
            'name': 'plr131',
            'geometry_type': 'POLYGON',
            'label': u'Grundwasserschutzzonen'
        }, {
            'name': 'plr132',
            'geometry_type': 'POLYGON',
            'label': u'Grundwasserschutzareale'
        }, {
            'name': 'plr145',
            'geometry_type': 'POLYGON',
            'label': u'Lärmemfindlichkeitsstufen'
        }, {
            'name': 'plr157',
            'geometry_type': 'POLYGON',
            'label': u'Waldgrenzen'
        }, {
            'name': 'plr159',
            'geometry_type': 'POLYGON',
            'label': u'Waldabstandslinien'
        }
    ],
    'srid': 2056
}


def create_models_py():
    template = Template(
        filename=AssetResolver('pyramid_oereb').resolve('standard/templates/models.py.mako').abspath()
    )
    content = template.render(**config)
    models_path = '{path}/models.py'.format(
        path=AssetResolver('pyramid_oereb').resolve('').abspath()
    )
    if os.path.exists(models_path):
        os.remove(models_path)
    models_file = open(models_path, 'w')
    models_file.write(content)
    models_file.close()


def create_tables(connection_string='postgresql://postgres:password@172.17.0.2/pyramid_oereb'):
    from pyramid_oereb.models import Base
    engine = create_engine(connection_string, echo=True)
    connection = engine.connect()
    for schema in config.get('schemas'):
        connection.execute('CREATE SCHEMA {name};'.format(name=schema.get('name')))
    connection.close()
    Base.metadata.create_all(engine)


def drop_tables(connection_string='postgresql://postgres:password@172.17.0.2/pyramid_oereb'):
    from pyramid_oereb.models import Base
    engine = create_engine(connection_string, echo=True)
    Base.metadata.drop_all(engine)
    connection = engine.connect()
    for schema in config.get('schemas'):
        connection.execute('DROP SCHEMA IF EXISTS {name};'.format(name=schema.get('name')))
    connection.close()
