# -*- coding: utf-8 -*-

import pytest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response

from pyramid_oereb.lib.adapter import FileAdapter
from tests.mockrequest import MockRequest
from pyramid_oereb.views.webservice import Symbol


def test_get_image():
    request = MockRequest()
    request.matchdict.update({
        'theme_code': 'ContaminatedSites',
        'view_service_id': '1',
        'type_code': 'CodeA'
    })
    webservice = Symbol(request)
    result = webservice.get_image()
    assert isinstance(result, Response)
    assert result.body == FileAdapter().read('tests/resources/symbol.png')


def test_get_image_invalid():
    request = MockRequest()
    request.matchdict.update({
        'theme_code': 'ContaminatedSites',
        'view_service_id': '1',
        'type_code': 'notExisting'
    })
    webservice = Symbol(request)
    with pytest.raises(HTTPNotFound):
        webservice.get_image()
