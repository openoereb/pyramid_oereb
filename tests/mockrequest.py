# -*- coding: utf-8 -*-
from pyramid.path import DottedNameResolver
from pyramid.testing import DummyRequest

from pyramid_oereb import ExtractReader
from pyramid_oereb import MunicipalityReader
from pyramid_oereb import ExclusionOfLiabilityReader
from pyramid_oereb import GlossaryReader
from pyramid_oereb import Processor
from pyramid_oereb import RealEstateReader

from pyramid_oereb.lib.config import Config
from pyramid_oereb.views.webservice import Parameter


class MockParameter(Parameter):
    def __init__(self):
        super(MockParameter, self).__init__('JSON', flavour='REDUCED', with_geometry=False, images=False)


class MockRequest(DummyRequest):
    def __init__(self, current_route_url=None):
        super(MockRequest, self).__init__()

        self._current_route_url = current_route_url

        real_estate_config = Config.get_real_estate_config()
        municipality_config = Config.get_municipality_config()
        exclusion_of_liability_config = Config.get_exclusion_of_liability_config()
        glossary_config = Config.get_glossary_config()
        extract = Config.get_extract_config()
        certification = extract.get('certification')
        certification_at_web = extract.get('certification_at_web')
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
