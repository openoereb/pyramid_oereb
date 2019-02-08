# -*- coding: utf-8 -*-
from contextlib import contextmanager
from pyramid.testing import testConfig

from pyramid_oereb.lib.config import Config
from pyramid_oereb.standard import create_tables_from_standard_configuration

from tests.init_db import DummyData


params = [
    {
        'flavour': 'INVALIDFLAVOUR',
        'format': 'xml',
        'param1': 'egrid'
    },
    {
        'flavour': 'reduced',
        'format': 'INVALIDFORMAT',
        'param1': 'egrid'
    },
    {
        'flavour': 'FULL',
        'format': 'XML',
        'param1': 'egrid'
    },
    {
        'flavour': 'SIGNED',
        'format': 'JSON',
        'param1': 'egrid'
    },
    {
        'flavour': 'EMBEDDABLE',
        'format': 'PDF',
        'param1': 'egrid'
    },
    {
        'flavour': 'full',
        'format': 'PDF',
        'param1': 'GEOMETRY',
        'param2': 'egrid'
    }
]


schema_json_versions = './tests/resources/schema/20170825/versioning.json'
schema_json_extract = './tests/resources/schema/20170825/extract.json'
schema_json_extract_data = './tests/resources/schema/20170825/extractdata.json'
schema_xml_versions = './tests/resources/schema/20170825/Versioning.xsd'
schema_xml_extract = './tests/resources/schema/20170825/Extract.xsd'
schema_xml_extract_data = './tests/resources/schema/20170825/ExtractData.xsd'


pyramid_oereb_test_yml = 'pyramid_oereb/standard/pyramid_oereb.yml'


@contextmanager
def pyramid_oereb_test_config():
    with testConfig() as pyramid_config:
        pyramid_config.include('pyramid_oereb.routes')
        yield pyramid_config


# Set up test database and init the Config
Config._config = None
create_tables_from_standard_configuration(pyramid_oereb_test_yml)
dummy_data = DummyData()
dummy_data.init()
