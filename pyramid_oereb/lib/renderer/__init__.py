# -*- coding: utf-8 -*-
import datetime

from pyramid.request import Request
from pyramid.testing import DummyRequest


class Base(object):
    def __init__(self, info):
        """
        Creates a new base renderer instance.

        Args:
            info (pyramid.interfaces.IRendererInfo): Info object.
        """
        self._info_ = info

    @classmethod
    def get_response(cls, system):
        """
        Returns the response object if available.

        Args:
            system (dict): The available system properties.
        :return: The response object.
        :rtype: pyramid.response.Response or None
        """
        request = system.get('request')
        if isinstance(request, Request) or isinstance(request, DummyRequest):
            return request.response
        return None

    @classmethod
    def get_request(cls, system):
        """
        Returns the request object if available.

        Args:
            system (dict): The available system properties.
        :return: The request object.
        :rtype: pyramid.request.Request or None
        """
        request = system.get('request')
        if isinstance(request, Request) or isinstance(request, DummyRequest):
            return request
        return None

    @classmethod
    def date_time(cls, dt):
        """
        Formats the date/time according to the specification.

        Args:
            dt (datetime.dateordatetime.timeordatetime.datetime): The datetime object.
        :return: The formatted date/time.
        :rtype: str
        """
        if isinstance(dt, datetime.date) or isinstance(dt, datetime.time)\
                or isinstance(dt, datetime.datetime):
            return dt.strftime('%Y-%m-%dT%H:%M:%S')
        return dt

    @property
    def info(self):
        """

        :return: The passed renderer info object.
        :rtype: pyramid.interfaces.IRendererInfo
        """
        return self._info_
