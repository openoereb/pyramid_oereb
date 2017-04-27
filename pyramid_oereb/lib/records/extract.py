# -*- coding: utf-8 -*-
from datetime import datetime
import uuid


class ExtractRecord(object):
    # Attributes calculated or defined while processing
    creation_date = None
    electronic_signature = None
    concerned_theme = None
    notconcerned_theme = None
    theme_without_data = None
    is_reduced = False
    extract_identifier = None
    qr_code = None
    general_information = None
    base_data = None
    plr_cadastre_authority = None

    def __init__(self, real_estate, logo_plr_cadastre, federal_logo, cantonal_logo, municipality_logo,
                 plr_cadastre_authority, exclusions_of_liability=None, glossaries=None,
                 notconcerned_theme=None):
        """
        The extract base class.
        :param real_estate: The real estate in its record representation.
        :type real_estate: pyramid_oereb.lib.records.real_estate.RealEstateRecord
        :param logo_plr_cadastre: Image file of the PLR logo
        :type logo_plr_cadastre: pyramid_oereb.lib.records.logo.LogoRecord
        :param federal_logo:Image file of the federal logo
        :type federal_logo: pyramid_oereb.lib.records.logo.LogoRecord
        :param cantonal_logo: Image file of the cantonal logo
        :type cantonal_logo: pyramid_oereb.lib.records.logo.LogoRecord
        :param municipality_logo: Image file of the municipality logo
        :type municipality_logo: pyramid_oereb.lib.records.logo.LogoRecord
        :param plr_cadastre_authority: The authority which is responsible for the PLR cadastre
        :type plr_cadastre_authority: pyramid_oereb.lib.records.office.OfficeRecord
        :param exclusions_of_liability: Exclusions of liability for the extract
        :param glossaries: Glossary for the extract
        """
        self.extract_identifier = str(uuid.uuid4())
        self.real_estate = real_estate
        if notconcerned_theme:
            self.notconcerned_theme = notconcerned_theme
        else:
            self.notconcerned_theme = []
        self.concerned_theme = []
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
        :return: List of available field names.
        :rtype: list of str
        """
        return [
            'extract_identifier',
            'real_estate',
            'notconcerned_theme',
            'concerned_theme',
            'theme_without_data',
            'logo_plr_cadastre',
            'creation_date',
            'federal_logo',
            'cantonal_logo',
            'municipality_logo',
            'plr_cadastre_authority',
            'exclusions_of_liability',
            'glossaries'
        ]

    def to_extract(self):
        """
        Returns a dictionary with all available values needed for the extract.
        :return: Dictionary with values for the extract.
        :rtype: dict
        """
        extract = dict()
        for key in [
            'extract_identifier',
            'notconcerned_theme',
            'concerned_theme',
            'theme_without_data',
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
        key = 'creation_date'
        extract[key] = getattr(self, key).isoformat()
        for key in ['logo_plr_cadastre', 'federal_logo', 'cantonal_logo', 'municipality_logo']:
            extract[key] = getattr(self, key).to_extract()

        return extract
