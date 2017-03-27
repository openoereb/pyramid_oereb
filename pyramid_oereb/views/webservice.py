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
        return {
            'supportedVersion': [
                {
                    'version': '1.0.0',
                    'serviceEndpointBase': self._request_.application_url + '/' + route_prefix
                }
            ]
        }
