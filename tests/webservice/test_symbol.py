# -*- coding: utf-8 -*-

import sys
import base64
import json
import pytest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response

from tests.conftest import MockRequest
from pyramid_oereb.views.webservice import Symbol


def test_get_image():
    request = MockRequest()
    request.matchdict.update({
        'theme_code': 'ContaminatedSites'
    })
    request.params.update({
        'CODE': 'test',
        'TEXT': base64.b64encode(json.dumps({'de': u'Test'}).encode('utf-8')).decode('ascii')
    })
    webservice = Symbol(request)
    result = webservice.get_image()
    assert isinstance(result, Response)
    if sys.version_info.major == 2:
        assert result.body == '1'
    else:
        assert result.body == b'1'


def test_get_image_invalid():
    request = MockRequest()
    request.matchdict.update({
        'theme_code': 'ContaminatedSites'
    })
    request.params.update({
        'CODE': 'notExisting',
        'TEXT': base64.b64encode(json.dumps({'de': u'Test'}).encode('utf-8')).decode('ascii')
    })
    webservice = Symbol(request)
    with pytest.raises(HTTPNotFound):
        webservice.get_image()
