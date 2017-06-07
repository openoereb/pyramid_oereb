# -*- coding: utf-8 -*-
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
    general_information = None
    plr_cadastre_authority = None

    def __init__(self, real_estate, logo_plr_cadastre, federal_logo, cantonal_logo, municipality_logo,
                 plr_cadastre_authority, base_data, exclusions_of_liability=None, glossaries=None,
                 concerned_theme=None, not_concerned_theme=None, theme_without_data=None):
        """
        The extract base class.

        Args:
            real_estate (pyramid_oereb.lib.records.real_estate.RealEstateRecord): The real
                estate in its record representation.
            logo_plr_cadastre (pyramid_oereb.lib.records.logo.LogoRecord): Image file of the PLR
                logo
            federal_logo (pyramid_oereb.lib.records.logo.LogoRecord):Image file of the federal
                logo
            cantonal_logo (pyramid_oereb.lib.records.logo.LogoRecord): Image file of the
                cantonal logo
            municipality_logo (pyramid_oereb.lib.records.logo.LogoRecord): Image file of the
                municipality logo
            plr_cadastre_authority (pyramid_oereb.lib.records.office.OfficeRecord): The
                authority which is responsible for the PLR cadastre
            base_data (list of dictofstr): A list of basic data layers used by the extract. For
                instance the basic map fromswisstopo
            exclusions_of_liability (): Exclusions of liability for the extract
            list of pyramid_oereb.lib.records.exclusion_of_liability.ExclusionOfLiabilityRecord

        Args:
            glossaries (list of pyramid_oereb.lib.records.glossary.GlossaryRecord): Glossary for
                the extract
            concerned_theme (list of pyramid_oereb.lib.records.theme.ThemeRecord or None): Concerned
                themes.
            not_concerned_theme (list of pyramid_oereb.lib.records.theme.ThemeRecord or None): Not
                concerned themes.
            theme_without_data (list of pyramid_oereb.lib.records.theme.ThemeRecord or None): Themes
                without data.
        """
        self.base_data = base_data
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

    @classmethod
    def get_fields(cls):
        """
        Returns a list of available field names.

        Returns:
            list of str: List of available field names.
        """
        return [
            'extract_identifier',
            'real_estate',
            'not_concerned_theme',
            'concerned_theme',
            'theme_without_data',
            'logo_plr_cadastre',
            'creation_date',
            'federal_logo',
            'cantonal_logo',
            'municipality_logo',
            'plr_cadastre_authority',
            'base_data'
            'exclusions_of_liability',
            'glossaries'
        ]

    def to_extract(self):
        """
        Returns a dictionary with all available values needed for the extract.

        Returns:
            dict: Dictionary with values for the extract.
        """
        extract = dict()
        for key in [
            'extract_identifier',
            'exclusions_of_liability',
            'glossaries'
        ]:
            value = getattr(self, key)
            if value:
                extract[key] = value
        key = 'real_estate'
        record = getattr(self, key)
        if record:
            extract[key] = record.to_extract()
        for key in [
            'not_concerned_theme',
            'concerned_theme',
            'theme_without_data'
        ]:
            themes = getattr(self, key)
            if isinstance(themes, list) and len(themes) > 0:
                extract[key] = [theme.to_extract() for theme in themes]
        key = 'creation_date'
        extract[key] = getattr(self, key).isoformat()
        for key in ['logo_plr_cadastre', 'federal_logo', 'cantonal_logo', 'municipality_logo']:
            extract[key] = getattr(self, key).to_extract()

        return extract
