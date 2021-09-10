# -*- coding: utf-8 -*-

import subprocess
import requests
import os


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
db_mainschema = "oereb_main"

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
