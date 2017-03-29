# -*- coding: utf-8 -*-

import json

from jsonschema import validate
from pyramid.testing import DummyRequest, testConfig

from pyramid_oereb.views.webservice import PlrWebservice


def test_getextractbyid():
    settings = {
        'pyramid_oereb.cfg.file': 'pyramid_oereb_test.yml',
        'pyramid_oereb.cfg.section': 'pyramid_oereb'
    }
    with testConfig(settings=settings):

        service = PlrWebservice(DummyRequest())
        extract = service.get_extract_by_id()
        # TODO: Activate validation when schema issues are fixed
        # with open('./pyramid_oereb/tests/resources/schema_webservices.json') as f:
        #     schema = json.load(f)
        # validate(extract, schema)

        assert isinstance(extract, dict)

