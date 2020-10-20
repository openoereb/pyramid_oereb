# -*- coding: utf-8 -*-
from pyramid.testing import DummyRequest

from pyramid_oereb.views.webservice import Parameter


class MockParameter(Parameter):
    def __init__(self):
        super(MockParameter, self).__init__('JSON', flavour='REDUCED', with_geometry=False, images=False)


class MockRequest(DummyRequest):
    def __init__(self, current_route_url=None):
        super(MockRequest, self).__init__()

        self._current_route_url = current_route_url

    def current_route_url(self, *elements, **kw):
        if self._current_route_url:
            return self._current_route_url
        else:
            return super(MockRequest, self).current_route_url(*elements, **kw)
