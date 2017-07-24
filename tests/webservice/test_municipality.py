# -*- coding: utf-8 -*-

import sys
import pytest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response

from tests.conftest import MockRequest
from pyramid_oereb.views.webservice import Municipality


def test_get_image():
    request = MockRequest()
    request.matchdict.update({
        'fosnr': '1234'
    })
    webservice = Municipality(request)
    result = webservice.get_image()
    assert isinstance(result, Response)
    if sys.version_info.major == 2:
        assert result.body == 'abcdefg'
    else:
        assert result.body == b'abcdefg'


def test_get_image_invalid():
    request = MockRequest()
    request.matchdict.update({
        'fosnr': '0'
    })
    webservice = Municipality(request)
    with pytest.raises(HTTPNotFound):
        webservice.get_image()
