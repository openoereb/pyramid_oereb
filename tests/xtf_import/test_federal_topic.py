# -*- coding: utf-8 -*-
import os
import shutil
import pytest

from logging import Logger

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pyramid_oereb.core.config import Config
from pyramid_oereb.contrib.data_sources.standard.xtf_import import FederalTopic
from pyramid_oereb.contrib.data_sources.standard.models.theme import Models

yaml_file = 'pyramid_oereb/standard/pyramid_oereb.yml'


@pytest.mark.run(order=-1)
def test_init():
    Config._config = None
    loader = FederalTopic(yaml_file, 'ch.Sicherheitszonenplan')
    assert isinstance(loader._log, Logger)
    assert isinstance(loader._settings, dict)
    assert len(loader._settings.get('plrs')) == 17
    assert loader._topic_settings.get('code') == 'ch.Sicherheitszonenplan'
    assert loader._connection.startswith('postgresql://')
    assert isinstance(loader._models, Models)
    assert len(loader._file_id) == 36
    assert loader._checksum is None
    assert loader._data_integration_office_id is None


@pytest.mark.run(order=-1)
def test_unzip_cleanup():
    Config._config = None
    loader = FederalTopic(yaml_file, 'ch.Sicherheitszonenplan')

    zip_file = os.path.join(loader._tmp_dir, '{0}.zip'.format(loader._file_id))
    zip_path = os.path.join(loader._tmp_dir, '{0}'.format(loader._file_id))
    shutil.copyfile('tests/resources/data.zip', zip_file)
    assert os.path.isfile(zip_file)
    loader.unzip_data()
    assert os.path.isdir(zip_path)
    loader.cleanup_files()
    assert not os.path.isfile(zip_file)
    assert not os.path.isdir(zip_path)


@pytest.mark.run(order=-1)
def test_collect_files():
    Config._config = None
    loader = FederalTopic(yaml_file, 'ch.Sicherheitszonenplan')
    zip_file = os.path.join(loader._tmp_dir, '{0}.zip'.format(loader._file_id))
    zip_path = os.path.join(loader._tmp_dir, '{0}'.format(loader._file_id))
    shutil.copy('tests/resources/data.zip', zip_file)
    loader.unzip_data()
    files = loader.collect_files()
    assert files[0] == os.path.join(zip_path, 'OeREBKRM_V1_1_Gesetze_20180501.xml')
    assert files[1] == os.path.join(zip_path, 'ch.bazl.sicherheitszonenplan.oereb_20131118.xtf')
    loader.cleanup_files()


@pytest.mark.run(order=-1)
def test_read_checksum():
    Config._config = None
    loader = FederalTopic(yaml_file, 'ch.Sicherheitszonenplan')
    zip_file = os.path.join(loader._tmp_dir, '{0}.zip'.format(loader._file_id))
    shutil.copy('tests/resources/data.zip', zip_file)
    loader.unzip_data()
    loader.read_checksum()
    assert loader._checksum == '45d215bd701c63d372e99630fb6ce04f'
    loader.cleanup_files()


@pytest.mark.run(order=-1)
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
    Config._config = None
    loader = FederalTopic(yaml_file, 'ch.Sicherheitszonenplan')
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
