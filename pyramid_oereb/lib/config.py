# -*- coding: utf-8 -*-
import os

import yaml
from pyramid.config import ConfigurationError
from pyramid_oereb.lib.adapter import FileAdapter
from pyramid_oereb.lib.records.office import OfficeRecord
from pyramid_oereb.lib.records.logo import LogoRecord


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

    def get_extract_config(self):
        """
        Returns a dictionary of the configured extract settings.
        :return: The configured extract settings.
        :rtype: dict
        """
        return self.__config__.get('extract')

    def get_plr_cadastre_authority(self):
        """
        Returns an office record for the configured PLR cadastre authority.
        :return: The configured PLR cadastre authority.
        :rtype: pyramid_oereb.lib.records.office.OfficeRecord
        """
        cfg = self.__config__.get('plr_cadastre_authority')
        return OfficeRecord(
            cfg.get('name'),
            uid=cfg.get('uid'),
            office_at_web=cfg.get('office_at_web'),
            line1=cfg.get('line1'),
            line2=cfg.get('line2'),
            street=cfg.get('street'),
            number=cfg.get('number'),
            postal_code=cfg.get('postal_code'),
            city=cfg.get('city')
        )

    def get_logo_config(self):
        """
        Returns a dictionary of the configured file path's to the logos.
        :return: The configured paths to the logos wrapped in a dictionary.
        :rtype: dict
        """
        confederation_fkey = 'confederation'
        oereb_key = 'oereb'
        canton_key = 'canton'
        msg = 'The definition for "{key}" must be set. Got: {found_config}'
        logo_dict = self.__config__.get('logo')
        if not logo_dict.get(confederation_fkey):
            raise ConfigurationError(msg.format(key=confederation_fkey, found_config=logo_dict))
        if not logo_dict.get(oereb_key):
            raise ConfigurationError(msg.format(key=oereb_key, found_config=logo_dict))
        if not logo_dict.get(canton_key):
            raise ConfigurationError(msg.format(key=canton_key, found_config=logo_dict))
        file_adapter = FileAdapter()
        confederation_logo = LogoRecord(file_adapter.read(logo_dict.get(confederation_fkey)))
        oereb_logo = LogoRecord(file_adapter.read(logo_dict.get(oereb_key)))
        canton_logo = LogoRecord(file_adapter.read(logo_dict.get(canton_key)))

        return {
            confederation_fkey: confederation_logo,
            oereb_key: oereb_logo,
            canton_key: canton_logo
        }

    def get(self, key, default=None):
        """
        Returns the specified configuration value.
        :param key: Configuration parameter name.
        :type key: str
        :param default: Default value if the specified parameter is not defined. Defaults to None.
        :return: The specified configuration or default value
        """
        return self.__config__.get(key, default)
