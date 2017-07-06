# -*- coding: utf-8 -*-
import pytest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response

from tests.conftest import MockRequest
from pyramid_oereb.views.webservice import Symbol


def test_get_image():
    request = MockRequest()
    request.matchdict.update({
        'theme_code': 'ContaminatedSites',
        'type_code': 'test'
    })
    webservice = Symbol(request)
    result = webservice.get_image()
    assert isinstance(result, Response)
    assert result.body == bin(1)


def test_get_image_invalid():
    request = MockRequest()
    request.matchdict.update({
        'theme_code': 'ContaminatedSites',
        'type_code': 'notExisting'
    })
    webservice = Symbol(request)
    with pytest.raises(HTTPNotFound):
        webservice.get_image()
