# -*- coding: utf-8 -*-
import pyramid_oereb
import pytest

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.testing import DummyRequest, testConfig
from pyramid_oereb.lib.records.real_estate import RealEstateRecord
from pyramid_oereb.lib.readers.real_estate import RealEstateReader
from pyramid_oereb.models import PyramidOerebMainRealEstate
from pyramid_oereb.tests.conftest import adapter, config_reader, db_url
from pyramid_oereb.views.webservice import PlrWebservice, __get_egrid_response__


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
        real_estates = webservice.get_egrid_coord()
        # TODO: Activate validation when schema issues are fixed
        # with open('./pyramid_oereb/tests/resources/schema_webservices.json') as f:
        #     schema = json.load(f)
        # validate(properties, schema)
        assert isinstance(real_estates, list)


def test_getegrid_ident():
    session = adapter.get_session(db_url)
    session.add(PyramidOerebMainRealEstate(
        identdn='test_identdn',
        number='1234',
        egrid='TESTEGRID',
        type='SelbstRecht.Baurecht',
        canton='BL',
        municipality='Liestal',
        fosnr=2829,
        metadata_of_geographical_base_data='metadataurl',
        land_registry_area=500
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
    record = RealEstateRecord('test', 'BL', 'test', 1, 'test', 1, 'test', 'number', 'identdn', 'egrid')
    response = __get_egrid_response__([record])
    assert response == [{
        'egrid': 'egrid',
        'number': 'number',
        'identDN': 'identdn'
    }]
