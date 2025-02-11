# -*- coding: utf-8 -*-
from pyramid.testing import DummyRequest

from pyramid_oereb.core.processor import create_processor
from pyramid_oereb.core.views.webservice import Parameter


class MockParameter(Parameter):
    def __init__(self):
        super(MockParameter, self).__init__('JSON', with_geometry=False, images=False)


class MockProcessor():

    @property
    def real_estate_reader(self):
        return


class MockRequest(DummyRequest):
    def __init__(self, current_route_url=None):
        super(MockRequest, self).__init__()

        self._current_route_url = current_route_url
        self.pyramid_oereb_processor = create_processor()

    def current_route_url(self, *elements, **kw):
        if self._current_route_url:
            return self._current_route_url
        else:
            return super(MockRequest, self).current_route_url(*elements, **kw)
