# -*- coding: utf-8 -*-
from pyramid.httpexceptions import HTTPNotFound

from pyramid_oereb.views.webservice import Error
from tests.conftest import MockRequest


def test_init():
    request = MockRequest()
    error = Error(request)
    assert error._request == request


def test_not_found():
    request = MockRequest()
    error = Error(request)
    response = error.not_found()
    assert isinstance(response, HTTPNotFound)
    assert response.status_int == 404
