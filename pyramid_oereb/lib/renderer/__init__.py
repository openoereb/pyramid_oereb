# -*- coding: utf-8 -*-
import datetime

import logging
from pyramid.httpexceptions import HTTPServerError
from pyramid.path import DottedNameResolver
from pyramid.request import Request
from pyramid.testing import DummyRequest

from pyramid_oereb import Config


log = logging.getLogger(__name__)


class Base(object):
    def __init__(self, info):
        """
        Creates a new base renderer instance.

        Args:
            info (pyramid.interfaces.IRendererInfo): Info object.
        """
        self._info_ = info
        self._language = str(Config.get('default_language')).lower()

    @classmethod
    def get_symbol_ref(cls, request, record):
        """
        Returns the link to the symbol of the specified public law restriction.

        Args:
            request (pyramid.request.Request): The current request instance.
            record (pyramid_oereb.lib.records.plr.PlrRecord or
                pyramid_oereb.lib.records.view_service.LegendEntryRecord): The record of the public law
                restriction to get the symbol reference for.

        Returns:
            uri: The link to the symbol for the specified public law restriction.
        """
        method = None
        for plr in Config.get('plrs'):
            if str(plr.get('code')).lower() == str(record.theme.code).lower():
                method = DottedNameResolver().resolve(plr.get('hooks').get('get_symbol_ref'))
        if callable(method):
            return method(request, record)
        log.error('No "get_symbol_ref" method found for theme {}'.format(record.theme.code))
        raise HTTPServerError()

    @classmethod
    def get_response(cls, system):
        """
        Returns the response object if available.

        Args:
            system (dict): The available system properties.

        Returns:
            pyramid.response.Response or None: The response object.
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
            pyramid.request.Request or None: The request object.
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

    def get_localized_text(self, values):
        """
        Returns the requested language of a multilingual text element.

        Args:
            values (str or dict): The multilingual values encoded as JSON.

        Returns:
            dict of str: Dictionary containing the localized representation.
        """
        default_language = Config.get('default_language')
        if isinstance(values, dict):
            if self._language in values:
                return {
                    'Language': self._language,
                    'Text': values.get(self._language)
                }
            else:
                return {
                    'Language': default_language,
                    'Text': values.get(default_language)
                }
        else:
            return {
                'Language': default_language,
                'Text': values
            }

    def get_multilingual_text(self, values):
        """
        Returns the set language of a multilingual text element.

        Args:
            values (str or dict): The multilingual values encoded as JSON.

        Returns:
            list of dict: List of dictionaries containing the multilingual representation.
        """
        return [self.get_localized_text(values)]

    @staticmethod
    def replace_de_umlaut(text):
        """
        Replaces all German special characters with the base character:
        ä -> a
        ö -> o
        ü -> u
        so that a proper sorting can be done according to the DIN 5007 norm

        Args:
            text (string): the string value

        Returns:
            new_text (string): with out umlaut
        """
        new_text=text.lower()
        new_text=new_text.replace(u'ä', u'a')
        new_text=new_text.replace(u'ö', u'o')
        new_text=new_text.replace(u'ü', u'u')

        return new_text
