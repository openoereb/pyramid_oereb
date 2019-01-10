# -*- coding: utf-8 -*-
import json
import logging
import pytest
from jsonschema import Draft4Validator
from pyramid.httpexceptions import HTTPBadRequest, HTTPNoContent

from tests import pyramid_oereb_test_config, schema_json_extract
from tests.mockrequest import MockRequest
from pyramid_oereb.views.webservice import PlrWebservice

log = logging.getLogger('pyramid_oereb')


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
    for k, v in expected.items():
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
    for k, v in expected.items():
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
    response = service.get_extract_by_id()
    assert isinstance(response, HTTPNoContent)


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

    with open(schema_json_extract) as f:
        schema = json.loads(f.read())
    Draft4Validator.check_schema(schema)
    validator = Draft4Validator(schema)
    response = json.loads(response.body.decode('utf-8'))
    validator.validate(response)

    assert isinstance(response, dict)

    extract = response.get('GetExtractByIdResponse').get('extract')
    real_estate = extract.get('RealEstate')

    assert isinstance(real_estate, dict)
    if topics == 'ALL':
        assert len(real_estate.get('RestrictionOnLandownership')) == 3
        assert len(extract.get('ConcernedTheme')) == 3
        assert len(extract.get('NotConcernedTheme')) == 14
        assert len(extract.get('ThemeWithoutData')) == 0
        restrictions = real_estate.get('RestrictionOnLandownership')
        assert restrictions[0]['Theme']['Code'] == 'LandUsePlans'
        assert restrictions[1]['Theme']['Code'] == 'MotorwaysBuildingLines'
        assert restrictions[2]['Theme']['Code'] == 'ContaminatedSites'
    if topics == 'ALL_FEDERAL':
        assert len(real_estate.get('RestrictionOnLandownership')) == 1
        assert len(extract.get('ConcernedTheme')) == 1
        assert len(extract.get('NotConcernedTheme')) == 9
        assert len(extract.get('ThemeWithoutData')) == 0
        restrictions = real_estate.get('RestrictionOnLandownership')
        assert restrictions[0]['Theme']['Code'] == 'MotorwaysBuildingLines'
    if topics == 'ContaminatedSites,RailwaysProjectPlanningZones':
        assert len(real_estate.get('RestrictionOnLandownership')) == 1
        assert len(extract.get('ConcernedTheme')) == 1
        assert len(extract.get('NotConcernedTheme')) == 1
        assert len(extract.get('ThemeWithoutData')) == 0
        restrictions = real_estate.get('RestrictionOnLandownership')
        assert restrictions[0]['Theme']['Code'] == 'ContaminatedSites'
