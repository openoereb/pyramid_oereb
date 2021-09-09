# -*- coding: utf-8 -*-

import subprocess
import requests
import yaml
import sys
import os
import glob
import zipfile
import hashlib

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

# command line arguments
theme_id = int(sys.argv[1])

# Load configuration
with open(config_yaml, "r") as f:
    themes = yaml.load(f, Loader=yaml.FullLoader)

# download zip-file / unzip
download_theme = None
for one_theme in themes:
    if theme_id == one_theme['id']:
        download_theme = one_theme
        break

r = requests.get(download_theme['download_url'])
data_dir = os.path.join(download_dir, 'data')
data_file_zip = os.path.join(download_dir, 'data.zip')

open(data_file_zip, 'wb').write(r.content)
if zipfile.is_zipfile(data_file_zip):
    with zipfile.ZipFile(data_file_zip, 'r') as zip_ref:
        zip_ref.extractall(data_dir)
else:
    raise zipfile.BadZipFile

# compute and compare md5sum
xtf_file = glob.glob(os.path.join(data_dir, "*.xtf"))
md5sum_file = glob.glob(os.path.join(data_dir, "*md5.txt"))

if len(xtf_file) != 1:
    raise RuntimeError('More than one xtf file in directory' + data_dir)
else:
    xtf_file = xtf_file[0]
if len(md5sum_file) != 1:
    raise RuntimeError('More than one md5.txt file in directory' + data_dir)
else:
    md5sum_file = md5sum_file[0]

with open(md5sum_file, 'r') as file:
    md5sum_reported = file.read().replace('\n', '')
with open(xtf_file,"rb") as f:
    bytes = f.read() # read file as bytes
    md5sum_computed = hashlib.md5(bytes).hexdigest()

if md5sum_reported != md5sum_computed:
    raise RuntimeError("Reported md5sum of downloaded xtf is not equal to computed md5sum.")


# create db schema for OeREBKRMtrsfr_V2_0
env = dict(os.environ)

subprocess.call(['java',
                 '-jar',
                 ili2pg_jar,
                 '--schemaimport',
                 '--dbhost', 'localhost',
                 '--dbport', dbport,
                 '--dbdatabase', dbdatabase,
                 '--dbusr', dbusr,
                 '--dbpwd', dbpwd,
                 '--dbschema', download_theme['theme'],
                 '--defaultSrsAuth', 'EPSG', '--defaultSrsCode', '2056',
                 '--createFk', '--createFkIdx', '--createGeomIdx',
                 '--createTidCol', '--createBasketCol', '--createDatasetCol', '--createTidCol',
                 '--createTypeDiscriminator',
                 '--createImportTabs', '--createMetaInfo', '--createNumChecks', '--createUnique',
                 '--models', 'OeREBKRMtrsfr_V2_0'],
                 env=env)


# import data from xtf into schema
subprocess.call(['java',
                 '-jar',
                 ili2pg_jar,
                 '--import',
                 '--dbhost', 'localhost',
                 '--dbport', dbport,
                 '--dbdatabase', dbdatabase,
                 '--dbusr', dbusr,
                 '--dbpwd', dbpwd,
                 '--dbschema', download_theme['schema'],
                 '--defaultSrsAuth', 'EPSG', '--defaultSrsCode', '2056',
                 '--createFk', '--createFkIdx', '--createGeomIdx',
                 '--createTidCol', '--createBasketCol', '--createDatasetCol', '--createTidCol',
                 '--createTypeDiscriminator',
                 '--createImportTabs', '--createMetaInfo', '--createNumChecks', '--createUnique',
                 '--dataset', download_theme['thema'],
                 '--replace', xtf_file],
                 env=env)

# create table "datenintegration" and "verfuegbarkeit"
subprocess.call(['docker-compose', 'exec', 'db',
                'psql', '-d', dbdatabase, '-U', dbusr,
                '-v', 'schema=' + 'download_theme["schema"]',
                '-v', 'usr=' + dbusr,
                '-f', '/data/add_tables_to_schema.sql'])

# Updata table 'datenintegration'
# To be don

# cleaning the directory
if os.path.exists(data_dir) and os.path.isdir(data_dir):
    for file_to_be_deleted in os.listdir(data_dir):
        os.remove(os.path.join(data_dir, file_to_be_deleted))
    os.rmdir(data_dir)
if os.path.exists(data_file_zip) and os.path.isfile(data_file_zip):
    os.remove(data_file_zip)
