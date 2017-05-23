# -*- coding: utf-8 -*-
import pytest
from pyramid_oereb.lib.processor import Processor
from pyramid_oereb.tests.conftest import MockRequest
from pyramid_oereb import ExtractReader
from pyramid_oereb import MunicipalityReader
from pyramid_oereb import ExclusionOfLiabilityReader
from pyramid_oereb import GlossaryReader
from pyramid_oereb import RealEstateReader


def test_missing_params():
    with pytest.raises(TypeError):
        Processor()


def test_properties():
    request = MockRequest()
    processor = request.pyramid_oereb_processor
    assert isinstance(processor.extract_reader, ExtractReader)
    assert isinstance(processor.municipality_reader, MunicipalityReader)
    assert isinstance(processor.exclusion_of_liability_reader, ExclusionOfLiabilityReader)
    assert isinstance(processor.glossary_reader, GlossaryReader)
    assert isinstance(processor.plr_sources, list)
    assert isinstance(processor.real_estate_reader, RealEstateReader)


def test_process(connection):
    assert connection.closed
    request = MockRequest()
    processor = request.pyramid_oereb_processor
    real_estate = processor.real_estate_reader.read(egrid=u'TEST')
    extract = processor.process(real_estate[0])
    assert isinstance(extract.to_extract(), dict)


def test_polygon_intersection():
    """ Tests the intersection between a rectangle and a polygon where the
    intersecting polygon produces two partial geometries inside the
    rectangle of wich one should be eliminated by the tolerance check
    """

    # shapely test geometries:
    rectangle = loads('POLYGON((0 0, 0 3, 3 3, 3 0, 0 0))')
    # polygon = loads('POLYGON(1 2.5, 1 5, 5 5, 5 0, 1 0, 1 1, 4 1, 4, 4, 2 2.5, 1 2.5))')

    request = MockRequest()
    processor = request.pyramid_oereb_processor
    view_service = ViewServiceRecord('test', 'test')
    real_estate = RealEstateRecord('Test', 'BL', 'Duggingen',
                                   1234, 1000, MultiPolygon([rectangle]), view_service)
    extract_dict = processor.process(real_estate)
    assert isinstance(extract_dict, dict)


def test_line_intersection():
    """ Tests the intersection between a rectangle and a polygon where the
    intersecting polygon produces two partial geometries inside the
    rectangle of wich one should be eliminated by the tolerance check
    """

    # shapely test geometries:
    rectangle = loads('POLYGON((0 0, 0 3, 3 3, 3 0, 0 0))')
    # line = loads('LINESTRING((1 1, 1 4, 4 4, 4 1, 2.5 1))')

    request = MockRequest()
    processor = request.pyramid_oereb_processor
    view_service = ViewServiceRecord('test', 'test')
    real_estate = RealEstateRecord('Test', 'BL', 'Duggingen',
                                   1234, 1000, MultiPolygon([rectangle]), view_service)
    extract_dict = processor.process(real_estate)
    assert isinstance(extract_dict, dict)