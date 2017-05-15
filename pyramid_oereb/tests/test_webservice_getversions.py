# -*- coding: utf-8 -*-
import json

from jsonschema import Draft4Validator
from pyramid_oereb.tests.conftest import MockRequest
from pyramid_oereb.views.webservice import PlrWebservice


def test_getversions():
    webservice = PlrWebservice(MockRequest())
    versions = webservice.get_versions()
    with open('./pyramid_oereb/tests/resources/schema_versions.json') as f:
        schema = json.load(f)
    Draft4Validator.check_schema(schema)
    validator = Draft4Validator(schema)
    validator.validate(versions)
    assert len(versions.get('supportedVersion')) == 1
