# -*- coding: utf-8 -*-
from jsonschema import Draft4Validator
from tests.mockrequest import MockRequest
from pyramid_oereb.core.views.webservice import PlrWebservice


def test_getversions_json(pyramid_oereb_test_config, schema_json_versions):
    request = MockRequest(current_route_url='http://example.com/oereb/versions/json')

    # Add params to matchdict as the view will do it for /versions/{format}
    request.matchdict.update({
        'format': u'json'
    })

    webservice = PlrWebservice(request)
    versions = webservice.get_versions().json
    Draft4Validator.check_schema(schema_json_versions)
    validator = Draft4Validator(schema_json_versions)
    validator.validate(versions)
    assert isinstance(versions, dict)
    supported_version = versions.get('GetVersionsResponse')
    assert len(supported_version.get('supportedVersion')) == 1
