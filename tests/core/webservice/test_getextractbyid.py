# -*- coding: utf-8 -*-
import json
import logging
import pytest
from unittest.mock import patch
from jsonschema import Draft4Validator
from pyramid.httpexceptions import HTTPBadRequest, HTTPSeeOther, HTTPNoContent

from tests.mockrequest import MockRequest
from pyramid_oereb.core.views.webservice import PlrWebservice

import pyramid_oereb.core.renderer.extract.json_
import pyramid_oereb.core.views.webservice
import pyramid_oereb.core.hook_methods

log = logging.getLogger('pyramid_oereb')


@pytest.mark.parametrize('matchdict,params', [
    (
        {
            'format': 'INVALIDFORMAT'
        }, {
            'EGRID': 'egrid'
        }
    ), (
        {
            'format': 'pdf'
        },
        {
            'EGRID': 'egrid',
            'GEOMETRY': 'true'
        }
    )
])
def test_invalid_params(matchdict, params):
    request = MockRequest()
    request.matchdict.update(matchdict)
    request.params.update(params)
    service = PlrWebservice(request)
    with pytest.raises(HTTPBadRequest):
        service.__validate_extract_params__()


@pytest.mark.parametrize('matchdict,expected', [
    (
        {
            'format': 'PDF',
        }, {
            'format': 'pdf',
            'with_geometry': False,
            'images': False,
            'signed': False,
            'egrid': 'egrid'
        }
    ),
    (
        {
            'format': 'XML',
        }, {
            'format': 'xml',
            'with_geometry': False,
            'images': False,
            'signed': False,
            'egrid': 'egrid'
        }
    ), (
        {
            'format': 'JSON',
        }, {
            'format': 'json',
            'with_geometry': False,
            'images': False,
            'signed': False,
            'egrid': 'egrid'
        }
    )
])
@patch.object(MockRequest, 'route_url', lambda *args, **kwargs: '')
def test_matchdict(pyramid_oereb_test_config, matchdict, expected):
    request = MockRequest()
    request.matchdict.update(matchdict)
    request.params.update({
        'EGRID': 'egrid'
    })
    service = PlrWebservice(request)
    params = service.__validate_extract_params__()
    for k, v in expected.items():
        assert getattr(params, k) == v


@pytest.mark.parametrize('params,expected', [
    (
        {
            'EGRID': 'egrid'
        }, {
            'egrid': 'egrid',
            'with_geometry': False,
            'images': False,
            'signed': False
        }
    ), (
        {
            'IDENTDN': 'identdn',
            'NUMBER': 'number',
            'WITHIMAGES': 'true',
            'GEOMETRY': 'true',
            'SIGNED': 'true',
            'LANG': 'de',
            'TOPICS': 'top_A,top_B,top_C'
        }, {
            'identdn': 'identdn',
            'number': 'number',
            'with_geometry': True,
            'images': True,
            'signed': True,
            'language': 'de',
            'topics': ['top_A', 'top_B', 'top_C']
        }
    )
])
@patch.object(MockRequest, 'route_url', lambda *args, **kwargs: '')
def test_params(params, expected):
    request = MockRequest()
    request.matchdict.update({
        'format': 'XML'
    })
    request.params.update(params)
    service = PlrWebservice(request)
    params = service.__validate_extract_params__()
    for k, v in expected.items():
        assert getattr(params, k) == v


@patch.object(MockRequest, 'route_url', lambda *args, **kwargs: '')
def test_return_no_content():
    request = MockRequest()
    request.matchdict.update({
        'format': 'XML'
    })
    request.params.update({
        'GEOMETRY': 'true',
        'EGRID': 'MISSINGEGRID'
    })
    service = PlrWebservice(request)
    response = service.get_extract_by_id()
    assert isinstance(response, HTTPNoContent)


