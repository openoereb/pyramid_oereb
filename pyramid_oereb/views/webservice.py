# -*- coding: utf-8 -*-
from pyramid_oereb import route_prefix
from pyramid_oereb.lib.webservice import ConfigReader

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
        """
        Returns the available versions of this service.
        :return: The available service versions.
        :rtype:  dict
        """
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

    def get_capabilities(self):
        """
        Returns the capabilities of this service.
        :return: The service capabilities.
        :rtype:  dict
        """
        settings = self._request_.registry.settings
        cfg = ConfigReader(
            settings.get('pyramid_oereb.cfg.file'),
            settings.get('pyramid_oereb.cfg.section')
        )
        return {
            u'topic': [],
            u'municipality': [],
            u'flavour': [],
            u'language': [],
            u'crs': cfg.get_crs()
        }
