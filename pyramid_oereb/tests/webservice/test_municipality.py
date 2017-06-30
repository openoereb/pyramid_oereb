# -*- coding: utf-8 -*-
import pytest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response

from pyramid_oereb.tests.conftest import MockRequest
from pyramid_oereb.views.webservice import Municipality


def test_get_image(connection):
    assert connection.closed
    request = MockRequest()
    request.matchdict.update({
        'fosnr': '1234'
    })
    webservice = Municipality(request)
    result = webservice.get_image()
    assert isinstance(result, Response)
    assert result.body == 'abcdefg'


def test_get_image_invalid(connection):
    assert connection.closed
    request = MockRequest()
    request.matchdict.update({
        'fosnr': '0'
    })
    webservice = Municipality(request)
    with pytest.raises(HTTPNotFound):
        webservice.get_image()
