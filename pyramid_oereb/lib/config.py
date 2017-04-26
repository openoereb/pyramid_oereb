# -*- coding: utf-8 -*-
import os

import yaml
from pyramid.config import ConfigurationError


def parse(cfg_file, cfg_section):
    """
    Parses the defined YAML file and returns the defined section as dictionary.
    :param cfg_file:    The YAML file to be parsed.
    :type  cfg_file:    str
    :param cfg_section: The section to be returned.
    :type  cfg_section: str
    :return: The parsed section as dictionary.
    :rtype: dict
    """
    if cfg_file is None:
        raise ConfigurationError('Missing configuration parameter "pyramid_oereb.cfg.file".')
    if cfg_section is None:
        raise ConfigurationError('Missing configuration parameter "pyramid_oereb.cfg.section".')

    try:
        with open(cfg_file) as f:
            content = yaml.safe_load(f.read())
    except IOError as e:
        import sys
        raise type(e), type(e)(e.message + '{0} \'{1}\', Current working directory is {2}'.format(
            e.args[1], e.filename, os.getcwd())), sys.exc_info()[2]
    cfg = content.get(cfg_section)
    if cfg is None:
        raise ConfigurationError('YAML file contains no section "{0}"'.format(cfg_section))
    return cfg


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

    def get_topic(self):
        """
        Returns a list of available topics.
        :return: The available topics.
        :rtype: list
        """
        result = list()
        plrs = self.__config__.get('plrs')
        if plrs and isinstance(plrs, list):
            for theme in plrs:
                result.append({
                    u'Code': unicode(theme.get('code')),
                    u'Text': {
                        u'Language': unicode(theme.get('language')),
                        u'Text': unicode(theme.get('label'))
                    }
                })
        return result

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

    def get_real_estate_config(self):
        """
        Returns a dictionary of the configured real estate settings.
        :return: The configured real estate settings.
        :rtype: dict
        """
        return self.__config__.get('real_estate')

    def get_address_config(self):
        """
        Returns a dictionary of the configured address settings.
        :return: The configured address settings.
        :rtype: dict
        """
        return self.__config__.get('address')

    def get_glossary_config(self):
        """
        Returns a dictionary of the configured glossary settings.
        :return: The configured glossary settings.
        :rtype: dict
        """
        return self.__config__.get('glossary')

    def get_exclusion_of_liability_config(self):
        """
        Returns a dictionary of the configured exclusion_of_liability settings.
        :return: The configured exclusion_of_liability settings.
        :rtype: dict
        """
        return self.__config__.get('exclusion_of_liability')

    def get_municipality_config(self):
        """
        Returns a dictionary of the configured municipality settings.
        :return: The configured municipality settings.
        :rtype: dict
        """
        return self.__config__.get('municipality')

    def get(self, key, default=None):
        """
        Returns the specified configuration value.
        :param key: Configuration parameter name.
        :type key: str
        :param default: Default value if the specified parameter is not defined. Defaults to None.
        :return: The specified configuration or default value
        """
        return self.__config__.get(key, default)
