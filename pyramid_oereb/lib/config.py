# -*- coding: utf-8 -*-
import os

import logging
import datetime
import yaml
from io import open as ioopen
from pyramid.config import ConfigurationError
from pyramid_oereb.lib.adapter import FileAdapter
from pyramid_oereb.lib.records.office import OfficeRecord
from pyramid_oereb.lib.records.image import ImageRecord
from pyramid_oereb.lib.records.theme import ThemeRecord

log = logging.getLogger(__name__)


class Config(object):
    """
    A central point where we can access to the application configuration.
    Init it with a config file (Config.init(configfile, configsection))
    Then use it anywhere with Config.get('my_config_variable').
    """

    _config = None

    @staticmethod
    def init(configfile, configsection, c2ctemplate_style=False):
        """
        Loads configuration from yaml file and provides methods for generating webservice output.

        Args:
            config_file (str): The configuration yaml file.
            config_section (str): The section within the yaml file.
        """
        assert Config._config is None

        Config._config = _parse(configfile, configsection, c2ctemplate_style)

    @staticmethod
    def get_config():
        """
        Returns the current configuration

        Returns:
            Dict: The current config or None.
        """
        return Config._config

    @staticmethod
    def update_settings(settings):
        settings.update(Config._config)

    @staticmethod
    def get_themes():
        """
        Returns a list of available themes.

        Returns:
            list of pyramid_oereb.lib.records.theme.ThemeRecord: The available themes.
        """
        assert Config._config is not None

        result = []
        plrs = Config._config.get('plrs')
        if plrs and isinstance(plrs, list):
            for position, theme in enumerate(plrs, start=1):
                result.append(ThemeRecord(
                    theme.get('code'),
                    theme.get('text'),
                    position
                ))
        return result

    @staticmethod
    def get_theme(code):
        """
        Returns the theme with the specified code.

        Args:
            code (str): The theme's code.

        Returns:
            pyramid_oereb.lib.records.theme.ThemeRecord or None: The theme with the specified
            code.
        """
        assert Config._config is not None

        plrs = Config._config.get('plrs')
        if plrs and isinstance(plrs, list):
            for position, theme in enumerate(plrs, start=1):
                if theme.get('code') == code:
                    return ThemeRecord(
                        theme.get('code'),
                        theme.get('text'),
                        position
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

    @staticmethod
    def get_all_federal():
        """
        Returns a list of all federal topic codes.

        :return: All federal topic codes.
        :rtype: list of str
        """
        assert Config._config is not None
        federal = []
        plrs = Config.get('plrs')
        if plrs and isinstance(plrs, list):
            for plr in plrs:
                if plr.get('federal'):
                    federal.append(plr.get('code'))
        return federal

    @staticmethod
    def get_crs():
        """
        Returns a unicode string of configured crs.

        Returns:
            unicode: The available crs.
        """
        assert Config._config is not None
        srid = Config._config.get('srid')
        return u'epsg:{}'.format(srid)

    @staticmethod
    def get_language():
        """
        Returns a list of available languages.

        Returns:
            list: The available languages.
        """
        assert Config._config is not None

        result = []
        language = Config._config.get('language')
        if language and isinstance(language, list):
            result.extend(language)
        return result

    @staticmethod
    def get_flavour():
        """
        Returns a list of available flavours.

        Returns:
            list: The available flavours.
        """
        assert Config._config is not None

        result = []
        flavour = Config._config.get('flavour')
        if flavour and isinstance(flavour, list):
            result.extend(flavour)
        return result

    @staticmethod
    def get_geometry_types():
        """
        Returns a list of available geometry_types.

        :return: The available geometry types.
        :rtype: list
        """
        assert Config._config is not None

        result = []
        geometry_types = Config._config.get('geometry_types')
        if geometry_types and isinstance(geometry_types, list):
            result.extend(geometry_types)
        return result

    @staticmethod
    def get_real_estate_config():
        """
        Returns a dictionary of the configured real estate settings.

        Returns:
            dict: The configured real estate settings.
        """
        assert Config._config is not None

        return Config._config.get('real_estate')

    @staticmethod
    def get_plan_for_land_register_main_page_config():
        assert Config._config is not None
        return Config._config.get('real_estate', {}).get('plan_for_land_register_main_page')

    @staticmethod
    def get_plan_for_land_register_config():
        assert Config._config is not None
        return Config._config.get('real_estate', {}).get('plan_for_land_register')

    @staticmethod
    def get_address_config():
        """
        Returns a dictionary of the configured address settings.

        Returns:
            dict: The configured address settings.
        """
        assert Config._config is not None

        return Config._config.get('address')

    @staticmethod
    def get_glossary_config():
        """
        Returns a dictionary of the configured glossary settings.

        Returns:
            dict: The configured glossary settings.
        """
        assert Config._config is not None

        return Config._config.get('glossary')

    @staticmethod
    def get_exclusion_of_liability_config():
        """
        Returns a dictionary of the configured exclusion_of_liability settings.

        Returns:
            dict: The configured exclusion_of_liability settings.
        """
        assert Config._config is not None

        return Config._config.get('exclusion_of_liability')

    @staticmethod
    def get_municipality_config():
        """
        Returns a dictionary of the configured municipality settings.

        Returns:
            dict: The configured municipality settings.
        """
        assert Config._config is not None

        return Config._config.get('municipality')

    @staticmethod
    def get_extract_config():
        """
        Returns a dictionary of the configured extract settings.

        Returns:
            dict: The configured extract settings.
        """
        assert Config._config is not None

        return Config._config.get('extract')

    @staticmethod
    def get_plr_cadastre_authority():
        """
        Returns an office record for the configured PLR cadastre authority.

        Returns:
            pyramid_oereb.lib.records.office.OfficeRecord: The configured PLR cadastre
            authority.
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

        Returns:
            dict: The configured paths to the logos wrapped in a dictionary.
        """
        assert Config._config is not None

        confederation_key = 'confederation'
        oereb_key = 'oereb'
        canton_key = 'canton'
        msg = 'The definition for "{key}" must be set. Got: {found_config}'
        logo_dict = Config._config.get('logo')
        if not logo_dict.get(confederation_key):
            raise ConfigurationError(msg.format(key=confederation_key, found_config=logo_dict))
        if not logo_dict.get(oereb_key):
            raise ConfigurationError(msg.format(key=oereb_key, found_config=logo_dict))
        if not logo_dict.get(canton_key):
            raise ConfigurationError(msg.format(key=canton_key, found_config=logo_dict))
        file_adapter = FileAdapter()
        confederation_logo = ImageRecord(file_adapter.read(logo_dict.get(confederation_key)))
        oereb_logo = ImageRecord(file_adapter.read(logo_dict.get(oereb_key)))
        canton_logo = ImageRecord(file_adapter.read(logo_dict.get(canton_key)))

        return {
            confederation_key: confederation_logo,
            oereb_key: oereb_logo,
            canton_key: canton_logo
        }

    @staticmethod
    def get_oereblex_config():
        """
        Returns a dictionary of the configured OEREBlex settings.

        Returns:
            dict: The configured OEREBlex settings.
        """
        assert Config._config is not None

        return Config._config.get('oereblex')

    @staticmethod
    def get_base_data(base_data_date):
        """
        Returns the multilingual base data description with updated currentness.

        Args:
            base_data_date datetime.datetime: The base data currentness.

        Returns:
            dict: The multilingual base data with updated currentness.
        """
        assert Config._config is not None
        assert isinstance(base_data_date, datetime.datetime)
        base_data = dict(Config.get_extract_config().get('base_data').get('text'))
        assert isinstance(base_data, dict)
        for k in base_data.keys():
            base_data.update({k: base_data.get(k).format(base_data_date.strftime('%d.%m.%Y'))})
        return base_data

    @staticmethod
    def get(key, default=None):
        """
        Returns the specified configuration value.

        Args:
            key (str): Configuration parameter name.
            default (*): Default value if the specified parameter is not defined. Defaults to
                None.

        Returns:
            *: The specified configuration or default value
        """
        assert Config._config is not None

        return Config._config.get(key, default)

    @staticmethod
    def get_object_path(path, default=None, required=None):
        """
        Returns the configuration object at a specified path.

        example:
        get_object_path('app.print', {'dpi': 300}, ['map_size'])

        Args:
            path (str): Dot separated path of the wonted object.
            default (dict): Default dictionary values of the object. Defaults to {}.
            required (list): The list of required sub values in the object. Defaults to [].

        Returns:
            *: The specified configuration object.
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
                        '.'.join(current_path), key))
            return result

        k = path[0]
        if k not in current_object:
            raise ConfigurationError('Missing configuration object for {}.{}.'.format(
                '.'.join(current_path), k))

        current_path.append(k)

        if type(current_object[k]) != dict:
            raise ConfigurationError('The configuration {} is not an object.'.format(
                '.'.join(current_path)))

        return Config._get_object_path(current_path, current_object[k], path[1:], default, required)

    @staticmethod
    def get_law_status(theme_code, law_status_config, law_status_code):
        """

        Args:
            theme_code (str): The theme code.
            law_status_config (dict): The configured mapping of the plrs law status.
            law_status_code (str): The law status code read from the data to wrap it into the only two allowed
                values: "inForce" or "runningModifications" which are possible on the extract.

        Returns:
            str: The mapped law status. This is "inForce" or "runningModifications".

        Raises:
            AttributeError: If the passed law status code does not match one of the configured ones.
        """
        if law_status_config.get('in_force') == law_status_code:
            return 'inForce'
        elif law_status_config.get('running_modifications') == law_status_code:
            return 'runningModifications'
        else:
            raise AttributeError(
                u'There was no proper configuration for the theme "{theme}" on the law '
                u'status it has to be configured depending on the data you imported. Law '
                u'status in your data was: {data_law_status}, the configured options are: '
                u'{in_force} and {running_modifications}'.format(
                    theme=theme_code,
                    data_law_status=law_status_code,
                    in_force=law_status_config.get('in_force'),
                    running_modifications=law_status_config.get('running_modifications')
                )
            )

    @staticmethod
    def get_law_status_translations(code):
        """
        Obtaining the law status translations from config via the code.

        Args:
            code (str): The law status code. This must be "inForce" or "runningModifications". Any other
                value won't match and throw a silent error.

        Returns:
            dict: The translation from the configuration.
        """
        translations = Config.get('law_status_translations')
        if code == 'inForce':
            return translations.get('in_force')
        elif code == 'runningModifications':
            return translations.get('running_modifications')
        else:
            log.error(u'No translation for law status found in config for the passed code: {code}'.format(
                code=code
            ))
            return {
                'de': u'Keine Übersetzung gefunden',
                'fr': u'Pas de traduction',
                'it': u'Nessuna traduzione trovato',
                'rm': u'Nagin translaziun chattà'
            }

    @staticmethod
    def get_layer_config(theme_code):
        """
        Obtaining the layer configuration of a theme from config.

        Args:
            theme_code (str): The theme code.

        Returns:
            list: Layer index (int) and layer opacity (float).
        """
        assert Config._config is not None
        themes = Config._config.get('plrs')
        if themes and isinstance(themes, list):
            for theme in themes:
                if theme.get('code') == theme_code:
                    view_service = theme.get('view_service')
                    if view_service and isinstance(view_service, dict):
                        layer_index = view_service.get('layer_index')
                        layer_opacity = view_service.get('layer_opacity')
                        if layer_opacity is None:
                            raise ConfigurationError(
                                'For {} the "layer_opacity" was not found!'.format(theme_code)
                            )
                        if layer_index is None:
                            raise ConfigurationError(
                                'For {} the "layer_index" was not found!'.format(theme_code)
                            )
                        return layer_index, layer_opacity
        return None, None

    @classmethod
    def get_real_estate_type_by_mapping(cls, real_estate_type):
        """
        Uses the configured mappings of the real estate type to translate it to the correct federal
        representation.

        Args:
            real_estate_type (unicode): The type which is used inside the data to distinguish the different
                kinds of real estates.

        Returns:
            unicode: The mapped type or the original one if no mapping fits.

        """
        real_estate_config = cls.get_real_estate_config()
        type_mapping = real_estate_config.get('type_mapping', [])
        for mapping in type_mapping:
            if mapping['type'] == real_estate_type:
                return mapping['mapping']
        return real_estate_type

    @staticmethod
    def get_sub_theme_sorter_config(theme_code):
        assert Config._config is not None
        sorter = {
            'module': 'pyramid_oereb.contrib.print_proxy.sub_themes.sorting',
            'class_name': 'BaseSort',
            'params': {}
        }
        themes = Config._config.get('plrs')
        if themes and isinstance(themes, list):
            for theme in themes:
                if theme.get('code') == theme_code:
                    sub_themes = theme.get('sub_themes', {})
                    if 'sorter' in sub_themes:
                        sorter = sub_themes.get('sorter')
                    break
        # Check if sorter is valid
        if 'module' not in sorter:
            log.error("Invalid configuration for sub theme sorter for theme {}, "
                      "no module property".format(theme_code))
        if 'class_name' not in sorter:
            log.error("Invalid configuration for sub theme sorter for theme {}, "
                      "no class_name property".format(theme_code))
        return sorter


def _parse(cfg_file, cfg_section, c2ctemplate_style=False):
    """
    Parses the defined YAML file and returns the defined section as dictionary.

    Args:
        cfg_file (str): The YAML file to be parsed.
        cfg_section (str): The section to be returned.

    Returns:
        dict: The parsed section as dictionary.
    """
    if cfg_file is None:
        raise ConfigurationError(
            'Missing configuration parameter "pyramid_oereb.cfg.file" or '
            '"pyramid_oereb.cfg.c2ctemplate.file".'
        )
    if cfg_section is None:
        raise ConfigurationError('Missing configuration parameter "pyramid_oereb.cfg.section".')

    try:
        if c2ctemplate_style:
            import c2c.template
            content = c2c.template.get_config(cfg_file)
        else:
            with ioopen(cfg_file, encoding='utf-8') as f:
                content = yaml.safe_load(f.read())
    except IOError as e:
        e.strerror = '{0}{1} \'{2}\', Current working directory is {3}'.format(
            e.strerror, e.args[1], e.filename, os.getcwd())
        raise
    cfg = content.get(cfg_section)
    if cfg is None:
        raise ConfigurationError('YAML file contains no section "{0}"'.format(cfg_section))
    return cfg
