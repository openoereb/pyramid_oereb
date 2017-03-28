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
        crs = list()
        srid = self.__config__.get('srid')
        if srid:
            crs.append(u'epsg:' + unicode(srid))
        return crs

    def get_language(self):
        result = list()
        language = self.__config__.get('language')
        print language
        if language and isinstance(language, list):
            result.extend(language)
        return result
