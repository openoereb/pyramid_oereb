# -*- coding: utf-8 -*-
import pytest

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.testing import DummyRequest, testConfig

from pyramid_oereb.views.webservice import PlrWebservice


def get_test_config():
    return {}


def test_getegrid_coord_missing_parameter():
    with testConfig(settings=get_test_config()):
        webservice = PlrWebservice(DummyRequest())
        with pytest.raises(HTTPBadRequest):
            webservice.get_egrid_coord()


def test_getegrid_xy():
    with testConfig(settings=get_test_config()):
        webservice = PlrWebservice(DummyRequest(params={
            'XY': '2622610,1259110'
        }))
        properties = webservice.get_egrid_coord()
        # TODO: Activate validation when schema issues are fixed
        # with open('./pyramid_oereb/tests/resources/schema_webservices.json') as f:
        #     schema = json.load(f)
        # validate(properties, schema)
        assert isinstance(properties, list)


def test_getegrid_gnss():
    with testConfig(settings=get_test_config()):
        webservice = PlrWebservice(DummyRequest(params={
            'GNSS': '47.48237,7.73860'
        }))
        properties = webservice.get_egrid_coord()
        # TODO: Activate validation when schema issues are fixed
        # with open('./pyramid_oereb/tests/resources/schema_webservices.json') as f:
        #     schema = json.load(f)
        # validate(properties, schema)
        assert isinstance(properties, list)


def test_getegrid_ident():
    with testConfig(settings=get_test_config()):
        request = DummyRequest()
        request.matchdict.update({
            'identdn': 'test1',
            'number': 'test2'
        })
        webservice = PlrWebservice(request)
        properties = webservice.get_egrid_ident()
        # TODO: Activate validation when schema issues are fixed
        # with open('./pyramid_oereb/tests/resources/schema_webservices.json') as f:
        #     schema = json.load(f)
        # validate(properties, schema)
        assert isinstance(properties, list)


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
        properties = webservice.get_egrid_address()
        # TODO: Activate validation when schema issues are fixed
        # with open('./pyramid_oereb/tests/resources/schema_webservices.json') as f:
        #     schema = json.load(f)
        # validate(properties, schema)
        assert isinstance(properties, list)


def test_getegrid_address_missing_parameter():
    with testConfig(settings=get_test_config()):
        webservice = PlrWebservice(DummyRequest())
        with pytest.raises(HTTPBadRequest):
            webservice.get_egrid_address()
