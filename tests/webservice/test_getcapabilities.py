# -*- coding: utf-8 -*-

import json

from jsonschema import Draft4Validator

from tests import schema_json_extract, pyramid_oereb_test_config
from tests.mockrequest import MockRequest
from pyramid_oereb.views.webservice import PlrWebservice


def test_getcapabilities():
    with pyramid_oereb_test_config():
        request = MockRequest(current_route_url='http://example.com/oereb/capabilities/json')

        # Add params to matchdict as the view will do it for /capabilities/{format}
        request.matchdict.update({
            'format': u'json'
        })

        service = PlrWebservice(request)
        with open(schema_json_extract) as f:
            schema = json.loads(f.read())
        Draft4Validator.check_schema(schema)
        validator = Draft4Validator(schema)
        response = service.get_capabilities().json
        validator.validate(response)

        assert isinstance(response, dict)
        caps = response.get('GetCapabilitiesResponse')

        assert isinstance(caps[u'topic'], list)
        assert len(caps[u'topic']) == 17
        assert caps[u'topic'][15][u'Code'] == u'ForestPerimeters'
        forest_perimeter_languages = list(map(lambda l: l[u'Language'], caps[u'topic'][15][u'Text']))
        assert u'de' in forest_perimeter_languages
        assert u'fr' in forest_perimeter_languages
        assert u'it' in forest_perimeter_languages
        assert u'rm' in forest_perimeter_languages

        assert isinstance(caps[u'flavour'], list)
        assert len(caps[u'flavour']) == 3
        assert u'REDUCED' in caps[u'flavour']
        assert u'FULL' in caps[u'flavour']
        assert u'EMBEDDABLE' in caps[u'flavour']

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
