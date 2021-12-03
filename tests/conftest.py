# -*- coding: utf-8 -*-
import pytest
import json

from pyramid.testing import testConfig

from pyramid_oereb.core.config import Config

CONFIG_PATH = 'tests/resources/test_config.yml'
SCHEMA_JSON_EXTRACT_PATH = './tests/resources/schema/20170825/extract.json'

schema_json_versions = './tests/resources/schema/20170825/versioning.json'

schema_json_extract_data = './tests/resources/schema/20170825/extractdata.json'
schema_xml_versions = './tests/resources/schema/20170825/Versioning.xsd'
schema_xml_extract = './tests/resources/schema/20170825/Extract.xsd'
schema_xml_extract_data = './tests/resources/schema/20170825/ExtractData.xsd'

@pytest.fixture(scope='session')
def pyramid_test_config():
    with testConfig() as pyramid_config:
        pyramid_config.include('pyramid_oereb.routes')
        yield pyramid_config

@pytest.fixture(scope='session')
def pyramid_oereb_test_config():
  # Load the standard test configuration
  Config.init(CONFIG_PATH, configsection='pyramid_oereb', init_data=True)
  return Config

@pytest.fixture(scope='session')
def schema_json_extract():
  with open(SCHEMA_JSON_EXTRACT_PATH) as f:
        return json.loads(f.read())