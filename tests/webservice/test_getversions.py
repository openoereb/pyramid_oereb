# -*- coding: utf-8 -*-
import json

from jsonschema import Draft4Validator
from tests.conftest import MockRequest, schema_json_versions, pyramid_oereb_test_config
from pyramid_oereb.views.webservice import PlrWebservice


def test_getversions_json():
    with pyramid_oereb_test_config():
        request = MockRequest(current_route_url='http://example.com/oereb/versions/json')

        # Add params to matchdict as the view will do it for /versions/{format}
        request.matchdict.update({
          'format': u'json'
        })

        webservice = PlrWebservice(request)
        versions = webservice.get_versions().json
        with open(schema_json_versions) as f:
            schema = json.loads(f.read())
        Draft4Validator.check_schema(schema)
        validator = Draft4Validator(schema)
        validator.validate(versions)
        assert isinstance(versions, dict)
        supported_version = versions.get('GetVersionsResponse')
        assert len(supported_version.get('supportedVersion')) == 1
