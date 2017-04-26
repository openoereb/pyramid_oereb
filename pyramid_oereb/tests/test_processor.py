# -*- coding: utf-8 -*-
from shapely.geometry import MultiPolygon
from shapely.wkt import loads
import pytest
from pyramid_oereb.lib.processor import Processor
from pyramid_oereb.lib.records.real_estate import RealEstateRecord
from pyramid_oereb.lib.records.view_service import ViewServiceRecord
from pyramid_oereb.tests.conftest import MockRequest
from pyramid_oereb import ExtractReader
from pyramid_oereb import MunicipalityReader
from pyramid_oereb import RealEstateReader


def test_missing_params():
    with pytest.raises(TypeError):
        Processor()


def test_properties():
    request = MockRequest()
    processor = request.pyramid_oereb_processor
    assert isinstance(processor.extract_reader, ExtractReader)
    assert isinstance(processor.municipality_reader, MunicipalityReader)
    assert isinstance(processor.plr_sources, list)
    assert isinstance(processor.real_estate_reader, RealEstateReader)


def test_process():
    request = MockRequest()
    processor = request.pyramid_oereb_processor
    polygon = loads('POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))')
    view_service = ViewServiceRecord('test', 'test')
    real_estate = RealEstateRecord('Test', 'BL', 'Duggingen',
                                   1234, 1000, MultiPolygon([polygon]), view_service)
    extract_dict = processor.process(real_estate)
    assert isinstance(extract_dict, dict)
