# -*- coding: utf-8 -*-
import json

from jsonschema import validate
from pyramid.testing import DummyRequest, testConfig

from pyramid_oereb.views.webservice import PlrWebservice


def test_getcapabilities():
    settings = {
        'pyramid_oereb.cfg.file': 'pyramid_oereb.yml',
        'pyramid_oereb.cfg.section': 'pyramid_oereb'
    }
    with testConfig(settings=settings):
        service = PlrWebservice(DummyRequest())
        with open('./pyramid_oereb/tests/resources/schema_webservices.json') as f:
            schema = json.load(f)
        caps = service.get_capabilities()
        validate(caps, schema)
        assert isinstance(caps[u'crs'], list)
        assert len(caps[u'crs']) == 1
        assert caps[u'crs'][0] == u'epsg:2056'
