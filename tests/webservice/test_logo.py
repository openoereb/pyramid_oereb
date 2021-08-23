# -*- coding: utf-8 -*-
import pytest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response

from tests.mockrequest import MockRequest
from pyramid_oereb.views.webservice import Logo


def test_get_image():
    request = MockRequest()
    request.matchdict.update({
        'logo': 'oereb',
        'language': 'de'
    })
    webservice = Logo(request)
    result = webservice.get_image()
    assert isinstance(result, Response)


def test_get_image_invalid():
    request = MockRequest()
    request.matchdict.update({
        'logo': 'invalid',
        'language': 'de'
    })
    webservice = Logo(request)
    with pytest.raises(HTTPNotFound):
        webservice.get_image()
