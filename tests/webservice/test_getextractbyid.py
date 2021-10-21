# -*- coding: utf-8 -*-
import json
import logging
import pytest
from jsonschema import Draft4Validator
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPNoContent

from tests import pyramid_oereb_test_config, schema_json_extract
from tests.mockrequest import MockRequest
from pyramid_oereb.views.webservice import PlrWebservice

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
def test_matchdict(matchdict, expected):
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


@pytest.mark.parametrize('egrid,topics', [
    ('TEST', 'ALL'),
    ('TEST', 'ALL_FEDERAL'),
    ('TEST', 'ch.BelasteteStandorte,ch.ProjektierungszonenEisenbahnanlagen'),
    ('TEST3', 'ALL')
])
def test_return_json(egrid, topics):
    with pyramid_oereb_test_config() as pyramid_config:
        pyramid_config.add_renderer('pyramid_oereb_extract_json',
                                    'pyramid_oereb.lib.renderer.extract.json_.Renderer')
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
    if topics == 'ALL' and egrid == 'TEST':
        assert len(real_estate.get('RestrictionOnLandownership')) == 3
        assert len(extract.get('ConcernedTheme')) == 3
        assert len(extract.get('NotConcernedTheme')) == 14
        assert len(extract.get('ThemeWithoutData')) == 0
        restrictions = real_estate.get('RestrictionOnLandownership')
        assert restrictions[0]['Theme']['Code'] == 'ch.Nutzungsplanung'
        assert restrictions[1]['Theme']['Code'] == 'ch.BaulinienNationalstrassen'
        assert restrictions[2]['Theme']['Code'] == 'ch.BelasteteStandorte'
        # Check consistency of ordering (according to config) for not concerned themes
        assert extract.get('NotConcernedTheme')[0]['Code'] == 'ch.ProjektierungszonenNationalstrassen'
        assert extract.get('NotConcernedTheme')[1]['Code'] == 'ch.ProjektierungszonenEisenbahnanlagen'
        assert extract.get('NotConcernedTheme')[2]['Code'] == 'ch.BaulinienEisenbahnanlagen'
        assert extract.get('NotConcernedTheme')[3]['Code'] == 'ch.ProjektierungszonenFlughafenanlagen'
        assert extract.get('NotConcernedTheme')[4]['Code'] == 'ch.BaulinienFlughafenanlagen'
        assert extract.get('NotConcernedTheme')[5]['Code'] == 'ch.Sicherheitszonenplan'
        assert extract.get('NotConcernedTheme')[6]['Code'] == 'ch.BelasteteStandorteMilitaer'
        assert extract.get('NotConcernedTheme')[7]['Code'] == 'ch.BelasteteStandorteZivileFlugplaetze'
        assert extract.get('NotConcernedTheme')[8]['Code'] == 'ch.BelasteteStandorteOeffentlicherVerkehr'
        assert extract.get('NotConcernedTheme')[9]['Code'] == 'ch.Grundwasserschutzzonen'
        assert extract.get('NotConcernedTheme')[10]['Code'] == 'ch.Grundwasserschutzareale'
        assert extract.get('NotConcernedTheme')[11]['Code'] == 'ch.Laermempfindlichkeitsstufen'
        assert extract.get('NotConcernedTheme')[12]['Code'] == 'ch.StatischeWaldgrenzen'
        assert extract.get('NotConcernedTheme')[13]['Code'] == 'ch.Waldabstandslinien'

    if topics == 'ALL_FEDERAL':
        assert len(real_estate.get('RestrictionOnLandownership')) == 1
        assert len(extract.get('ConcernedTheme')) == 1
        assert len(extract.get('NotConcernedTheme')) == 9
        assert len(extract.get('ThemeWithoutData')) == 0
        restrictions = real_estate.get('RestrictionOnLandownership')
        assert restrictions[0]['Theme']['Code'] == 'ch.BaulinienNationalstrassen'

    if topics == 'ch.BelasteteStandorte,ch.ProjektierungszonenEisenbahnanlagen':
        assert len(real_estate.get('RestrictionOnLandownership')) == 1
        assert len(extract.get('ConcernedTheme')) == 1
        assert len(extract.get('NotConcernedTheme')) == 1
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


def test_format_url():
    request = MockRequest()
    request.matchdict.update({
        'format': 'URL'
    })
    request.params.update({
        'EGRID': 'TEST'
    })
    service = PlrWebservice(request)
    response = service.get_extract_by_id()
    assert isinstance(response, HTTPFound)
    assert response.location == 'https://geoview.bl.ch/oereb/?egrid=TEST'
