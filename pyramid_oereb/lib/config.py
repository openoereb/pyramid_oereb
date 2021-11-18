# -*- coding: utf-8 -*-
import os

import logging
import yaml
from io import open as ioopen
from pyramid.config import ConfigurationError
from pyramid_oereb.lib.records.office import OfficeRecord
from pyramid_oereb.lib.records.document_types import DocumentTypeRecord
from pyramid_oereb.lib.records.law_status import LawStatusRecord
from pyramid_oereb.lib.records.real_estate_type import RealEstateTypeRecord
from pyramid_oereb.lib.readers.theme import ThemeReader
from pyramid_oereb.lib.readers.theme_document import ThemeDocumentReader
from pyramid_oereb.lib.records.logo import LogoRecord
from pyramid_oereb.lib.readers.logo import LogoReader
from pyramid_oereb.lib.readers.law_status import LawStatusReader
from pyramid_oereb.lib.readers.real_estate_type import RealEstateTypeReader
from pyramid_oereb.lib.readers.document_types import DocumentTypeReader
from pyramid_oereb.lib.readers.document import DocumentReader
from pyramid_oereb.lib.readers.office import OfficeReader
from pyramid_oereb.lib.readers.general_information import GeneralInformationReader
from pyramid_oereb.lib.readers.map_layering import MapLayeringReader
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
    logos = None
    document_types = None
    documents = None
    general_information = None
    law_status = None
    real_estate_types = None
    map_layering = None
    theme_document = None
    offices = None

    @staticmethod
    def init(configfile, configsection, c2ctemplate_style=False, resolve_doument_theme_relation=False):
        """
        Loads configuration from yaml file and provides methods for generating webservice output.

        Args:
            config_file (str): The configuration yaml file.
            config_section (str): The section within the yaml file.
        """
        assert Config._config is None

        Config._config = _parse(configfile, configsection, c2ctemplate_style)
        Config.init_law_status()
        Config.init_document_types()
        Config.init_offices()
        Config.init_themes()
        Config.init_theme_document()
        Config.init_documents()
        Config.init_general_information()
        Config.init_real_estate_types()
        Config.init_map_layering()
        Config.init_logos()

        if resolve_doument_theme_relation:
            Config.assemble_relation_themes_documents()

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
    def init_theme_document():
        try:
            Config.theme_document = Config._read_theme_document()
        except ProgrammingError:
            Config.theme_document = None

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
    def init_documents():
        try:
            Config.documents = Config._read_documents()
        except ProgrammingError:
            Config.documents = None

    @staticmethod
    def init_offices():
        try:
            Config.offices = Config._read_offices()
        except ProgrammingError:
            Config.offices = None

    @staticmethod
    def assemble_relation_themes_documents():
        for theme in Config.themes:
            theme_documents = []
            for theme_document in Config.theme_document:
                if theme_document.theme_id == theme.identifier:
                    for document in Config.documents:
                        if theme_document.document_id == document.identifier:
                            document_copy = document.copy()
                            document_copy.article_numbers = theme_document.article_numbers
                            theme_documents.append(document_copy)
            if len(theme_documents) > 0:
                theme.document_records = theme_documents

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
    def _read_theme_document():
        theme_document_config = Config.get_theme_document_config()
        if theme_document_config is None:
            raise ConfigurationError("Missing configuration for theme document")
        theme_document_reader = ThemeDocumentReader(
            theme_document_config.get('source').get('class'),
            **Config.get_theme_document_config().get('source').get('params')
        )
        return theme_document_reader.read()

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
    def _read_documents():
        document_config = Config.get_document_config()
        if document_config is None:
            raise ConfigurationError("Missing configuration for document source config")
        document_reader = DocumentReader(
            document_config.get('source').get('class'),
            **document_config.get('source').get('params')
        )
        return document_reader.read(Config.offices)

    @staticmethod
    def _read_offices():
        office_config = Config.get_office_config()
        if office_config is None:
            raise ConfigurationError("Missing configuration for office source config")
        office_reader = OfficeReader(
            office_config.get('source').get('class'),
            **office_config.get('source').get('params')
        )
        return office_reader.read()

    @staticmethod
    def get_general_information():
        """
        Returns the general information.

        Returns:
            list of pyramid_oereb.lib.records.theme.GeneralInformationRecord: The available general
            information entries.
        """
        assert Config._config is not None
        return Config.general_information

    @staticmethod
    def get_law_status_codes():
        """
        Returns a list of available law status codes.

        Returns:
            list of unicode: The available law status codes.
        """
        assert Config._config is not None
        return [law_status.code for law_status in Config.law_status]

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
    def get_theme_by_code_sub_code(code, sub_code=None):
        """
        Returns the theme or sub-theme which matches the code.

        Args:
            code (str): The theme's code or sub-code.

        Returns:
            pyramid_oereb.lib.records.theme.ThemeRecord or None: The theme with the specified
            code.
        """
        if Config.themes is None:
            raise ConfigurationError("Themes have not been initialized")
        theme_result = [theme for theme in Config.themes if theme.sub_code == sub_code and theme.code == code]
        if len(theme_result) > 0:
            return theme_result[0]
        else:
            raise ConfigurationError(
                f"Theme {code} with sub-code {sub_code} not found in the application configuration"
            )

    @staticmethod
    def init_logos():
        try:
            Config.logos = Config._read_logos()
        # When initializing the database (create_tables), the table 'logo' does not exist yet
        except ProgrammingError:
            Config.logos = None

    @staticmethod
    def _read_logos():
        logo_config = Config.get_logo_config()
        if logo_config is None:
            raise ConfigurationError("Missing configuration for logos")
        logo_reader = LogoReader(
            logo_config.get('source').get('class'),
            **Config.get_logo_config().get('source').get('params')
        )
        return logo_reader.read()

    @staticmethod
    def get_logos():
        """
        Returns all the logos and municipalities arms of coats.

        Returns:
            list of pyramid_oereb.lib.records.logo.LogoRecord: All the logo entries needed to
            generate an plr data-extract (plr-logo, confederation, canton, municipality).
        """
        assert Config._config is not None
        if len(Config.logos) < 1:
            raise ConfigurationError("At least one entry for the plr-logo is required")
        return Config.logos

    @staticmethod
    def get_logo_by_code(code):
        """
        Returns the image for a logo called by its code.
        Args:
            code (str): The identifier for the logo.
        Returns:
            pyramid_oereb.lib.records.logo.LogoRecord or None: The logo image
            for the specified code.
        """
        if Config.logos is None:
            raise ConfigurationError("The logo images have not been initialized")
        for logo in Config.logos:
            if isinstance(logo, LogoRecord):
                if logo.code == code:
                    return logo
            else:
                raise ConfigurationError("The logo has not the expected format")
        raise ConfigurationError(f"Logo for code: {code} not found in the application configuration")

    @staticmethod
    def get_conferderation_logo():
        return Config.get_logo_by_code(Config.get_logo_lookup_confederation())

    @staticmethod
    def get_canton_logo():
        return Config.get_logo_by_code(Config.get_logo_lookup_canton())

    @staticmethod
    def get_municipality_logo(fosnr):
        return Config.get_logo_by_code('{}.{}'.format(
            Config.get_logo_lookup_confederation(),
            str(fosnr))
        )

    @staticmethod
    def get_oereb_logo():
        return Config.get_logo_by_code(Config.get_logo_lookup_oereb())

    @staticmethod
    def get_logo_lookups():
        logo_lookups = Config.get('logo_lookups')
        if logo_lookups:
            return logo_lookups
        else:
            raise ConfigurationError('Configuration for "logo_lookups" not found.')

    @staticmethod
    def get_logo_lookup(key):
        code = Config.get_logo_lookups()[key]
        if code:
            return code
        else:
            raise ConfigurationError('Configuration for lookup "{}" not found.'.format(key))

    @staticmethod
    def get_logo_lookup_oereb():
        return Config.get_logo_lookup('oereb')

    @staticmethod
    def get_logo_lookup_canton():
        return Config.get_logo_lookup('canton')

    @staticmethod
    def get_logo_lookup_confederation():
        return Config.get_logo_lookup('confederation')

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
    def init_real_estate_types():
        try:
            Config.real_estate_types = Config._read_real_estate_types()
        # When initializing the database (create_tables), the table 'real_estate_type' does not exist yet
        except ProgrammingError:
            Config.real_estate_types = None

    @staticmethod
    def _read_real_estate_types():
        real_estate_types_config = Config.get('real_estate_type')
        if real_estate_types_config is None:
            raise ConfigurationError("Missing configuration for real estate type source config")
        real_estate_type_reader = RealEstateTypeReader(
            real_estate_types_config.get('source').get('class'),
            **real_estate_types_config.get('source').get('params'))

        return real_estate_type_reader.read()

    @staticmethod
    def get_real_estate_types():
        """
        Returns a list of available real_estate_types.

        Returns:
            list of pyramid_oereb.lib.records.real_estate_type.RealEstateTypeRecord: The available
            real estate types.
        """
        assert Config._config is not None
        return Config.real_estate_types

    @staticmethod
    def init_map_layering():
        try:
            Config.map_layering = Config._read_map_layering()
        # When initializing the database (create_tables), the table 'map_layering' does not exist yet
        except ProgrammingError:
            Config.map_layering = None

    @staticmethod
    def _read_map_layering():
        map_layering_config = Config.get('map_layering')
        if map_layering_config is None:
            raise ConfigurationError("Missing configuration for map layering source config")
        map_layering_reader = MapLayeringReader(
            map_layering_config.get('source').get('class'),
            **map_layering_config.get('source').get('params'))

        return map_layering_reader.read()

    @staticmethod
    def get_map_layering():
        """
        Returns a list of available map layerings.

        Returns:
            list of pyramid_oereb.lib.records.map_layering.MapLayeringRecord: The available
            map layering.
        """
        assert Config._config is not None
        return Config.map_layering

    @staticmethod
    def get_index_and_opacity_of_view_service(reference_wms):
        """
        Returns the index and the opacity of the view service.

        Args:
            reference_wms (dict): reference_wms.

        Returns:
            pyramid_oereb.standard.models.main.MapLayering.layer_index or 1 (default value),
            pyramid_oereb.standard.models.main.MapLayering.layer_opacity or 0.75 (default value)
        """
        default_index = 1
        default_opacity = 0.75
        if Config.map_layering is None:
            raise ConfigurationError("Map layering has not been initialized")
        if len(Config.map_layering) == 0:
            return default_index, default_opacity
        for map_layering_result in Config.map_layering:
            for lang1 in list(reference_wms.keys()):
                for lang2 in list(map_layering_result.keys()):
                    if reference_wms[lang1] == map_layering_result[lang2]:
                        return map_layering_result.layer_index, map_layering_result.layer_opacity
        return default_index, default_opacity

    @staticmethod
    def get_document_types_lookups(theme_code):
        lookups = Config.get_theme_config_by_code(theme_code).get('document_types_lookup')
        if lookups is None:
            raise ConfigurationError(
                '"document_types_lookup" must be defined in configuration for theme {}!'.format(theme_code)
            )
        return lookups

    @staticmethod
    def get_document_type_lookup_by_theme_code_key_code(theme_code, key, code):
        lookups = Config.get_document_types_lookups(theme_code)
        for lookup in lookups:
            if lookup[key] == code:
                return lookup
        raise ConfigurationError(
            'Document type lookup with key "{}" and code "{}" is not '
            'defined in configuration!'.format(key, code)
        )

    @staticmethod
    def get_document_type_lookup_by_data_code(theme_code, data_code):
        return Config.get_document_type_lookup_by_theme_code_key_code(
            theme_code,
            'data_code',
            data_code
        )

    @staticmethod
    def get_document_type_by_data_code(theme_code, data_code):
        lookup = Config.get_document_type_lookup_by_data_code(theme_code, data_code)
        record = Config.get_document_type_by_code(data_code)
        log.debug(
            'Translating code {} => code {} of {}'.format(
                lookup['data_code'], lookup['extract_code'], record.title
            )
        )
        translated_record = DocumentTypeRecord(lookup['extract_code'], record.title)
        return translated_record

    @staticmethod
    def get_main_document_types_lookups():
        lookups = Config._config.get('app_schema').get('document_types_lookup')
        if lookups is None:
            raise ConfigurationError(
                '"document_types_lookup" must be defined in "app_schema"!'
            )
        return lookups

    @staticmethod
    def get_main_document_type_lookup_by_key_code(key, code):
        lookups = Config.get_main_document_types_lookups()
        for lookup in lookups:
            if lookup[key] == code:
                return lookup
        raise ConfigurationError(
            'Document type lookup with key "{}" and code "{}" is not '
            'defined in configuration!'.format(key, code)
        )

    @staticmethod
    def get_main_document_type_lookup_by_data_code(data_code):
        return Config.get_main_document_type_lookup_by_key_code(
            'data_code',
            data_code
        )

    @staticmethod
    def get_main_document_type_by_data_code(data_code):
        lookup = Config.get_main_document_type_lookup_by_data_code(data_code)
        record = Config.get_document_type_by_code(data_code)
        log.debug(
            'Translating code {} => code {} of {}'.format(
                lookup['data_code'], lookup['extract_code'], record.title
            )
        )
        translated_record = DocumentTypeRecord(lookup['extract_code'], record.title)
        return translated_record

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

        for document_type in Config.document_types:
            if document_type.code == code:
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
    def get_real_estate_type_config():
        """
        Returns a dictionary of the configured real estate settings.

        Returns:
            dict: The configured real estate settings.
        """
        assert Config._config is not None

        return Config._config.get('real_estate_type')

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
    def get_theme_document_config():
        """
        Returns a dictionary of the configured theme document settings.

        Returns:
            dict: The configured theme document settings.
        """
        assert Config._config is not None

        return Config._config.get('theme_document')

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
    def get_disclaimer_config():
        """
        Returns a dictionary of the configured disclaimer settings.

        Returns:
            dict: The configured disclaimer settings.
        """
        assert Config._config is not None

        return Config._config.get('disclaimer')

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
    def get_logo_config():
        """
        Returns a dictionary of the configured file path's to the logos.

        Returns:
            dict: The configured paths to the logos wrapped in a dictionary.
        """
        assert Config._config is not None

        return Config._config.get('logos')

    def get_law_status_config():
        """
        Returns a dictionary of the configured law status sources.

        Returns:
            dict: The configured general law status sources.
        """
        assert Config._config is not None

        return Config._config.get('law_status_labels')

    @staticmethod
    def get_document_config():
        """
        Returns a dictionary of the configured document sources.

        Returns:
            dict: The configured documents sources.
        """
        assert Config._config is not None

        return Config._config.get('documents')

    @staticmethod
    def get_office_config():
        """
        Returns a dictionary of the configured office sources.

        Returns:
            dict: The configured office sources.
        """
        assert Config._config is not None

        return Config._config.get('offices')

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
    def get_oereblex_config():
        """
        Returns a dictionary of the configured OEREBlex settings.

        Returns:
            dict: The configured OEREBlex settings.
        """
        assert Config._config is not None

        return Config._config.get('oereblex')

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
    def get_law_status_lookups(theme_code):
        lookups = Config.get_theme_config_by_code(theme_code).get('law_status_lookup')
        if lookups is None:
            raise ConfigurationError(
                '"document_types_lookup" must be defined in configuration for theme {}!'.format(theme_code)
            )
        return lookups

    @staticmethod
    def get_law_status_lookup_by_theme_code_key_code(theme_code, key, code):
        lookups = Config.get_law_status_lookups(theme_code)
        for lookup in lookups:
            if lookup[key] == code:
                return lookup
        raise ConfigurationError(
            'Document type lookup with key "{}" and code "{}" is not'
            'defined in configuration!'.format(key, code)
        )

    @staticmethod
    def get_law_status_lookup_by_data_code(theme_code, data_code):
        return Config.get_law_status_lookup_by_theme_code_key_code(
            theme_code,
            'data_code',
            data_code
        )

    @staticmethod
    def get_law_status_by_data_code(theme_code, data_code):
        lookup = Config.get_law_status_lookup_by_data_code(theme_code, data_code)
        record = Config.get_law_status_by_code(data_code)
        log.debug(
            'Translating code {} => code {} of {}'.format(
                lookup['data_code'], lookup['extract_code'], record.title
            )
        )
        translated_record = LawStatusRecord(lookup['extract_code'], record.title)
        return translated_record

    @staticmethod
    def get_main_law_status_lookups():
        lookups = Config._config.get('app_schema').get('law_status_lookup')
        if lookups is None:
            raise ConfigurationError(
                '"law_status_lookup" must be defined in "app_schema"!'
            )
        return lookups

    @staticmethod
    def get_main_law_status_lookup_by_key_code(key, code):
        lookups = Config.get_main_law_status_lookups()
        for lookup in lookups:
            if lookup[key] == code:
                return lookup
        raise ConfigurationError(
            'Document type lookup with key "{}" and code "{}" is not'
            'defined in configuration!'.format(key, code)
        )

    @staticmethod
    def get_main_law_status_lookup_by_data_code(data_code):
        return Config.get_main_law_status_lookup_by_key_code(
            'data_code',
            data_code
        )

    @staticmethod
    def get_main_law_status_by_data_code(data_code):
        lookup = Config.get_main_law_status_lookup_by_data_code(data_code)
        record = Config.get_law_status_by_code(data_code)
        log.debug(
            'Translating code {} => code {} of {}'.format(
                lookup['data_code'], lookup['extract_code'], record.title
            )
        )
        translated_record = LawStatusRecord(lookup['extract_code'], record.title)
        return translated_record

    @staticmethod
    def get_law_status_by_code(law_status_code):
        """
         Returns a dictionary of the configured law status settings.

        Args:
            law_status_code (str): The law status code.

        Returns:
            pyramid_oereb.lib.records.law_status.LawStatusRecord: The found record.
        """
        if Config.law_status is None:
            raise ConfigurationError("The law status have not been initialized")

        for record in Config.law_status:
            if record.code == law_status_code:
                return record
        raise ConfigurationError(f"Law status {law_status_code} not found in the application configuration")

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

    @staticmethod
    def get_real_estate_type_lookups():
        lookups = Config.get_real_estate_type_config().get('lookup')
        if lookups is None:
            raise ConfigurationError(
                '"lookup" must be defined in configuration for theme real_estate_type!'
            )
        return lookups

    @staticmethod
    def get_real_estate_type_lookup_by_key_code(key, code):
        lookups = Config.get_real_estate_type_lookups()
        for lookup in lookups:
            if lookup[key] == code:
                return lookup
        raise ConfigurationError(
            'Document type lookup with key "{}" and code "{}" is not '
            'defined in configuration!'.format(key, code)
        )

    @staticmethod
    def get_real_estate_type_lookup_by_data_code(data_code):
        return Config.get_real_estate_type_lookup_by_key_code('data_code', data_code)

    @staticmethod
    def get_real_estate_type_by_data_code(data_code):
        lookup = Config.get_real_estate_type_lookup_by_data_code(data_code)
        record = Config.get_real_estate_type_by_code(data_code)
        log.debug(
            'Translating code {} => code {} of {}'.format(
                data_code, lookup['extract_code'], record.title
            )
        )
        translated_record = RealEstateTypeRecord(lookup['extract_code'], record.title)
        return translated_record

    @staticmethod
    def get_real_estate_type_by_code(code):
        """
         Returns a dictionary of the configured law status settings.

        Args:
            code (str): The real estate type code.

        Returns:
            pyramid_oereb.lib.records.real_estate_type.RealEstateTypeRecord: The found record.
        """
        if Config.real_estate_types is None:
            raise ConfigurationError("The real estate types have not been initialized")

        for record in Config.real_estate_types:
            if record.code == code:
                return record
        raise ConfigurationError(f"Real estate type with {code} not found in the application configuration")

    @staticmethod
    def extract_module_function(dotted_function_path):
        elements = dotted_function_path.split('.')
        function_name = elements[-1]
        module_path = '.'.join(elements[:-1])
        return {
            'module_path': module_path,
            'function_name': function_name
        }


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
