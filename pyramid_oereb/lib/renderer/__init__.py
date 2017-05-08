# -*- coding: utf-8 -*-


class Base(object):
    def __init__(self, info):
        """
        Creates a new base renderer instance.
        :param info: Info object.
        :type info: pyramid.interfaces.IRendererInfo
        """
        self._info_ = info

    @classmethod
    def get_response(cls, system):
        """
        Returns the response object if available.
        :param system: The available system properties.
        :type system: dict
        :return: The response object.
        :rtype: pyramid.response.Response or None
        """
        request = system.get('request')
        if request is not None:
            return request.response
        return None

    @property
    def info(self):
        return self._info_
