# -*- coding: utf-8 -*-
import pytest
from pyramid.httpexceptions import HTTPBadRequest, HTTPNoContent
from pyramid.testing import testConfig

from pyramid_oereb.tests.conftest import MockRequest
from pyramid_oereb.views.webservice import PlrWebservice


def get_settings():
    return {
        'pyramid_oereb.cfg.file': 'pyramid_oereb_test.yml',
        'pyramid_oereb.cfg.section': 'pyramid_oereb'
    }


@pytest.mark.parametrize('params', [
    {
        'flavour': 'INVALIDFLAVOUR',
        'format': 'xml',
        'param1': 'egrid'
    },
    {
        'flavour': 'reduced',
        'format': 'INVALIDFORMAT',
        'param1': 'egrid'
    },
    {
        'flavour': 'FULL',
        'format': 'XML',
        'param1': 'egrid'
    },
    {
        'flavour': 'SIGNED',
        'format': 'JSON',
        'param1': 'egrid'
    },
    {
        'flavour': 'EMBEDDABLE',
        'format': 'PDF',
        'param1': 'egrid'
    },
    {
        'flavour': 'full',
        'format': 'PDF',
        'param1': 'GEOMETRY',
        'param2': 'egrid'
    }
])
def test_invalid_flavour(params):
    with testConfig(settings=get_settings()):
        request = MockRequest()
        request.matchdict.update(params)
        service = PlrWebservice(request)
        with pytest.raises(HTTPBadRequest):
            service.__validate_extract_params__()


@pytest.mark.parametrize('params,expected', [
    (
        {
            'flavour': 'SIGNED',
            'format': 'PDF',
            'param1': 'SomeEGRID'
        }, {
            'flavour': 'signed',
            'format': 'pdf',
            'geometry': False,
            'images': False,
            'egrid': 'SomeEGRID'
        }
    ),
    (
        {
            'flavour': 'FULL',
            'format': 'PDF',
            'param1': 'SomeIdent',
            'param2': 'SomeNumber'
        }, {
            'flavour': 'full',
            'format': 'pdf',
            'geometry': False,
            'images': False,
            'identdn': 'SomeIdent',
            'number': 'SomeNumber'
        }
    ),
    (
        {
            'flavour': 'REDUCED',
            'format': 'XML',
            'param1': 'GEOMETRY',
            'param2': 'SomeEGRID'
        }, {
            'flavour': 'reduced',
            'format': 'xml',
            'geometry': True,
            'images': False,
            'egrid': 'SomeEGRID'
        }
    ),
    (
        {
            'flavour': 'EMBEDDABLE',
            'format': 'JSON',
            'param1': 'GEOMETRY',
            'param2': 'SomeIdent',
            'param3': 'SomeNumber'
        }, {
            'flavour': 'embeddable',
            'format': 'json',
            'geometry': True,
            'images': False,
            'identdn': 'SomeIdent',
            'number': 'SomeNumber'
        }
    )
])
def test_matchdict(params, expected):
    with testConfig(settings=get_settings()):
        request = MockRequest()
        request.matchdict.update(params)
        service = PlrWebservice(request)
        params = service.__validate_extract_params__()
        assert params == expected


def test_params():
    with testConfig(settings=get_settings()):
        request = MockRequest()
        request.matchdict.update({
            'flavour': 'REDUCED',
            'format': 'XML',
            'param1': 'SomeEGRID'
        })
        request.params.update({
            'WITHIMAGES': '',
            'LANG': 'de',
            'TOPICS': 'top_A,top_B,top_C'
        })
        service = PlrWebservice(request)
        params = service.__validate_extract_params__()
        assert params == {
            'flavour': 'reduced',
            'format': 'xml',
            'geometry': False,
            'images': True,
            'egrid': 'SomeEGRID',
            'language': 'de',
            'topics': ['top_A', 'top_B', 'top_C']
        }


def test_return_extract():
    with testConfig(settings=get_settings()):
        request = MockRequest()
        request.matchdict.update({
            'flavour': 'REDUCED',
            'format': 'XML',
            'param1': 'GEOMETRY',
            'param2': 'SomeEGRID'
        })
        service = PlrWebservice(request)
        with pytest.raises(HTTPNoContent):
            service.get_extract_by_id()

        # TODO: Activate validation when schema issues are fixed
        # with open('./pyramid_oereb/tests/resources/schema_webservices.json') as f:
        #     schema = json.load(f)
        # validate(extract, schema)
