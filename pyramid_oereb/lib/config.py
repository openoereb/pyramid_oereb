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
from pyramid_oereb.lib.readers.theme import ThemeReader
from pyramid_oereb.lib.readers.law_status import LawStatusReader
from pyramid_oereb.lib.readers.document_types import DocumentTypeReader
from pyramid_oereb.lib.readers.general_information import GeneralInformationReader
from sqlalchemy.exc import ProgrammingError

log = logging.getLogger(__name__)


class Config(object):
    """
    A central point where we can access to the application configuration.
    Init it with a config file (Config.init(configfile, configsection))
    Then use it anywhere with Config.get('my_config_variable').
    """

    _config = None
    themes = None
    document_types = None
    general_information = None
    law_status = None

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
        Config.init_themes()
        Config.init_document_types()
        Config.init_general_information()
        Config.init_law_status()

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
    def init_themes():
        try:
            Config.themes = Config._read_themes()
        # When initializing the database (create_tables), the table 'theme' does not exist yet
        except ProgrammingError:
            Config.themes = None

    @staticmethod
    def init_general_information():
        try:
            Config.general_information = Config._read_general_information()
        except ProgrammingError:
            Config.general_information = None

    @staticmethod
    def init_law_status():
        try:
            Config.law_status = Config._read_law_status()
        except ProgrammingError:
            Config.law_status = None

    @staticmethod
    def _read_themes():
        theme_config = Config.get_theme_config()
        if theme_config is None:
            raise ConfigurationError("Missing configuration for themes")
        theme_reader = ThemeReader(
            theme_config.get('source').get('class'),
            **Config.get_theme_config().get('source').get('params')
        )
        return theme_reader.read()

    @staticmethod
    def _read_general_information():
        info_config = Config.get_info_config()
        if info_config is None:
            raise ConfigurationError("Missing configuration for general information")
        info_reader = GeneralInformationReader(
            info_config.get('source').get('class'),
            **Config.get_info_config().get('source').get('params')
        )
        return info_reader.read()

    @staticmethod
    def _read_law_status():
        law_status_config = Config.get_law_status_config()
        if law_status_config is None:
            raise ConfigurationError("Missing configuration for law status source config")
        law_status_reader = LawStatusReader(
            law_status_config.get('source').get('class'),
            **law_status_config.get('source').get('params')
        )
        return law_status_reader.read()

    @staticmethod
    def get_general_information():
        """
        Returns the general information.

        Returns:
            list of pyramid_oereb.lib.records.theme.GeneralInformationRecord: The available general
            information entries.
        """
        assert Config._config is not None
        if len(Config.general_information) < 1:
            raise ConfigurationError("At least one general information entry is required")
        return Config.general_information

    @staticmethod
    def get_themes():
        """
        Returns a list of available themes.

        Returns:
            list of pyramid_oereb.lib.records.theme.ThemeRecord: The available themes.
        """
        assert Config._config is not None
        return Config.themes

    @staticmethod
    def get_theme_by_code(code):
        """
        Returns the theme with the specified code.

        Args:
            code (str): The theme's code.

        Returns:
            pyramid_oereb.lib.records.theme.ThemeRecord or None: The theme with the specified
            code.
        """
        if Config.themes is None:
            raise ConfigurationError("Themes have not been initialized")
        for theme in Config.themes:
            if theme.code == code:
                return theme
        raise ConfigurationError(f"Theme {code} not found in the application configuration")

    @staticmethod
    def init_document_types():
        try:
            Config.document_types = Config._read_document_types()
        # When initializing the database (create_tables), the table 'document_types' does not exist yet
        except ProgrammingError:
            Config.document_types = None

    @staticmethod
    def _read_document_types():
        document_types_config = Config.get_document_types_config()
        if document_types_config is None:
            raise ConfigurationError("Missing configuration for document types")
        document_types_reader = DocumentTypeReader(
            document_types_config.get('source').get('class'),
            **Config.get_document_types_config().get('source').get('params')
        )
        return document_types_reader.read()

    @staticmethod
    def get_document_types():
        """
        Returns a list of available document_types.

        Returns:
            list of pyramid_oereb.lib.records.document_types.DocumentTypeRecord: The available
            document types.
        """
        assert Config._config is not None
        return Config.document_types

    @staticmethod
    def get_document_type_by_code(code):
        """
        Returns the label for the document type by code.
        Args:
            code (str): The document type code.
        Returns:
            pyramid_oereb.lib.records.document_types.DocumentTypeRecord or None: The document
            type for the specified code.
        """
        if Config.document_types is None:
            raise ConfigurationError("The document types have not been initialized")
        document_type_lookup = Config.get('document_types_lookup')[code]

        for document_type in Config.document_types:
            if document_type.code == document_type_lookup:
                return document_type
        raise ConfigurationError(f"Document type {code} not found in the application configuration")

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
    def get_theme_config():
        """
        Returns a dictionary of the configured theme settings.

        Returns:
            dict: The configured theme settings.
        """
        assert Config._config is not None

        return Config._config.get('theme')

    @staticmethod
    def get_document_types_config():
        """
        Returns a dictionary of the configured document type values settings.

        Returns:
            dict: The configured document types settings.
        """
        assert Config._config is not None

        return Config._config.get('document_types')

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
    def get_info_config():
        """
        Returns a dictionary of the configured general settings.

        Returns:
            dict: The configured general information settings.
        """
        assert Config._config is not None

        return Config._config.get('general_information')

    @staticmethod
    def get_law_status_config():
        """
        Returns a dictionary of the configured law status sources.

        Returns:
            dict: The configured general law status sources.
        """
        assert Config._config is not None

        return Config._config.get('law_status_labels')

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
    def get_logo_config(language=None):
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
        canton_logo = ImageRecord(file_adapter.read(logo_dict.get(canton_key)))

        if isinstance(logo_dict.get(oereb_key), dict):
            if language is None or language not in logo_dict.get(oereb_key):
                logo_language = Config.get('default_language')
            else:
                logo_language = language
            oereb_logo = ImageRecord(file_adapter.read(logo_dict.get(oereb_key).get(logo_language)))
        else:
            oereb_logo = ImageRecord(file_adapter.read(logo_dict.get(oereb_key)))

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
    def get_law_status_by_code(theme_code, law_status_code):
        """
         Returns a dictionary of the configured law status settings.

        Args:
            theme_code (str): The theme code to look up the configured law status code.
            law_status_code (str): The law status code. This must be "inKraft" or "AenderungMitVorwirkung"
            or "AenderungOhneVorwirkung". Any other value won't match and throws a silent error.

        Returns:
            dict: The translation from the configuration.
        """

        theme_law_status = Config.get_theme_config_by_code(theme_code).get('law_status')
        for record in Config.law_status:
            law_status_code_from_config = theme_law_status.get(record.code)
            if law_status_code == law_status_code_from_config:
                return record

        raise AttributeError(
            u'There was no proper configuration for the theme "{theme}" on the law '
            u'status it has to be configured depending on the data you imported. Law '
            u'status in your data was: {data_law_status}, the configured options are: '
            u'{in_kraft}, {aenderung_mit_vorwirkung} or {aenderung_ohne_vorwirkung}'.format(
                theme=theme_code,
                data_law_status=law_status_code,
                in_kraft="inKraft",
                aenderung_mit_vorwirkung='AenderungMitVorwirkung',
                aenderung_ohne_vorwirkung='AenderungOhneVorwirkung'
            )
        )

    @staticmethod
    def get_law_status_by_law_status_code(law_status_code):
        """
         Returns a dictionary of the configured law status settings.

        Args:
            law_status_code (str): The law status code. It must be "inKraft" or
            "AenderungMitVorwirkung" or "AenderungOhneVorwirkung". Any other value won't match
            and throws a silent error.

        Returns:
            dict: The translation from the configuration.
        """
        for status in Config.law_status:
            if status.code == law_status_code:
                return status

    @staticmethod
    def get_theme_config_by_code(theme_code):
        """
        Obtaining the theme configuration from config.

        Args:
            theme_code (str): The theme code.

        Returns:
            dict: theme settings from config.
        """
        assert Config._config is not None
        themes = Config._config.get('plrs')
        if themes and isinstance(themes, list):
            for theme in themes:
                if theme.get('code') == theme_code:
                    return theme
        return None

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
