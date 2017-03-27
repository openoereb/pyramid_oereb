# -*- coding: utf-8 -*-
import json

from jsonschema import validate
from pyramid.testing import DummyRequest

from pyramid_oereb.views.webservice import PlrWebservice


def test_getcapabilities():
    service = PlrWebservice(DummyRequest())
    with open('./pyramid_oereb/tests/resources/schema_webservices.json') as f:
        schema = json.load(f)
    caps = service.get_capabilities()
    validate(caps, schema)
