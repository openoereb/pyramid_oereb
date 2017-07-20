# -*- coding: utf-8 -*-
import pytest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response

from tests.conftest import MockRequest
from pyramid_oereb.views.webservice import Logo


def test_get_image(config):
    assert isinstance(config._config, dict)
    request = MockRequest()
    request.matchdict.update({
        'logo': 'oereb'
    })
    webservice = Logo(request)
    result = webservice.get_image()
    assert isinstance(result, Response)
    assert result.body == config.get_logo_config().get('oereb').content


def test_get_image_invalid():
    request = MockRequest()
    request.matchdict.update({
        'logo': 'invalid'
    })
    webservice = Logo(request)
    with pytest.raises(HTTPNotFound):
        webservice.get_image()
