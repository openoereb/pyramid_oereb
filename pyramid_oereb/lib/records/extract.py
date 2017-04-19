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

    def __init__(self, real_estate, logo_plr_cadastre, federal_logo, cantonal_logo, municipality_logo,
                 exclusions_of_liability=None, glossaries=None, notconcerned_theme=None):
        """
        The extract base class.
        :param real_estate: The real estate in its record representation.
        :type real_estate: pyramid_oereb.lib.records.real_estate.RealEstateRecord
        :param logo_plr_cadastre: Image file of the PLR logo
        :type logo_plr_cadastre: bytes
        :param federal_logo:Image file of the federal logo
        :type federal_logo: bytes
        :param cantonal_logo: Image file of the cantonal logo
        :type cantonal_logo: bytes
        :param municipality_logo: Image file of the municipality logo
        :type municipality_logo: bytes
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
            'exclusions_of_liability',
            'glossaries'
        ]