@patch.object(pyramid_oereb.core.hook_methods, 'route_prefix', 'oereb')
@patch.object(pyramid_oereb.core.views.webservice, 'route_prefix', 'oereb')
@patch.object(MockRequest, 'route_url', lambda *args, **kwargs: '')
@pytest.mark.parametrize('egrid,topics', [
    ('TEST', 'ALL'),
    ('TEST', 'ALL_FEDERAL'),
    ('TEST', 'ch.BelasteteStandorte,ch.ProjektierungszonenEisenbahnanlagen'),
    ('TEST3', 'ALL')
])
def test_return_json(pyramid_oereb_test_config, pyramid_test_config, schema_json_extract,
                     egrid, topics, extract_real_estate_data,
                     main_schema, land_use_plans, contaminated_sites):
    pyramid_test_config.add_renderer('pyramid_oereb_extract_json',
                                     'pyramid_oereb.core.renderer.extract.json_.Renderer')
    request = MockRequest()
    request.matchdict.update({
        'format': 'JSON'
    })
    request.params.update({
        'GEOMETRY': 'true',
        'EGRID': egrid,
        'TOPICS': topics
    })
    service = PlrWebservice(request)
    response = service.get_extract_by_id()

    if topics == 'ALL' and egrid == 'TEST3':
        assert isinstance(response, HTTPNoContent)
        return
    Draft4Validator.check_schema(schema_json_extract)
    validator = Draft4Validator(schema_json_extract)
    response = json.loads(response.body.decode('utf-8'))
    validator.validate(response)

    assert isinstance(response, dict)

    extract = response.get('GetExtractByIdResponse').get('extract')
    real_estate = extract.get('RealEstate')

    assert isinstance(real_estate, dict)
    if topics == 'ALL' and egrid == 'TEST':
        assert len(real_estate.get('RestrictionOnLandownership')) == 2
        assert len(extract.get('ConcernedTheme')) == 2
        assert len(extract.get('NotConcernedTheme')) == 0
        assert len(extract.get('ThemeWithoutData')) == 0
        restrictions = real_estate.get('RestrictionOnLandownership')
        assert restrictions[0]['Theme']['Code'] == 'ch.Nutzungsplanung'
        assert restrictions[1]['Theme']['Code'] == 'ch.BelasteteStandorte'
        # simplified dataset, containing only two restrictions insetead of previously 14

    if topics == 'ALL_FEDERAL':
        assert len(real_estate.get('RestrictionOnLandownership')) == 2
        assert len(extract.get('ConcernedTheme')) == 2
        assert len(extract.get('NotConcernedTheme')) == 0
        assert len(extract.get('ThemeWithoutData')) == 0
        restrictions = real_estate.get('RestrictionOnLandownership')
        assert restrictions[0]['Theme']['Code'] == 'ch.Nutzungsplanung'
        assert restrictions[1]['Theme']['Code'] == 'ch.BelasteteStandorte'

    if topics == 'ch.BelasteteStandorte,ch.ProjektierungszonenEisenbahnanlagen':
        assert len(real_estate.get('RestrictionOnLandownership')) == 1
        assert len(extract.get('ConcernedTheme')) == 1
        assert len(extract.get('NotConcernedTheme')) == 0
        assert len(extract.get('ThemeWithoutData')) == 0
        restrictions = real_estate.get('RestrictionOnLandownership')
        assert restrictions[0]['Theme']['Code'] == 'ch.BelasteteStandorte'

    if topics == 'ALL' and egrid == 'TEST3':
        assert len(extract.get('ConcernedTheme')) == 3
        assert len(extract.get('NotConcernedTheme')) == 14
        assert len(extract.get('ThemeWithoutData')) == 0
        restrictions = real_estate.get('RestrictionOnLandownership')
        assert len(restrictions) == 4
        assert restrictions[1]['Theme']['Code'] == 'ch.BaulinienNationalstrassen'
        assert restrictions[1]['Lawstatus']['Code'] == 'changeWithoutPreEffect'
        assert restrictions[2]['Theme']['Code'] == 'ch.BaulinienNationalstrassen'
        assert restrictions[2]['Lawstatus']['Code'] == 'inForce'


@patch.object(MockRequest, 'route_url', lambda *args, **kwargs: '')
def test_format_url(real_estate_data):
    request = MockRequest()
    request.matchdict.update({
        'format': 'URL'
    })
    request.params.update({
        'EGRID': 'TEST'
    })
    service = PlrWebservice(request)
    response = service.get_extract_by_id()
    assert isinstance(response, HTTPSeeOther)
    assert response.location == 'https://geoview.bl.ch/oereb/?egrid=TEST'
