# -*- coding: utf-8 -*-

from pyramid_oereb.lib.config import parse


class ConfigReader(object):
    def __init__(self, config_file, config_section):
        """
        Loads configuration from yaml file and provides methods for generating webservice output.
        :param config_file: The configuration yaml file.
        :type config_file: str
        :param config_section: The section within the yaml file.
        :type config_section: str
        """
        self.__config__ = parse(config_file, config_section)

    def get_crs(self):
        """
        Returns a list of available crs.
        :return: The available crs.
        :rtype: list
        """
        crs = list()
        srid = self.__config__.get('srid')
        if srid:
            crs.append(u'epsg:' + unicode(srid))
        return crs

    def get_language(self):
        """
        Returns a list of available languages.
        :return: The available languages.
        :rtype: list
        """
        result = list()
        language = self.__config__.get('language')
        if language and isinstance(language, list):
            result.extend(language)
        return result

    def get_flavour(self):
        """
        Returns a list of available flavours.
        :return: The available flavours.
        :rtype: list
        """
        result = list()
        flavour = self.__config__.get('flavour')
        if flavour and isinstance(flavour, list):
            result.extend(flavour)
        return result
