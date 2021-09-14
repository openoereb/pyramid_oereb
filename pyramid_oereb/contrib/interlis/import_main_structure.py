# -*- coding: utf-8 -*-

import subprocess
import requests
import os
import sqlalchemy as sa
from sqlalchemy import create_engine
from geoalchemy2.types import Geometry as GeoAlchemyGeometry


# file and directories
config_yaml = 'import_theme_transfer_structure.yml'
download_dir = '/home/michael/Projects/oereb_ili_import'

# ili2pg parameters
ili2pg_jar = '/home/michael/Software/ILI/ili2pg-4.5.0/ili2pg-4.5.0.jar'
dbhost = 'localhost'
dbport = '5432'
dbdatabase = 'federal_themes'
dbusr = 'federal_themes'
dbpwd = 'federal_themes'
db_mainschema = 'oereb_main'
srid = 2056

# create db schema for OeREBKRMkvs_V2_0
env = dict(os.environ)

subprocess.call(['java',
                 '-jar',
                 ili2pg_jar,
                 '--schemaimport',
                 '--dbhost', dbhost,
                 '--dbport', dbport,
                 '--dbdatabase', dbdatabase,
                 '--dbusr', dbusr,
                 '--dbpwd', dbpwd,
                 '--dbschema', db_mainschema,
                 '--defaultSrsAuth', 'EPSG', '--defaultSrsCode', '2056',
                 '--createFk', '--createFkIdx', '--createGeomIdx',
                 '--createTidCol', '--createBasketCol', '--createDatasetCol', '--createTidCol',
                 '--createTypeDiscriminator',
                 '--createImportTabs', '--createMetaInfo', '--createNumChecks', '--createUnique',
                 '--models', 'OeREBKRMkvs_V2_0'],
                env=env)


# create tables "municipality", "real_estate" and "address"
engine = create_engine('postgresql://' + dbusr + ':' + dbpwd + '@'
                       + dbhost + ':' + dbport + '/' + dbdatabase)
metadata_obj = sa.MetaData()

if not sa.inspect(engine).has_table('municipality', schema=db_mainschema):
    Municipality = sa.Table('municipality', metadata_obj,
                            sa.Column('fosnr', sa.BigInteger, primary_key=True),
                            sa.Column('name', sa.String, nullable=False),
                            sa.Column('published', sa.Date, nullable=False),
                            sa.Column('geom', GeoAlchemyGeometry('MULTIPOLYGON', srid=srid), nullable=True),
                            schema=db_mainschema)
    Municipality.create(engine, checkfirst=True)

if not sa.inspect(engine).has_table('real_estate', schema=db_mainschema):
    RealEstate = sa.Table('real_estate', metadata_obj,
                          sa.Column('id', sa.Integer, primary_key=True, autoincrement=False),
                          sa.Column('identdn', sa.String, nullable=True),
                          sa.Column('number', sa.String, nullable=True),
                          sa.Column('egrid', sa.String, nullable=True),
                          sa.Column('type', sa.String, nullable=False),
                          sa.Column('canton', sa.String, nullable=False),
                          sa.Column('municipality', sa.String, nullable=False),
                          sa.Column('subunit_of_land_register', sa.String, nullable=True),
                          sa.Column('fosnr', sa.Integer, nullable=False),
                          sa.Column('metadata_of_geographical_base_data', sa.String, nullable=True),
                          sa.Column('land_registry_area', sa.Integer, nullable=False),
                          sa.Column('limit', GeoAlchemyGeometry('MULTIPOLYGON', srid=srid)),
                          schema=db_mainschema)
    RealEstate.create(engine, checkfirst=True)

if not sa.inspect(engine).has_table('address', schema=db_mainschema):
    Address = sa.table('address', metadata_obj,
                       sa.Column('street_name', sa.Unicode, nullable=False),
                       sa.Column('street_number', sa.String, nullable=False),
                       sa.Column('zip_code', sa.Integer, nullable=False, autoincrement=False),
                       sa.Column('geom', GeoAlchemyGeometry('POINT', srid=srid)),
                       sa.PrimaryKeyConstraint('street_name', 'street_number', 'zip_code'))
    Address.create(engine, checkfirst=True)


# import laws / logos / texts / themes

xml_files = ['OeREBKRM_V2_0_Gesetze_20210414.xml',
             'OeREBKRM_V2_0_Themen_20210714.xml',
             'OeREBKRM_V2_0_Logos_20210414.xml',
             'OeREBKRM_V2_0_Texte_20210714.xml']

for xml_file in xml_files:
    dataset = xml_file.replace('.xml', '')
    url = 'https://models.geo.admin.ch/V_D/OeREB/' + xml_file
    r = requests.get(url)
    open(xml_file, 'wb').write(r.content)

    # delete data of dataset
    subprocess.call(['java',
                     '-jar',
                     ili2pg_jar,
                     '--import',
                     '--dbhost', dbhost,
                     '--dbport', dbport,
                     '--dbdatabase', dbdatabase,
                     '--dbusr', dbusr,
                     '--dbpwd', dbpwd,
                     '--dbschema', db_mainschema,
                     '--defaultSrsAuth', 'EPSG', '--defaultSrsCode', '2056',
                     '--createFk', '--createFkIdx', '--createGeomIdx',
                     '--createTidCol', '--createBasketCol', '--createDatasetCol', '--createTidCol',
                     '--createTypeDiscriminator',
                     '--createImportTabs', '--createMetaInfo', '--createNumChecks', '--createUnique',
                     '--delete',
                     '--dataset', dataset],
                    env=env)

    # import data of dataset
    subprocess.call(['java',
                     '-jar',
                     ili2pg_jar,
                     '--import',
                     '--dbhost', dbhost,
                     '--dbport', dbport,
                     '--dbdatabase', dbdatabase,
                     '--dbusr', dbusr,
                     '--dbpwd', dbpwd,
                     '--dbschema', db_mainschema,
                     '--defaultSrsAuth', 'EPSG', '--defaultSrsCode', '2056',
                     '--createFk', '--createFkIdx', '--createGeomIdx',
                     '--createTidCol', '--createBasketCol', '--createDatasetCol', '--createTidCol',
                     '--createTypeDiscriminator',
                     '--createImportTabs', '--createMetaInfo', '--createNumChecks', '--createUnique',
                     '--dataset', dataset,
                     xml_file],
                    env=env)

    os.remove(xml_file)


# add additional tables for main schema

# to be done
