# -*- coding: utf-8 -*-
import json

import pytest
from jsonschema import Draft4Validator
from pyramid.httpexceptions import HTTPBadRequest, HTTPNoContent

from pyramid_oereb.tests.conftest import MockRequest, pyramid_oereb_test_config
from pyramid_oereb.views.webservice import PlrWebservice


@pytest.mark.parametrize('params', [
    {
        'flavour': 'INVALIDFLAVOUR',
        'format': 'xml',
        'param1': 'egrid'
    },
    {
        'flavour': 'reduced',
        'format': 'INVALIDFORMAT',
        'param1': 'egrid'
    },
    {
        'flavour': 'FULL',
        'format': 'XML',
        'param1': 'egrid'
    },
    {
        'flavour': 'SIGNED',
        'format': 'JSON',
        'param1': 'egrid'
    },
    {
        'flavour': 'EMBEDDABLE',
        'format': 'PDF',
        'param1': 'egrid'
    },
    {
        'flavour': 'full',
        'format': 'PDF',
        'param1': 'GEOMETRY',
        'param2': 'egrid'
    }
])
def test_invalid_flavour(params):
    request = MockRequest()
    request.matchdict.update(params)
    service = PlrWebservice(request)
    with pytest.raises(HTTPBadRequest):
        service.__validate_extract_params__()


@pytest.mark.parametrize('params,expected', [
    (
        {
            'flavour': 'SIGNED',
            'format': 'PDF',
            'param1': 'SomeEGRID'
        }, {
            'flavour': 'signed',
            'format': 'pdf',
            'geometry': False,
            'images': False,
            'egrid': 'SomeEGRID'
        }
    ),
    (
        {
            'flavour': 'FULL',
            'format': 'PDF',
            'param1': 'SomeIdent',
            'param2': 'SomeNumber'
        }, {
            'flavour': 'full',
            'format': 'pdf',
            'geometry': False,
            'images': False,
            'identdn': 'SomeIdent',
            'number': 'SomeNumber'
        }
    ),
    (
        {
            'flavour': 'REDUCED',
            'format': 'XML',
            'param1': 'GEOMETRY',
            'param2': 'SomeEGRID'
        }, {
            'flavour': 'reduced',
            'format': 'xml',
            'geometry': True,
            'images': False,
            'egrid': 'SomeEGRID'
        }
    ),
    (
        {
            'flavour': 'EMBEDDABLE',
            'format': 'JSON',
            'param1': 'GEOMETRY',
            'param2': 'SomeIdent',
            'param3': 'SomeNumber'
        }, {
            'flavour': 'embeddable',
            'format': 'json',
            'geometry': True,
            'images': False,
            'identdn': 'SomeIdent',
            'number': 'SomeNumber'
        }
    )
])
def test_matchdict(params, expected):
    request = MockRequest()
    request.matchdict.update(params)
    service = PlrWebservice(request)
    params = service.__validate_extract_params__()
    for k, v in expected.iteritems():
        assert getattr(params, k) == v


def test_params():
    request = MockRequest()
    request.matchdict.update({
        'flavour': 'REDUCED',
        'format': 'XML',
        'param1': 'SomeEGRID'
    })
    request.params.update({
        'WITHIMAGES': '',
        'LANG': 'de',
        'TOPICS': 'top_A,top_B,top_C'
    })
    service = PlrWebservice(request)
    params = service.__validate_extract_params__()
    expected = {
        'flavour': 'reduced',
        'format': 'xml',
        'geometry': False,
        'images': True,
        'egrid': 'SomeEGRID',
        'language': 'de',
        'topics': ['top_A', 'top_B', 'top_C']
    }
    for k, v in expected.iteritems():
        assert getattr(params, k) == v


def test_return_no_content():
    request = MockRequest()
    request.matchdict.update({
        'flavour': 'REDUCED',
        'format': 'XML',
        'param1': 'GEOMETRY',
        'param2': 'MISSINGEGRID'
    })
    service = PlrWebservice(request)
    with pytest.raises(HTTPNoContent):
        service.get_extract_by_id()


@pytest.mark.last
@pytest.mark.parametrize('topics', [
    'ALL',
    'ALL_FEDERAL',
    'ContaminatedSites,RailwaysProjectPlanningZones'
])
def test_return_json(topics):
    with pyramid_oereb_test_config() as pyramid_config:
        pyramid_config.add_renderer('pyramid_oereb_extract_json',
                                    'pyramid_oereb.lib.renderer.extract.json_.Renderer')
        request = MockRequest()
        request.matchdict.update({
            'flavour': 'REDUCED',
            'format': 'JSON',
            'param1': 'GEOMETRY',
            'param2': 'TEST'
        })
        request.params.update({
            'TOPICS': topics
        })
        service = PlrWebservice(request)
        response = service.get_extract_by_id()

    with open('./pyramid_oereb/tests/resources/schema_webservices.json') as f:
        schema = json.loads(f.read())
    Draft4Validator.check_schema(schema)
    validator = Draft4Validator(schema)
    extract = json.loads(response.body)
    validator.validate(extract)

    assert isinstance(extract, dict)

    real_estate = extract.get('GetExtractByIdResponse').get('extract').get('RealEstate')
    assert isinstance(real_estate, dict)
    if topics == 'ALL' or topics == 'ALL_FEDERAL':
        assert len(real_estate.get('RestrictionOnLandownership')) == 5
    if topics == 'ContaminatedSites,RailwaysProjectPlanningZones':
        assert len(real_estate.get('RestrictionOnLandownership')) == 1
