# -*- coding: utf-8 -*-

import json

from jsonschema import Draft4Validator

from pyramid_oereb.tests.conftest import MockRequest
from pyramid_oereb.views.webservice import PlrWebservice


def test_getcapabilities(config):
    service = PlrWebservice(MockRequest())
    with open('./pyramid_oereb/tests/resources/schema_webservices.json') as f:
        schema = json.loads(f.read())
    Draft4Validator.check_schema(schema)
    validator = Draft4Validator(schema)
    response = service.get_capabilities()
    validator.validate(response)

    assert isinstance(response, dict)
    caps = response.get('GetCapabilitiesResponse')

    assert isinstance(caps[u'topic'], list)
    assert len(caps[u'topic']) == 17
    assert caps[u'topic'][15][u'Code'] == u'ForestPerimeters'
    assert caps[u'topic'][15][u'Text'][0][u'Language'] == u'de'

    assert isinstance(caps[u'flavour'], list)
    assert len(caps[u'flavour']) == 3
    assert caps[u'flavour'][0] == u'REDUCED'

    assert isinstance(caps[u'language'], list)
    assert len(caps[u'language']) == 4
    assert caps[u'language'][0] == u'de'

    assert isinstance(caps[u'crs'], list)
    assert len(caps[u'crs']) == 1
    assert caps[u'crs'][0] == u'epsg:2056'

    assert isinstance(caps[u'municipality'], list)
