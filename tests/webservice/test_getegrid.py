# -*- coding: utf-8 -*-
import json
import math

from jsonschema import Draft4Validator
from shapely.geometry import Point, Polygon, MultiPolygon

import pytest

from pyramid.httpexceptions import HTTPBadRequest, HTTPNoContent

from pyramid_oereb.lib.records.real_estate import RealEstateRecord
from pyramid_oereb.lib.records.view_service import ViewServiceRecord
from tests import schema_json_extract, pyramid_oereb_test_config
from tests.mockrequest import MockRequest
from pyramid_oereb.views.webservice import PlrWebservice, Parameter


def test_getegrid_coord_missing_parameter():
    request = MockRequest(current_route_url='http://example.com/oereb/getegrid/json/')

    # Add params to matchdict as the view will do it for /getegrid/{format}/
    request.matchdict.update({
        'format': u'json'
    })
    webservice = PlrWebservice(request)
    response = webservice.get_egrid()
    assert response.code == 400


@pytest.mark.parametrize('geometry', [False, True])
def test_getegrid_ident(geometry):
    with pyramid_oereb_test_config():
        request = MockRequest(current_route_url='http://example.com/oereb/getegrid/json/BLTEST/1000')

        # Add params to matchdict as the view will do it for /getegrid/{format}/{identdn}/{number}
        request.matchdict.update({
            'format': u'json'
        })
        request.params.update({
            'IDENTDN': u'BLTEST',
            'NUMBER': u'1000'
        })
        if geometry:
            request.params.update({
                'GEOMETRY': u'true'
            })

        webservice = PlrWebservice(request)
        response = webservice.get_egrid().json
        with open(schema_json_extract) as f:
            schema = json.loads(f.read())
        Draft4Validator.check_schema(schema)
        validator = Draft4Validator(schema)
        validator.validate(response)
        assert isinstance(response, dict)
        real_estates = response.get('GetEGRIDResponse')
        assert isinstance(real_estates, list)
        assert len(real_estates) == 1
        assert real_estates[0]['egrid'] == u'TEST'
        assert real_estates[0]['number'] == u'1000'
        assert real_estates[0]['identDN'] == u'BLTEST'
        assert real_estates[0]['type'] == u'Liegenschaft'
        if geometry:
            assert 'limit' in real_estates[0]
            assert 'crs' in real_estates[0]['limit']
            assert 'coordinates' in real_estates[0]['limit']


def test_getegrid_en():
    with pyramid_oereb_test_config():
        url = 'http://example.com/oereb/getegrid/json/?EN=2,0'
        request = MockRequest(
            current_route_url=url
        )

        # Add params to matchdict as the view will do it for /getegrid/{format}/
        request.matchdict.update({
          'format': u'json'
        })
        request.params.update({
            'EN': '2,0'
        })
        webservice = PlrWebservice(request)
        response = webservice.get_egrid().json
        with open(schema_json_extract) as f:
            schema = json.loads(f.read())
        Draft4Validator.check_schema(schema)
        validator = Draft4Validator(schema)
        validator.validate(response)
        assert isinstance(response, dict)
        real_estates = response.get('GetEGRIDResponse')
        assert isinstance(real_estates, list)
        assert len(real_estates) == 2
        assert real_estates[0]['egrid'] == u'TEST'
        assert real_estates[0]['number'] == u'1000'
        assert real_estates[0]['identDN'] == u'BLTEST'


def test_getegrid_gnss():
    with pyramid_oereb_test_config():
        request = MockRequest(
            current_route_url='http://example.com/oereb/getegrid/json/?GNSS=32.1244978460310,-19.917989937473'
        )

        # Add params to matchdict as the view will do it for /getegrid/{format}/
        request.matchdict.update({
          'format': u'json'
        })
        request.params.update({
            'GNSS': '32.1244978460310,-19.917989937473'
        })
        webservice = PlrWebservice(request)
        response = webservice.get_egrid().json
        with open(schema_json_extract) as f:
            schema = json.loads(f.read())
        Draft4Validator.check_schema(schema)
        validator = Draft4Validator(schema)
        validator.validate(response)
        assert isinstance(response, dict)
        real_estates = response.get('GetEGRIDResponse')
        assert isinstance(real_estates, list)
        assert len(real_estates) == 1
        assert real_estates[0]['egrid'] == u'TEST'
        assert real_estates[0]['number'] == u'1000'
        assert real_estates[0]['identDN'] == u'BLTEST'


