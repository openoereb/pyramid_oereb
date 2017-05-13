# -*- coding: utf-8 -*-
import math
from shapely.geometry import Point, Polygon, MultiPolygon

import pyramid_oereb
import pytest

from pyramid.httpexceptions import HTTPBadRequest
from pyramid_oereb.lib.records.real_estate import RealEstateRecord
from pyramid_oereb.lib.records.view_service import ViewServiceRecord
from pyramid_oereb.tests.conftest import config_reader, MockRequest
from pyramid_oereb.views.webservice import PlrWebservice


def test_getegrid_coord_missing_parameter():
    webservice = PlrWebservice(MockRequest())
    with pytest.raises(HTTPBadRequest):
        webservice.get_egrid_coord()


def test_getegrid_ident(connection):
    assert connection.closed
    pyramid_oereb.config_reader = config_reader
    request = MockRequest()
    request.matchdict.update({
        'identdn': u'BLTEST',
        'number': u'1000'
    })
    webservice = PlrWebservice(request)
    real_estates = webservice.get_egrid_ident()
    # TODO: Activate validation when schema issues are fixed
    # with open('./pyramid_oereb/tests/resources/schema_webservices.json') as f:
    #     schema = json.load(f)
    # validate(properties, schema)
    assert isinstance(real_estates, list)
    assert len(real_estates) == 1
    assert real_estates[0]['egrid'] == u'TEST'
    assert real_estates[0]['number'] == u'1000'
    assert real_estates[0]['identDN'] == u'BLTEST'


def test_getegrid_xy(connection):
    assert connection.closed
    pyramid_oereb.config_reader = config_reader
    request = MockRequest()
    request.params.update({
        'XY': '-1999999.0327394493,-999998.9404575331'
    })
    webservice = PlrWebservice(request)
    real_estates = webservice.get_egrid_coord()
    # TODO: Activate validation when schema issues are fixed
    # with open('./pyramid_oereb/tests/resources/schema_webservices.json') as f:
    #     schema = json.load(f)
    # validate(properties, schema)
    assert isinstance(real_estates, list)
    assert len(real_estates) == 1
    assert real_estates[0]['egrid'] == u'TEST'
    assert real_estates[0]['number'] == u'1000'
    assert real_estates[0]['identDN'] == u'BLTEST'


def test_getegrid_gnss():
    pyramid_oereb.config_reader = config_reader
    request = MockRequest()
    request.params.update({
        'GNSS': '-19.91798993747352,32.124497846031005'
    })
    webservice = PlrWebservice(request)
    real_estates = webservice.get_egrid_coord()
    # TODO: Activate validation when schema issues are fixed
    # with open('./pyramid_oereb/tests/resources/schema_webservices.json') as f:
    #     schema = json.load(f)
    # validate(properties, schema)
    assert isinstance(real_estates, list)
    assert len(real_estates) == 1
    assert real_estates[0]['egrid'] == u'TEST'
    assert real_estates[0]['number'] == u'1000'
    assert real_estates[0]['identDN'] == u'BLTEST'


def test_getegrid_ident_missing_parameter():
    webservice = PlrWebservice(MockRequest())
    with pytest.raises(HTTPBadRequest):
        webservice.get_egrid_ident()


def test_getegrid_address():
    request = MockRequest()
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
    webservice = PlrWebservice(MockRequest())
    with pytest.raises(HTTPBadRequest):
        webservice.get_egrid_address()


def test_get_egrid_response():
    view_service = ViewServiceRecord('test', 'test')
    record = RealEstateRecord('test', 'BL', 'test', 1, 100, MultiPolygon([Polygon([(0, 0), (1, 1), (1, 0)])]),
                              view_service, number='number', identdn='identdn', egrid='egrid')
    response = PlrWebservice(MockRequest()).__get_egrid_response__([record])
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
    geom = PlrWebservice(MockRequest()).__parse_xy__(src, buffer_dist=buffer_dist)
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
    geom = PlrWebservice(MockRequest()).__parse_gnss__('7.72866,47.48911')
    assert isinstance(geom, Polygon)
    assert round(geom.centroid.x, 3) == 2621858.036
    assert round(geom.centroid.y, 3) == 1259856.747
    assert round(geom.area, 2) == round(math.pi, 2)
