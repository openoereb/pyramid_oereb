# -*- coding: utf-8 -*-


class ExtractRecord(object):
    # Attributes calculated or defined while processing
    creation_date = None
    electronic_signature = None
    concerned_Theme = None
    notconcerned_theme = None
    theme_without_data = None
    is_reduced = False
    extract_identifier = None
    qr_code = None
    general_information = None
    base_data = None

    def __init__(self, logo_plr_cadastre, federal_logo, cantonal_logo, municipality_logo):
        """
        The extract base class.
        :param logo_plr_cadastre: Image file of the PLR logo
        :type logo_plr_cadastre: bytes
        :param federal_logo:Image file of the federal logo
        :type federal_logo: bytes
        :param cantonal_logo: Image file of the cantonal logo
        :type cantonal_logo: bytes
        :param municipality_logo: Image file of the municipality logo
        :type municipality_logo: bytes
        """
        self.logo_plr_cadastre = logo_plr_cadastre
        self.federal_logo = federal_logo
        self.cantonal_logo = cantonal_logo
        self.municipality_logo = municipality_logo

    @classmethod
    def get_fields(cls):
        """
        Returns a list of available field names.
        :return: List of available field names.
        :rtype: list of str
        """
        return [
            'logo_plr_cadastre',
            'federal_logo',
            'cantonal_logo',
            'municipality_logo'
        ]
