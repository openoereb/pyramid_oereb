# -*- coding: utf-8 -*-
import datetime
import pytest
from shapely.geometry import Point

from pyramid_oereb.lib.processor import Processor
from pyramid_oereb.lib.records.extract import ExtractRecord
from pyramid_oereb.lib.records.geometry import GeometryRecord
from pyramid_oereb.lib.records.image import ImageRecord
from pyramid_oereb.lib.records.office import OfficeRecord
from pyramid_oereb.lib.records.plr import PlrRecord
from pyramid_oereb.lib.records.theme import ThemeRecord
from pyramid_oereb.lib.records.view_service import ViewServiceRecord, LegendEntryRecord
from pyramid_oereb import ExtractReader
from pyramid_oereb import MunicipalityReader
from pyramid_oereb import ExclusionOfLiabilityReader
from pyramid_oereb import GlossaryReader
from pyramid_oereb import RealEstateReader
from pyramid_oereb.views.webservice import PlrWebservice
from tests.conftest import MockRequest

request_matchdict = {
    'flavour': 'reduced',
    'format': 'json',
    'param1': 'TEST'
}


def test_missing_params():
    with pytest.raises(TypeError):
        Processor()


def test_properties():
    request = MockRequest()
    request.matchdict.update(request_matchdict)
    processor = request.pyramid_oereb_processor
    assert isinstance(processor.extract_reader, ExtractReader)
    assert isinstance(processor.municipality_reader, MunicipalityReader)
    assert isinstance(processor.exclusion_of_liability_reader, ExclusionOfLiabilityReader)
    assert isinstance(processor.glossary_reader, GlossaryReader)
    assert isinstance(processor.plr_sources, list)
    assert isinstance(processor.real_estate_reader, RealEstateReader)


def test_process():
    request = MockRequest()
    request.matchdict.update(request_matchdict)
    processor = request.pyramid_oereb_processor
    real_estate = processor.real_estate_reader.read(egrid=u'TEST')
    webservice = PlrWebservice(request)
    params = webservice.__validate_extract_params__()
    extract = processor.process(real_estate[0], params, 'http://test.ch')
    assert isinstance(extract, ExtractRecord)


def test_process_geometry_testing():
    request = MockRequest()
    request.matchdict.update(request_matchdict)
    processor = request.pyramid_oereb_processor
    real_estate = processor.real_estate_reader.read(egrid=u'TEST')
    webservice = PlrWebservice(request)
    params = webservice.__validate_extract_params__()
    extract = processor.process(real_estate[0], params, 'http://test.ch')
    for plr in extract.real_estate.public_law_restrictions:
        for g in plr.geometries:
            assert g._test_passed


def test_filter_published_documents():
    request = MockRequest()
    request.matchdict.update(request_matchdict)
    processor = request.pyramid_oereb_processor
    real_estate = processor.real_estate_reader.read(egrid=u'TEST')
    webservice = PlrWebservice(request)
    params = webservice.__validate_extract_params__()
    extract = processor.process(real_estate[0], params, 'http://test.ch')
    for plr in extract.real_estate.public_law_restrictions:
        if plr.theme.code == u'MotorwaysBuildingLines':
            assert len(plr.documents) == 1
            assert len(plr.documents[0].references) == 1


def test_processor_with_images():
    request = MockRequest()
    request.matchdict.update(request_matchdict)
    request.params.update({
        'WITHIMAGES': '',
        'LANG': 'de'
    })
    processor = request.pyramid_oereb_processor
    real_estate = processor.real_estate_reader.read(egrid=u'TEST')
    webservice = PlrWebservice(request)
    params = webservice.__validate_extract_params__()
    extract = processor.process(real_estate[0], params, 'http://test.ch')
    assert extract.real_estate.plan_for_land_register.image is not None
    for plr in extract.real_estate.public_law_restrictions:
        assert plr.view_service.image is not None


def test_processor_without_images():
    request = MockRequest()
    request.matchdict.update(request_matchdict)
    request.params.update({
        'LANG': 'de'
    })
    processor = request.pyramid_oereb_processor
    real_estate = processor.real_estate_reader.read(egrid=u'TEST')
    webservice = PlrWebservice(request)
    params = webservice.__validate_extract_params__()
    extract = processor.process(real_estate[0], params, 'http://test.ch')
    assert extract.real_estate.plan_for_land_register.image is None
    for plr in extract.real_estate.public_law_restrictions:
        assert plr.view_service.image is None


def test_processor_get_legend_entries(law_status):
    theme1 = ThemeRecord(u'TEST', {'de': 'Theme 1'})
    theme2 = ThemeRecord(u'TEST', {'de': 'Theme 2'})
    office = OfficeRecord({'de': 'Test Office'})
    geometries = [GeometryRecord(law_status, datetime.date.today(), Point(1, 1))]
    legend1 = LegendEntryRecord(
        ImageRecord('1'.encode('utf-8')),
        {'de': 'legend1'},
        'CodeA',
        'bla',
        theme1,
        view_service_id=1
    )
    legend2 = LegendEntryRecord(
        ImageRecord('1'.encode('utf-8')),
        {'de': 'legend2'},
        'CodeB',
        'bla',
        theme1,
        view_service_id=1
    )
    legend3 = LegendEntryRecord(
        ImageRecord('1'.encode('utf-8')),
        {'de': 'legend3'},
        'CodeC',
        'bla',
        theme2,
        view_service_id=1
    )
    legend4 = LegendEntryRecord(
        ImageRecord('1'.encode('utf-8')),
        {'de': 'legend4'},
        'CodeD',
        'bla',
        theme2,
        view_service_id=1
    )
    view_service1 = ViewServiceRecord(
        'http://www.test1.url.ch',
        1,
        1.0,
        legend_at_web='http://www.test1.url.ch',
        legends=[legend1, legend2]
    )
    view_service2 = ViewServiceRecord(
        'http://www.test2.url.ch',
        1,
        1.0,
        legend_at_web='http://www.test2.url.ch',
        legends=[legend3, legend4]
    )
    image = ImageRecord('1'.encode('utf-8'))
    plr1 = PlrRecord(
        theme1,
        {'de': 'CONTENT'},
        law_status,
        datetime.datetime.now(),
        office,
        image,
        view_service1,
        geometries,
        type_code='CodeA',
    )
    plr2 = PlrRecord(
        theme1,
        {'de': 'CONTENT'},
        law_status,
        datetime.datetime.now(),
        office,
        image,
        view_service1,
        geometries,
        type_code='CodeB'
    )
    plr3 = PlrRecord(
        theme1,
        {'de': 'CONTENT'},
        law_status,
        datetime.datetime.now(),
        office,
        image,
        view_service2,
        geometries,
        type_code='CodeB'
    )
    plr4 = PlrRecord(
        theme1,
        {'de': 'CONTENT'},
        law_status,
        datetime.datetime.now(),
        office,
        image,
        view_service2,
        geometries,
        type_code='CodeB'
    )

    inside_plrs = [plr1]
    outside_plrs = [plr2, plr3]
    after_process = Processor.get_legend_entries(inside_plrs, outside_plrs)
    assert len(inside_plrs) == len(after_process)
    inside_plrs = [plr3]
    outside_plrs = [plr4]
    after_process = Processor.get_legend_entries(inside_plrs, outside_plrs)
    assert len(after_process) == 1
