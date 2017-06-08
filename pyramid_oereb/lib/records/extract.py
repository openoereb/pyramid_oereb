# -*- coding: utf-8 -*-
import warnings
from datetime import datetime
import uuid


class ExtractRecord(object):
    # Attributes calculated or defined while processing
    creation_date = None
    electronic_signature = None
    concerned_theme = None
    not_concerned_theme = None
    theme_without_data = None
    is_reduced = False
    extract_identifier = None
    qr_code = None
    plr_cadastre_authority = None

    def __init__(self, real_estate, logo_plr_cadastre, federal_logo, cantonal_logo, municipality_logo,
                 plr_cadastre_authority, base_data, exclusions_of_liability=None, glossaries=None,
                 concerned_theme=None, not_concerned_theme=None, theme_without_data=None,
                 general_information=None):
        """
        The extract base class.

        Args:
            real_estate (pyramid_oereb.lib.records.real_estate.RealEstateRecord): The real estate in its
                record representation.
            logo_plr_cadastre (pyramid_oereb.lib.records.image.ImageRecord): Image file of the PLR logo.
            federal_logo (pyramid_oereb.lib.records.image.ImageRecord):Image file of the federal logo.
            cantonal_logo (pyramid_oereb.lib.records.image.ImageRecord): Image file of the cantonal logo.
            municipality_logo (pyramid_oereb.lib.records.image.ImageRecord): Image file of the municipality
                logo.
            plr_cadastre_authority (pyramid_oereb.lib.records.office.OfficeRecord): The authority which is
                responsible for the PLR cadastre.
            base_data (dict of str): A multilingual list of basic data layers used by the extract. For
                instance the base map from swisstopo.
            exclusions_of_liability (list of
                pyramid_oereb.lib.records.exclusion_of_liability.ExclusionOfLiabilityRecord): Exclusions of
                liability for the extract.
            glossaries (list of pyramid_oereb.lib.records.glossary.GlossaryRecord): Glossaries for the
                extract.
            concerned_theme (list of pyramid_oereb.lib.records.theme.ThemeRecord or None): Concerned themes.
            not_concerned_theme (list of pyramid_oereb.lib.records.theme.ThemeRecord or None): Not concerned
                themes.
            theme_without_data (list of pyramid_oereb.lib.records.theme.ThemeRecord or None): Themes without
                data.
            general_information (dict): General information for the static extract as multilingual text.
        """
        if not isinstance(base_data, dict):
            warnings.warn('Type of "base_data" should be "dict"')
        if general_information and not isinstance(general_information, dict):
            warnings.warn('Type of "general_information" should be "dict"')

        self.base_data = base_data
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
        self.creation_date = datetime.now().date()
        self.logo_plr_cadastre = logo_plr_cadastre
        self.federal_logo = federal_logo
        self.cantonal_logo = cantonal_logo
        self.municipality_logo = municipality_logo
        self.plr_cadastre_authority = plr_cadastre_authority
        if exclusions_of_liability:
            self.exclusions_of_liability = exclusions_of_liability
        else:
            self.exclusions_of_liability = []
        if glossaries:
            self.glossaries = glossaries
        else:
            self.glossaries = []
