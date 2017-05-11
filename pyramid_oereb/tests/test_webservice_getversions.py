# -*- coding: utf-8 -*-
import json

from jsonschema import validate
from pyramid_oereb.tests.conftest import MockRequest
from pyramid_oereb.views.webservice import PlrWebservice


def test_getversions():
    webservice = PlrWebservice(MockRequest())
    versions = webservice.get_versions()
    with open('./pyramid_oereb/tests/resources/schema_versions.json') as f:
        schema = json.load(f)
    validate(versions, schema)
    assert len(versions.get('supportedVersion')) == 1
