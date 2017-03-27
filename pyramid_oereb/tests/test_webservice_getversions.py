# -*- coding: utf-8 -*-
import json

from jsonschema import validate
from pyramid.testing import DummyRequest

from pyramid_oereb.views.webservice import PlrWebservice


def test_getversions():
    webservice = PlrWebservice(DummyRequest())
    versions = webservice.get_versions()
    with open('./pyramid_oereb/tests/resources/schema_versions.json') as f:
        schema = json.load(f)
    validate(versions, schema)
    assert len(versions.get('supportedVersion')) == 1
