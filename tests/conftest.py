# -*- coding: utf-8 -*-
from contextlib import contextmanager

from mako.lookup import TemplateLookup
from pyramid.path import DottedNameResolver, AssetResolver
from pyramid.testing import DummyRequest, testConfig
import pytest

from pyramid_oereb import ExtractReader
from pyramid_oereb import MunicipalityReader
from pyramid_oereb import ExclusionOfLiabilityReader
from pyramid_oereb import GlossaryReader
from pyramid_oereb import Processor
from pyramid_oereb import RealEstateReader
from pyramid_oereb.lib.records.law_status import LawStatusRecord
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


@pytest.fixture
def xml_templates():
    a = AssetResolver('pyramid_oereb')
    resolver = a.resolve('lib/renderer/extract/templates/xml')
    templates = TemplateLookup(
        directories=[resolver.abspath()],
        output_encoding='utf-8',
        input_encoding='utf-8'
    )
    return templates


@pytest.fixture
def xml_schema():
    a = AssetResolver('tests')
    resolver = a.resolve('resources/Extract.xsd')
    return open(resolver.abspath())


@pytest.fixture(scope='module')
def config():
    Config._config = None
    Config.init(pyramid_oereb_test_yml, 'pyramid_oereb')
    return Config


@contextmanager
def pyramid_oereb_test_config():
    with testConfig() as pyramid_config:
        pyramid_config.include('pyramid_oereb.routes')
        yield pyramid_config


@pytest.fixture(scope='module')
def law_status(config):
    assert isinstance(config._config, dict)
    return LawStatusRecord.from_config(u'inForce')


class MockRequest(DummyRequest):
    def __init__(self, current_route_url=None):
        super(MockRequest, self).__init__()

        self._current_route_url = current_route_url

        Config._config = None
        Config.init(pyramid_oereb_test_yml, 'pyramid_oereb')

        real_estate_config = Config.get_real_estate_config()
        municipality_config = Config.get_municipality_config()
        exclusion_of_liability_config = Config.get_exclusion_of_liability_config()
        glossary_config = Config.get_glossary_config()
        extract = Config.get_extract_config()
        certification = extract.get('certification')
        certification_at_web = extract.get('certification_at_web')
        logos = Config.get_logo_config()
        plr_cadastre_authority = Config.get_plr_cadastre_authority()

        real_estate_reader = RealEstateReader(
            real_estate_config.get('source').get('class'),
            **real_estate_config.get('source').get('params')
        )

        municipality_reader = MunicipalityReader(
            municipality_config.get('source').get('class'),
            **municipality_config.get('source').get('params')
        )

        exclusion_of_liability_reader = ExclusionOfLiabilityReader(
            exclusion_of_liability_config.get('source').get('class'),
            **exclusion_of_liability_config.get('source').get('params')
        )

        glossary_reader = GlossaryReader(
            glossary_config.get('source').get('class'),
            **glossary_config.get('source').get('params')
        )

        plr_sources = []
        for plr in Config.get('plrs'):
            plr_source_class = DottedNameResolver().maybe_resolve(plr.get('source').get('class'))
            plr_sources.append(plr_source_class(**plr))

        extract_reader = ExtractReader(
            plr_sources,
            plr_cadastre_authority,
            logos,
            certification,
            certification_at_web
        )
        self.processor = Processor(
            real_estate_reader=real_estate_reader,
            municipality_reader=municipality_reader,
            exclusion_of_liability_reader=exclusion_of_liability_reader,
            glossary_reader=glossary_reader,
            plr_sources=plr_sources,
            extract_reader=extract_reader,
        )

    @property
    def pyramid_oereb_processor(self):
        return self.processor

    def current_route_url(self, *elements, **kw):
        if self._current_route_url:
            return self._current_route_url
        else:
            return super(MockRequest, self).current_route_url(*elements, **kw)


# Set up test database
create_tables_from_standard_configuration(pyramid_oereb_test_yml)
dummy_data = DummyData(config())
dummy_data.init()
