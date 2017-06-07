# -*- coding: utf-8 -*-
import os

import yaml
from pyramid.config import ConfigurationError
from pyramid_oereb.lib.adapter import FileAdapter
from pyramid_oereb.lib.records.office import OfficeRecord
from pyramid_oereb.lib.records.logo import LogoRecord
from pyramid_oereb.lib.records.theme import ThemeRecord


def parse(cfg_file, cfg_section):
    """
    Parses the defined YAML file and returns the defined section as dictionary.

    :param cfg_file: The YAML file to be parsed.
    :type  cfg_file: str
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
        e.strerror = '{0}{1} \'{2}\', Current working directory is {3}'.format(
            e.strerror, e.args[1], e.filename, os.getcwd())
        raise
    cfg = content.get(cfg_section)
    if cfg is None:
        raise ConfigurationError('YAML file contains no section "{0}"'.format(cfg_section))
    return cfg


class Config(object):

    _config = None

    @staticmethod
    def init(configfile, configsection):
        """
        Loads configuration from yaml file and provides methods for generating webservice output.

        :param config_file: The configuration yaml file.
        :type config_file: str
        :param config_section: The section within the yaml file.
        :type config_section: str
        """
        assert Config._config is None

        Config._config = parse(configfile, configsection)

    @staticmethod
    def update_settings(settings):
        settings.update(Config._config)

    @staticmethod
    def get_themes():
        """
        Returns a list of available themes.

        :return: The available themes.
        :rtype: list of pyramid_oereb.lib.records.theme.ThemeRecord
        """
        assert Config._config is not None

        result = list()
        plrs = Config._config.get('plrs')
        if plrs and isinstance(plrs, list):
            for theme in plrs:
                result.append(ThemeRecord(
                    theme.get('code'),
                    theme.get('text')
                ))
        return result

    @staticmethod
    def get_theme(code):
        """
        Returns the theme with the specified code.

        :param code: The theme's code.
        :type code: str
        :return: The theme with the specified code.
        :rtype: pyramid_oereb.lib.records.theme.ThemeRecord or None
        """
        assert Config._config is not None

        plrs = Config._config.get('plrs')
        if plrs and isinstance(plrs, list):
            for theme in plrs:
                if theme.get('code') == code:
                    return ThemeRecord(
                        theme.get('code'),
                        theme.get('text')
                    )
        return None

    @staticmethod

    def get_theme_thresholds(code):
        """
        Returns the limits for the geometries of the theme with the specified code.

        :param code: The theme's code.
        :type code: str
        :return: The geometric tolerances for this theme.
        :rtype: dict
        """
        assert Config._config is not None

        plrs = Config._config.get('plrs')
        if plrs and isinstance(plrs, list):
            for theme in plrs:
                if theme.get('code') == code:
                    return theme.get('plr_thresholds')
        return None

    def get_all_federal():
        assert Config._config is not None
        federal = list()
        plrs = Config._config.get('plrs')
        if plrs and isinstance(plrs, list):
            for plr in plrs:
                if plr.get('federal'):
                    federal.append(plr.get('code'))
        return federal

    @staticmethod
    def get_crs():
        """
        Returns a list of available crs.

        :return: The available crs.
        :rtype: list
        """
        assert Config._config is not None

        crs = list()
        srid = Config._config.get('srid')
        if srid:
            crs.append(u'epsg:' + unicode(srid))
        return crs

    @staticmethod
    def get_language():
        """
        Returns a list of available languages.

        :return: The available languages.
        :rtype: list
        """
        assert Config._config is not None

        result = list()
        language = Config._config.get('language')
        if language and isinstance(language, list):
            result.extend(language)
        return result

    @staticmethod
    def get_flavour():
        """
        Returns a list of available flavours.

        :return: The available flavours.
        :rtype: list
        """
        assert Config._config is not None

        result = list()
        flavour = Config._config.get('flavour')
        if flavour and isinstance(flavour, list):
            result.extend(flavour)
        return result

    @staticmethod
    def get_real_estate_config():
        """
        Returns a dictionary of the configured real estate settings.

        :return: The configured real estate settings.
        :rtype: dict
        """
        assert Config._config is not None

        return Config._config.get('real_estate')

    @staticmethod
    def get_address_config():
        """
        Returns a dictionary of the configured address settings.

        :return: The configured address settings.
        :rtype: dict
        """
        assert Config._config is not None

        return Config._config.get('address')

    @staticmethod
    def get_glossary_config():
        """
        Returns a dictionary of the configured glossary settings.

        :return: The configured glossary settings.
        :rtype: dict
        """
        assert Config._config is not None

        return Config._config.get('glossary')

    @staticmethod
    def get_exclusion_of_liability_config():
        """
        Returns a dictionary of the configured exclusion_of_liability settings.

        :return: The configured exclusion_of_liability settings.
        :rtype: dict
        """
        assert Config._config is not None

        return Config._config.get('exclusion_of_liability')

    @staticmethod
    def get_municipality_config():
        """
        Returns a dictionary of the configured municipality settings.

        :return: The configured municipality settings.
        :rtype: dict
        """
        assert Config._config is not None

        return Config._config.get('municipality')

    @staticmethod
    def get_extract_config():
        """
        Returns a dictionary of the configured extract settings.

        :return: The configured extract settings.
        :rtype: dict
        """
        assert Config._config is not None

        return Config._config.get('extract')

    @staticmethod
    def get_plr_cadastre_authority():
        """
        Returns an office record for the configured PLR cadastre authority.

        :return: The configured PLR cadastre authority.
        :rtype: pyramid_oereb.lib.records.office.OfficeRecord
        """
        assert Config._config is not None

        cfg = Config._config.get('plr_cadastre_authority')
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

    @staticmethod
    def get_logo_config():
        """
        Returns a dictionary of the configured file path's to the logos.

        :return: The configured paths to the logos wrapped in a dictionary.
        :rtype: dict
        """
        assert Config._config is not None

        confederation_fkey = 'confederation'
        oereb_key = 'oereb'
        canton_key = 'canton'
        msg = 'The definition for "{key}" must be set. Got: {found_config}'
        logo_dict = Config._config.get('logo')
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

    @staticmethod
    def get(key, default=None):
        """
        Returns the specified configuration value.

        :param key: Configuration parameter name.
        :type key: str
        :param default: Default value if the specified parameter is not defined. Defaults to None.
        :return: The specified configuration or default value
        """
        assert Config._config is not None

        return Config._config.get(key, default)

    @staticmethod
    def get_object_path(path, default=None, required=None):
        """
        Returns the configuration object at a specified path.

        example:
        get_object_path('app.print', {'dpi': 300}, ['map_size'])

        :param path: Dot separated path of the wonted object.
        :type path: str
        :param default: Default dictionary values of the object. Defaults to {}.
        :type default: dict
        :param required: The list of required sub values in the object. Defaults to [].
        :type required: list
        :return: The specified configuration object.
        """

        return Config._get_object_path(
            [], Config._config, path.split('.'),
            default if default is not None else {},
            required if required is not None else [])

    @staticmethod
    def _get_object_path(current_path, current_object, path, default, required):
        if len(path) == 0:
            result = dict(default)
            result.update(current_object)
            for key in required:
                if key not in result:
                    raise ConfigurationError('Missing configuration value for {}.{}.'.format(
                        current_path.join('.'), key))
            return result

        k = path[0]
        if k not in current_object:
            raise ConfigurationError('Missing configuration object for {}.{}.'.format(
                current_path.join('.'), k))

        current_path.append(k)

        if type(current_object[k]) != dict:
            raise ConfigurationError('The configuration {} is not an object.'.format(
                current_path.join('.')))

        return Config._get_object_path(current_path, current_object[k], path[1:], default, required)
