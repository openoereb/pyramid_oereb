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

        Returns:
            pyramid.response.ResponseorNone: The response object.
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

        Returns:
            pyramid.request.RequestorNone: The request object.
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

        Returns:
            str: The formatted date/time.
        """
        if isinstance(dt, datetime.date) or isinstance(dt, datetime.time)\
                or isinstance(dt, datetime.datetime):
            return dt.strftime('%Y-%m-%dT%H:%M:%S')
        return dt

    @property
    def info(self):
        """

        Returns:
            pyramid.interfaces.IRendererInfo: The passed renderer info object.
        """
        return self._info_
