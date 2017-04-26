# -*- coding: utf-8 -*-


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
    with open(cfg_file) as f:
        content = yaml.safe_load(f.read())
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

    def get_municipality_config(self):
        """
        Returns a dictionary of the configured municipality settings.
        :return: The configured municipality settings.
        :rtype: dict
        """
        return self.__config__.get('municipality')

    def get_extract_config(self):
        """
        Returns a dictionary of the configured extract settings.
        :return: The configured extract settings.
        :rtype: dict
        """
        return self.__config__.get('extract')

    def get(self, key, default=None):
        """
        Returns the specified configuration value.
        :param key: Configuration parameter name.
        :type key: str
        :param default: Default value if the specified parameter is not defined. Defaults to None.
        :return: The specified configuration or default value
        """
        return self.__config__.get(key, default)


class RequestConfigurator(object):

    def __init__(self, real_estate_reader, municipality_reader, plr_sources, extract_reader):
        """
        A helper which provides runtime access to the instances of readers and sources read from config. This
        is a handy way provided by the pyramid web framework.
        :param real_estate_reader: The real estate reader instance for runtime use.
        :type real_estate_reader: pyramid_oereb.lib.readers.real_estate.RealEstateReader
        :param municipality_reader: The municipality reader instance for runtime use.
        :type municipality_reader: pyramid_oereb.lib.readers.municipality.MunicipalityReader
        :param plr_sources: The public law restriction source instances for runtime use wrapped in a list.
        :type plr_sources: list of pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
        :param extract_reader: The extract reader instance for runtime use.
        :type extract_reader: pyramid_oereb.lib.readers.extract.ExtractReader
        """
        self._real_estate_reader_ = real_estate_reader
        self._municipality_reader_ = municipality_reader
        self._plr_sources_ = plr_sources
        self._extract_reader_ = extract_reader

    @property
    def real_estate_reader(self):
        """

        :return: The real estate reader instance.
        :rtype real_estate_reader: pyramid_oereb.lib.readers.real_estate.RealEstateReader
        """
        return self._real_estate_reader_

    @property
    def municipality_reader(self):
        """

        :return: The municipality reader reader instance.
        :rtype municipality_reader: pyramid_oereb.lib.readers.municipality.MunicipalityReader
        """
        return self._municipality_reader_

    @property
    def plr_sources(self):
        """

        :return: The list of plr source instances.
        :rtype plr_sources: list of pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
        """
        return self._plr_sources_

    @property
    def extract_reader(self):
        """

        :return: The extract reader instance.
        :rtype extract_reader: pyramid_oereb.lib.readers.extract.ExtractReader
        """
        return self._extract_reader_
