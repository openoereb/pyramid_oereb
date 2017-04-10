# -*- coding: utf-8 -*-


class ExtractRecord(object):
    # Attributes calculated or defined while processing
    CreationDate = None
    ElectronicSignature = None
    ConcernedTheme = None
    NotConcernedTheme = None
    ThemeWithoutData = None
    IsReduced = False
    ExtractIdentifier = None
    QRCode = None
    GeneralInformation = None
    BaseData = None

    def __init__(self, LogoPLRCadastre, FederalLogo, CantonalLogo, MunicipalityLogo):
        """
        The extract base class.
        :param LogoPLRCadastre: Image file of the PLR logo
        :type LogoPLRCadastre: binary
        :param FederalLogo:Image file of the federal logo
        :type FederalLogo: binary
        :param CantonalLogo: Image file of the cantonal logo
        :type CantonalLogo: binary
        :param MunicipalityLogo: Image file of the municipality logo
        :type MunicipalityLogo: binary
        """
        self.LogoPLRCadastre = LogoPLRCadastre
        self.FederalLogo = FederalLogo
        self.CantonalLogo = CantonalLogo
        self.MunicipalityLogo = MunicipalityLogo

    @classmethod
    def get_fields(cls):
        """
        Returns a list of available field names.
        :return: List of available field names.
        :rtype: list of str
        """
        return [
            'LogoPLRCadastre',
            'FederalLogo',
            'CantonalLogo',
            'MunicipalityLogo'
        ]
