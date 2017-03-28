# -*- coding: utf-8 -*-
from pyramid_oereb import route_prefix

__author__ = 'Karsten Deininger'
__create_date__ = '27.03.2017'


class PlrWebservice(object):
    def __init__(self, request):
        """
        This class provides the PLR webservice methods.
        :param request: The pyramid request instance.
        :type request:  pyramid.request.Request
        """
        self._request_ = request

    def get_versions(self):
        endpoint = self._request_.application_url
        if route_prefix:
            endpoint += '/' + route_prefix
        return {
            u'supportedVersion': [
                {
                    u'version': u'1.0.0',
                    u'serviceEndpointBase': unicode(endpoint)
                }
            ]
        }
