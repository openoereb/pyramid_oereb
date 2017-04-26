# -*- coding: utf-8 -*-
from pyramid.testing import DummyRequest

from pyramid_oereb import ExtractReader
from pyramid_oereb import MunicipalityReader
from pyramid_oereb import PlrStandardDatabaseSource
from pyramid_oereb import Processor
from pyramid_oereb import RealEstateReader
from pyramid_oereb.lib.config import parse, ConfigReader

db_url = parse('pyramid_oereb_test.yml', 'pyramid_oereb').get('db_connection')
config_reader = ConfigReader('pyramid_oereb_test.yml', 'pyramid_oereb')


class MockRequest(DummyRequest):
    def __init__(self):
        super(MockRequest, self).__init__()
        real_estate_config = config_reader.get_real_estate_config()
        municipality_config = config_reader.get_municipality_config()

        real_estate_reader = RealEstateReader(
            real_estate_config.get('source').get('class'),
            **real_estate_config.get('source').get('params')
        )

        municipality_reader = MunicipalityReader(
            municipality_config.get('source').get('class'),
            **municipality_config.get('source').get('params')
        )

        # TODO: Make this more configurable, cause it is only useful for standard config now
        plr_sources = []
        for plr in config_reader.get('plrs'):
            plr['db_connection'] = config_reader.get('db_connection')
            plr_sources.append(PlrStandardDatabaseSource(**plr))

        extract_reader = ExtractReader(
            plr_sources
        )
        self.processor = Processor(
            real_estate_reader,
            municipality_reader,
            plr_sources,
            extract_reader
        )

    @property
    def pyramid_oereb_processor(self):
        return self.processor
