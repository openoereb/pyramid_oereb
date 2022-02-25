# -*- coding: utf-8 -*-
import warnings
from datetime import datetime
import uuid


class ExtractRecord(object):
    """
    The extract base class.
    Attributes:
        creation_date (datetime.datetime): The date and time of the extract creation.
        electronic_signature (unicode or None): Digital signature for the extract.
        concerned_theme (list of pyramid_oereb.core.records.theme.ThemeRecord): List of concerned themes.
        not_concerned_theme (list of pyramid_oereb.core.records.theme.ThemeRecord): List of not concerned
            themes.
        theme_without_data (list of pyramid_oereb.core.records.theme.ThemeRecord): List of themes without
            data.
        extract_identifier (unicode): The extract identifier (UUID).
        qr_code (binary or None): QR code for the extract as binary string.
        update_date_os (datetime): Last update of the official survey used as base map in the extract.
        general_information (list of dict): General information for the static extract as multilingual
            text.
        real_estate (pyramid_oereb.lib.records.real_estate.RealEstateRecord): The real estate in its
            record representation.
        logo_plr_cadastre (pyramid_oereb.lib.records.logo.LogoRecord): Image file of the PLR logo.
        federal_logo (pyramid_oereb.lib.records.image.ImageRecord):Image file of the federal logo.
        cantonal_logo (pyramid_oereb.lib.records.image.ImageRecord): Image file of the cantonal logo.
        municipality_logo (pyramid_oereb.lib.records.image.ImageRecord): Image file of the municipality
            logo.
        plr_cadastre_authority (pyramid_oereb.lib.records.office.OfficeRecord): The authority which is
            responsible for the PLR cadastre.
        disclaimer (list of
            pyramid_oereb.core.records.disclaimer.DisclaimerRecord or None): Disclaimers for the extract.
        glossaries (list of pyramid_oereb.lib.records.glossary.GlossaryRecord): Glossaries for the
            extract.
    """

    creation_date = None
    electronic_signature = None
    concerned_theme = None
    not_concerned_theme = None
    theme_without_data = None
    extract_identifier = None
    qr_code = None

    def __init__(self, real_estate, logo_plr_cadastre, federal_logo, cantonal_logo, municipality_logo,
                 plr_cadastre_authority, update_date_os, disclaimers=None, glossaries=None,
                 concerned_theme=None, not_concerned_theme=None, theme_without_data=None,
                 general_information=None):
        """
        Args:
            real_estate (pyramid_oereb.lib.records.real_estate.RealEstateRecord): The real estate in its
                record representation.
            logo_plr_cadastre (pyramid_oereb.lib.records.logo.LogoRecord): Image file of the PLR logo.
            federal_logo (pyramid_oereb.lib.records.image.ImageRecord):Image file of the federal logo.
            cantonal_logo (pyramid_oereb.lib.records.image.ImageRecord): Image file of the cantonal logo.
            municipality_logo (pyramid_oereb.lib.records.image.ImageRecord): Image file of the municipality
                logo.
            plr_cadastre_authority (pyramid_oereb.lib.records.office.OfficeRecord): The authority which is
                responsible for the PLR cadastre.
            update_date_os (datetime): Last update of the official survey used as base map in the extract.
            disclaimer (list of
                pyramid_oereb.core.records.disclaimer.DisclaimerRecord or None): Disclaimers for the extract.
            glossaries (list of pyramid_oereb.lib.records.glossary.GlossaryRecord): Glossaries for the
                extract.
            concerned_theme (list of pyramid_oereb.lib.records.theme.ThemeRecord or None): Concerned themes.
            not_concerned_theme (list of pyramid_oereb.lib.records.theme.ThemeRecord or None): Not concerned
                themes.
            theme_without_data (list of pyramid_oereb.lib.records.theme.ThemeRecord or None): Themes without
                data.
            general_information (list of dict): General information for the static extract as multilingual
                text.
        """
        if not isinstance(update_date_os, datetime):
            warnings.warn('Type of "update_date_os" should be "datetime.datetime"')
        if general_information and not isinstance(general_information, list):
            warnings.warn('Type of "general_information" should be "list"')

        self.update_date_os = update_date_os
        self.general_information = general_information
        self.extract_identifier = str(uuid.uuid4())
        self.real_estate = real_estate
        if concerned_theme:
            self.concerned_theme = concerned_theme
        else:
            self.concerned_theme = []
        if not_concerned_theme:
            self.not_concerned_theme = not_concerned_theme
        else:
            self.not_concerned_theme = []
        if theme_without_data:
            self.theme_without_data = theme_without_data
        else:
            self.theme_without_data = []
        self.creation_date = datetime.now()
        self.logo_plr_cadastre = logo_plr_cadastre
        self.federal_logo = federal_logo
        self.cantonal_logo = cantonal_logo
        self.municipality_logo = municipality_logo
        self.plr_cadastre_authority = plr_cadastre_authority
        if disclaimers:
            self.disclaimers = disclaimers
        else:
            self.disclaimers = []
        if glossaries:
            self.glossaries = glossaries
        else:
            self.glossaries = []
