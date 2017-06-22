# -*- coding: utf-8 -*-
import pytest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response

from pyramid_oereb.tests.conftest import MockRequest
from pyramid_oereb.views.webservice import Symbol


@pytest.mark.last
def test_get_image(connection):
    assert connection.closed
    request = MockRequest()
    request.matchdict.update({
        'theme_code': 'ContaminatedSites',
        'type_code': 'test'
    })
    webservice = Symbol(request)
    result = webservice.get_image()
    assert isinstance(result, Response)
    assert result.body == bin(1)


@pytest.mark.last
def test_get_image_invalid(connection):
    assert connection.closed
    request = MockRequest()
    request.matchdict.update({
        'theme_code': 'ContaminatedSites',
        'type_code': 'notExisting'
    })
    webservice = Symbol(request)
    with pytest.raises(HTTPNotFound):
        webservice.get_image()
