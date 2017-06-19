# -*- coding: utf-8 -*-
import pytest
import datetime
from pyramid.response import Response
from pyramid.testing import DummyRequest

from pyramid_oereb.lib.renderer import Base
from pyramid_oereb.tests.renderer import DummyRenderInfo


def test_call():
    renderer = Base(DummyRenderInfo())
    assert isinstance(renderer.info, DummyRenderInfo)
    assert renderer.info.name == 'test'


@pytest.mark.parametrize('input,result', [
    (datetime.date.today(), datetime.date.today().strftime('%Y-%m-%dT%H:%M:%S')),
    ('test', 'test')
])
def test_date_time(input, result):
    assert Base.date_time(input) == result


def test_get_request():
    request = Base.get_request({
        'request': DummyRequest()
    })
    assert isinstance(request, DummyRequest)


def test_get_missing_request():
    request = Base.get_request({})
    assert request is None


def test_get_response():
    response = Base.get_response({
        'request': DummyRequest()
    })
    assert isinstance(response, Response)


def test_get_missing_response():
    response = Base.get_response({})
    assert response is None
