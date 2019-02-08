# -*- coding: utf-8 -*-
import os
import shutil

from logging import Logger

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pyramid_oereb.standard.models import airports_security_zone_plans
from pyramid_oereb.standard.xtf_import import FederalTopic


yaml_file = 'pyramid_oereb/standard/pyramid_oereb.yml'


def test_init():
    loader = FederalTopic(yaml_file, 'AirportsSecurityZonePlans')
    assert isinstance(loader._log, Logger)
    assert isinstance(loader._settings, dict)
    assert len(loader._settings.get('plrs')) == 17
    assert loader._topic_settings.get('code') == 'AirportsSecurityZonePlans'
    assert loader._connection.startswith('postgresql://')
    assert loader._models == airports_security_zone_plans
    assert len(loader._file_id) == 36
    assert loader._checksum is None
    assert loader._data_integration_office_id is None


def test_unzip_cleanup():
    loader = FederalTopic(yaml_file, 'AirportsSecurityZonePlans')

    zip_file = os.path.join(loader._tmp_dir, '{0}.zip'.format(loader._file_id))
    zip_path = os.path.join(loader._tmp_dir, '{0}'.format(loader._file_id))
    shutil.copyfile('tests/resources/data.zip', zip_file)
    assert os.path.isfile(zip_file)
    loader.unzip_data()
    assert os.path.isdir(zip_path)
    loader.cleanup_files()
    assert not os.path.isfile(zip_file)
    assert not os.path.isdir(zip_path)


def test_collect_files():
    loader = FederalTopic(yaml_file, 'AirportsSecurityZonePlans')
    zip_file = os.path.join(loader._tmp_dir, '{0}.zip'.format(loader._file_id))
    zip_path = os.path.join(loader._tmp_dir, '{0}'.format(loader._file_id))
    shutil.copy('tests/resources/data.zip', zip_file)
    loader.unzip_data()
    files = loader.collect_files()
    assert files[0] == os.path.join(zip_path, 'OeREBKRM_V1_1_Gesetze_20180501.xml')
    assert files[1] == os.path.join(zip_path, 'ch.bazl.sicherheitszonenplan.oereb_20131118.xtf')
    loader.cleanup_files()


def test_read_checksum():
    loader = FederalTopic(yaml_file, 'AirportsSecurityZonePlans')
    zip_file = os.path.join(loader._tmp_dir, '{0}.zip'.format(loader._file_id))
    shutil.copy('tests/resources/data.zip', zip_file)
    loader.unzip_data()
    loader.read_checksum()
    assert loader._checksum == '45d215bd701c63d372e99630fb6ce04f'
    loader.cleanup_files()


def test_load():
    def check_counts(loader, schema):
        engine = create_engine(loader._connection)
        connection = engine.connect()
        try:
            count_plrs = connection.execute('SELECT COUNT(*) FROM {0}.{1}'.format(
                schema,
                'public_law_restriction'
            )).first()[0]
            count_geometries = connection.execute('SELECT COUNT(*) FROM {0}.{1}'.format(
                schema,
                'geometry'
            )).first()[0]
            count_documents = connection.execute('SELECT COUNT(*) FROM {0}.{1}'.format(
                schema,
                'document'
            )).first()[0]
            checksum = connection.execute('SELECT checksum FROM {0}.{1}'.format(
                schema,
                'data_integration'
            )).first()[0]
        finally:
            connection.close()
        assert count_plrs == 17
        assert count_geometries == 36
        assert count_documents == 100
        assert checksum == loader._checksum
    schema = 'airports_security_zone_plans'
    loader = FederalTopic(yaml_file, 'AirportsSecurityZonePlans')
    zip_file = os.path.join(loader._tmp_dir, '{0}.zip'.format(loader._file_id))
    shutil.copy('tests/resources/data.zip', zip_file)
    loader.unzip_data()
    loader.read_checksum()
    files = loader.collect_files()
    loader.load(files)
    check_counts(loader, schema)
    loader.load(files)
    check_counts(loader, schema)
    engine = create_engine(loader._connection)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        session.execute('UPDATE {0}.{1} SET checksum = \'foo\''.format(
            schema,
            'data_integration'
        ))
        session.commit()
    finally:
        session.close()
    loader.load(files)
    check_counts(loader, schema)
    loader.cleanup_files()
