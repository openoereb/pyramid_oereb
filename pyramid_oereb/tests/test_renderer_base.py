# -*- coding: utf-8 -*-
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
