# -*- coding: utf-8 -*-
import pytest
from unittest.mock import patch
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response

from tests.mockrequest import MockRequest
from pyramid_oereb.core.views.webservice import Logo
from pyramid_oereb.core.config import Config


def test_get_image(pyramid_oereb_test_config, logo_test_data):
    with patch.object(Config, 'logos', logo_test_data):
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
