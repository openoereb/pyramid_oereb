# -*- coding: utf-8 -*-
from jsonschema import Draft4Validator

from tests.mockrequest import MockRequest
from pyramid_oereb.core.views.webservice import PlrWebservice


def test_getcapabilities(pyramid_oereb_test_config, schema_json_extract, municipalities, themes):
    request = MockRequest(current_route_url='http://example.com/oereb/capabilities/json')

    # Add params to matchdict as the view will do it for /capabilities/{format}
    request.matchdict.update({
        'format': u'json'
    })

    service = PlrWebservice(request)
    Draft4Validator.check_schema(schema_json_extract)
    validator = Draft4Validator(schema_json_extract)
    response = service.get_capabilities().json
    validator.validate(response)

    assert isinstance(response, dict)
    caps = response.get('GetCapabilitiesResponse')

    assert isinstance(caps[u'topic'], list)
    assert len(caps[u'topic']) == 4
    assert caps[u'topic'][1][u'Code'] == u'ch.StatischeWaldgrenzen'
    forest_perimeter_languages = list(map(lambda x: x[u'Language'], caps[u'topic'][1][u'Text']))
    assert u'de' in forest_perimeter_languages
    assert u'fr' in forest_perimeter_languages
    assert u'it' in forest_perimeter_languages
    assert u'rm' in forest_perimeter_languages

    assert isinstance(caps[u'flavour'], list)
    assert len(caps[u'flavour']) == 2
    assert u'REDUCED' in caps[u'flavour']
    assert u'SIGNED' in caps[u'flavour']

    assert isinstance(caps[u'language'], list)
    assert len(caps[u'language']) == 4
    assert u'de' in caps[u'language']
    assert u'fr' in caps[u'language']
    assert u'it' in caps[u'language']
    assert u'rm' in caps[u'language']

    assert isinstance(caps[u'crs'], list)
    assert len(caps[u'crs']) == 1
    assert caps[u'crs'][0] == u'epsg:2056'

    assert isinstance(caps[u'municipality'], list)