def test_getegrid_address():
    with pyramid_oereb_test_config():
        request = MockRequest(
            current_route_url='http://example.com/oereb/getegrid/json/4410/test/10'
        )

        # Add params to matchdict as the view will do it for
        # /getegrid/{format}/{postalcode}/{localisation}/{number}
        request.matchdict.update({
            'format': u'json'
        })
        request.params.update({
            'POSTALCODE': u'4410',
            'LOCALISATION': u'test',
            'NUMBER': u'10'
        })
        webservice = PlrWebservice(request)
        response = webservice.get_egrid().json
        with open(schema_json_extract) as f:
            schema = json.loads(f.read())
        Draft4Validator.check_schema(schema)
        validator = Draft4Validator(schema)
        validator.validate(response)
        assert isinstance(response, dict)
        assert response.get('GetEGRIDResponse') is not None
        assert response.get('GetEGRIDResponse')[0].get('egrid') == u'TEST'
        assert response.get('GetEGRIDResponse')[0].get('number') == u'1000'
        assert response.get('GetEGRIDResponse')[0].get('identDN') == u'BLTEST'


def test_get_egrid_response():
    with pyramid_oereb_test_config():
        request = MockRequest(current_route_url='http://example.com/oereb/getegrid/json/')
        # Add params to matchdict as the view will do it for /getegrid/{format}/
        request.matchdict.update({
          'format': u'json'
        })

        view_service = ViewServiceRecord({'de': 'test'},
                                         1,
                                         1.0,
                                         None)
        record = RealEstateRecord('Liegenschaft', 'BL', 'test', 1, 100,
                                  MultiPolygon([Polygon([(0, 0), (1, 1), (1, 0)])]), view_service,
                                  number='number', identdn='identdn', egrid='egrid')
        params = Parameter('json')
        response = PlrWebservice(request).__get_egrid_response__([record], params).json
        assert response == {
            'GetEGRIDResponse': [{
                'egrid': 'egrid',
                'number': 'number',
                'identDN': 'identdn',
                'type': 'Liegenschaft'
            }]
        }


def test_get_egrid_response_no_content():
    with pyramid_oereb_test_config():
        request = MockRequest(current_route_url='http://example.com/oereb/getegrid/json/')

        # Add params to matchdict as the view will do it for /getegrid/{format}/
        request.matchdict.update({
          'format': u'json'
        })

        params = Parameter('json')
        response = PlrWebservice(request).__get_egrid_response__([], params)
        assert isinstance(response, HTTPNoContent)


@pytest.mark.parametrize('src,dst,buffer_dist', [
    ('2621857.856,1259856.578', (2621857.856, 1259856.578), None)
])
def test_parse_xy(src, dst, buffer_dist):
    geom = PlrWebservice(MockRequest()).__parse_en__(src, buffer_dist=buffer_dist)
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
    geom = PlrWebservice(MockRequest()).__parse_gnss__('47.48911,7.72866')
    assert isinstance(geom, Polygon)
    assert round(geom.centroid.x, 3) == 2621858.036
    assert round(geom.centroid.y, 3) == 1259856.747
    assert round(geom.area, 2) == round(math.pi, 2)


def test_parse_invalid_coordinates():
    with pytest.raises(HTTPBadRequest):
        PlrWebservice(MockRequest()).__parse_gnss__('7.72866')
    with pytest.raises(HTTPBadRequest):
        PlrWebservice(MockRequest()).__parse_en__('2621857.856;1259856.578')
