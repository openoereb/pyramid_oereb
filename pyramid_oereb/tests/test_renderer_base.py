# -*- coding: utf-8 -*-
import pytest
import datetime
from pyramid.response import Response
from pyramid.testing import DummyRequest

from pyramid_oereb.lib.renderer import Base


class DummyRenderInfo(object):
    name = 'test'


def test_call():
    renderer = Base(DummyRenderInfo())
    request = DummyRequest()
    assert isinstance(renderer.info, DummyRenderInfo)
    assert renderer.info.name == 'test'
    assert Base.get_response({}) is None
    assert isinstance(Base.get_response({'request': request}), Response)


@pytest.mark.parametrize('input,result', [
    (datetime.date.today(), datetime.date.today().strftime('%Y-%m-%dT%H:%M:%S')),
    ('test', 'test')
])
def test_date_time(input, result):
    assert Base.date_time(input) == result
