# -*- coding: utf-8 -*-
import math
from geoalchemy2 import WKTElement
from shapely.geometry import Point, Polygon

import pyramid_oereb
import pytest

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.testing import DummyRequest, testConfig
from pyramid_oereb.lib.records.real_estate import RealEstateRecord
from pyramid_oereb.lib.readers.real_estate import RealEstateReader
from pyramid_oereb.lib.records.view_service import ViewServiceRecord
from pyramid_oereb.models import PyramidOerebMainRealEstate
from pyramid_oereb.tests.conftest import config_reader, db_url
from pyramid_oereb.views.webservice import PlrWebservice, __get_egrid_response__, __parse_xy__, __parse_gnss__


def get_test_config():
    return {}


def set_up_real_estate_reader():
    real_estate_config = config_reader.get_real_estate_config()
    pyramid_oereb.real_estate_reader = RealEstateReader(
        real_estate_config.get('source').get('class'),
        **real_estate_config.get('source').get('params')
    )


def test_getegrid_coord_missing_parameter():
    with testConfig(settings=get_test_config()):
        webservice = PlrWebservice(DummyRequest())
        with pytest.raises(HTTPBadRequest):
            webservice.get_egrid_coord()


@pytest.mark.run(order=1)
def test_getegrid_ident():
    session = pyramid_oereb.database_adapter.get_session(db_url)
    session.add(PyramidOerebMainRealEstate(
        identdn='test_identdn',
        number='1234',
        egrid='TESTEGRID',
        type='SelbstRecht.Baurecht',
        canton='BL',
        municipality='Liestal',
        fosnr=2829,
        metadata_of_geographical_base_data='metadataurl',
        land_registry_area=500,
        limit=WKTElement('MULTIPOLYGON(((2621826.461 1259877.780, 2621889.613 1259880.298, 2621890.969 '
                         '1259825.282, 2621828.011 1259826.831, 2621826.461 1259877.780)))', srid=2056)
    ))
    session.commit()
    with testConfig(settings=get_test_config()):
        set_up_real_estate_reader()
        request = DummyRequest()
        request.matchdict.update({
            'identdn': 'test_identdn',
            'number': '1234'
        })
        webservice = PlrWebservice(request)
        real_estates = webservice.get_egrid_ident()
        # TODO: Activate validation when schema issues are fixed
        # with open('./pyramid_oereb/tests/resources/schema_webservices.json') as f:
        #     schema = json.load(f)
        # validate(properties, schema)
        assert isinstance(real_estates, list)
        assert len(real_estates) == 1
        assert real_estates[0]['egrid'] == 'TESTEGRID'
        assert real_estates[0]['number'] == '1234'
        assert real_estates[0]['identDN'] == 'test_identdn'


@pytest.mark.run(order=2)
def test_getegrid_xy():
    with testConfig(settings=get_test_config()):
        set_up_real_estate_reader()
        pyramid_oereb.config_reader = config_reader
        webservice = PlrWebservice(DummyRequest(params={
            'XY': '2621857.856,1259856.578'
        }))
        real_estates = webservice.get_egrid_coord()
        # TODO: Activate validation when schema issues are fixed
        # with open('./pyramid_oereb/tests/resources/schema_webservices.json') as f:
        #     schema = json.load(f)
        # validate(properties, schema)
        assert isinstance(real_estates, list)
        assert len(real_estates) == 1
        assert real_estates[0]['egrid'] == 'TESTEGRID'
        assert real_estates[0]['number'] == '1234'
        assert real_estates[0]['identDN'] == 'test_identdn'


@pytest.mark.run(order=2)
def test_getegrid_gnss():
    with testConfig(settings=get_test_config()):
        set_up_real_estate_reader()
        pyramid_oereb.config_reader = config_reader
        webservice = PlrWebservice(DummyRequest(params={
            'GNSS': '7.72866,47.48911'
        }))
        real_estates = webservice.get_egrid_coord()
        # TODO: Activate validation when schema issues are fixed
        # with open('./pyramid_oereb/tests/resources/schema_webservices.json') as f:
        #     schema = json.load(f)
        # validate(properties, schema)
        assert isinstance(real_estates, list)
        assert len(real_estates) == 1
        assert real_estates[0]['egrid'] == 'TESTEGRID'
        assert real_estates[0]['number'] == '1234'
        assert real_estates[0]['identDN'] == 'test_identdn'


def test_getegrid_ident_missing_parameter():
    with testConfig(settings=get_test_config()):
        webservice = PlrWebservice(DummyRequest())
        with pytest.raises(HTTPBadRequest):
            webservice.get_egrid_ident()


def test_getegrid_address():
    with testConfig(settings=get_test_config()):
        request = DummyRequest()
        request.matchdict.update({
            'postalcode': '4321',
            'localisation': 'test',
            'number': '123'
        })
        webservice = PlrWebservice(request)
        real_estates = webservice.get_egrid_address()
        # TODO: Activate validation when schema issues are fixed
        # with open('./pyramid_oereb/tests/resources/schema_webservices.json') as f:
        #     schema = json.load(f)
        # validate(properties, schema)
        assert isinstance(real_estates, list)


def test_getegrid_address_missing_parameter():
    with testConfig(settings=get_test_config()):
        webservice = PlrWebservice(DummyRequest())
        with pytest.raises(HTTPBadRequest):
            webservice.get_egrid_address()


def test_get_egrid_response():
    view_service = ViewServiceRecord('test', 'test')
    record = RealEstateRecord('test', 'BL', 'test', 1, 100, 'WKT', view_service, number='number',
                              identdn='identdn', egrid='egrid')
    response = __get_egrid_response__([record])
    assert response == [{
        'egrid': 'egrid',
        'number': 'number',
        'identDN': 'identdn'
    }]


@pytest.mark.parametrize('src,dst,buffer_dist', [
    ('2621857.856,1259856.578', (2621857.856, 1259856.578), None),
    ('621857.759,259856.554', (2621857.799, 1259856.500), 1.0)
])
def test_parse_xy(src, dst, buffer_dist):
    pyramid_oereb.config_reader = config_reader
    geom = __parse_xy__(src, buffer_dist=buffer_dist)
    if buffer_dist:
        assert isinstance(geom, Polygon)
        assert round(geom.area, 2) == round(math.pi, 2)
        assert round(geom.centroid.x, 3) == round(dst[0], 3)
        assert round(geom.centroid.y, 3) == round(dst[1], 3)
    else:
        assert isinstance(geom, Point)
        assert round(geom.x, 3) == round(dst[0], 3)
        assert round(geom.y, 3) == round(dst[1], 3)


def test_parse_gnss():
    pyramid_oereb.config_reader = config_reader
    geom = __parse_gnss__('7.72866,47.48911')
    assert isinstance(geom, Polygon)
    assert round(geom.centroid.x, 3) == 2621858.036
    assert round(geom.centroid.y, 3) == 1259856.747
    assert round(geom.area, 2) == round(math.pi, 2)
