# -*- coding: utf-8 -*-
import json

from jsonschema import Draft4Validator
from tests.conftest import MockRequest, schema_json_versions
from pyramid_oereb.views.webservice import PlrWebservice


def test_getversions():
    webservice = PlrWebservice(MockRequest())
    versions = webservice.get_versions()
    with open(schema_json_versions) as f:
        schema = json.loads(f.read())
    Draft4Validator.check_schema(schema)
    validator = Draft4Validator(schema)
    validator.validate(versions)
    assert isinstance(versions, dict)
    supported_version = versions.get('GetVersionsResponse')
    assert len(supported_version.get('supportedVersion')) == 1
