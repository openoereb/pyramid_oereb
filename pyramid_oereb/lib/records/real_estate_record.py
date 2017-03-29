# -*- coding: utf-8 -*-


class RealEstateRecord(object):

    def __init__(self, type, canton, municipality, fosnr, metadata_of_geographical_base_data,
                 land_registry_area, limit, number=None, identdn=None, egrid=None,
                 subunit_of_land_register=None):
        """
        Basic caracteristics and geometry of the properrty to be analysed.
        :param type: The property type
        :type type: str
        :param canton: The abbreviation of the canton the property is located in
        :type canton: str
        :param municipality: The municipality the property is located in
        :type municipality: str
        :param fosnr: The federal number of the municipality defined by the statistics office
        :type fosnr: integer
        :param metadata_of_geographical_base_data: Link to the metadata of the geodata
        :type metadata_of_geographical_base_data: uri
        :param land_registry_area: Area of the property as defined in the land registry
        :type land_registry_area: integer
        :param limit: The boundary of the property as geometry in WKT format
        :type limit: str
        :param number:  The official cantonal number of the property
        :type  number: str
        :param identdn: The unique identifier of the property
        :type  identdn: str
        :param egrid: The federal property identifier
        :type egrid: str
        :param subunit_of_land_register: Subunit of the land register if existing
        :type subunit_of_land_register: str
        """
        self.number = number
        self.identdn = identdn
        self.egrid = egrid
        self.type = type
        self.canton = canton
        self.municipality = municipality
        self.subunit_of_land_register = subunit_of_land_register
        self.fosnr = fosnr
        self.metadata_of_geographical_base_data = metadata_of_geographical_base_data
        self.land_registry_area = land_registry_area
        self.limit = limit

    @classmethod
    def get_fields(cls):
        """
        Returns a list of available field names.
        :return:    List of available field names.
        :rtype:     list
        """
        return [
            'type',
            'canton',
            'municipality',
            'fosnr',
            'metadata_of_geographical_base_data',
            'land_registry_area',
            'limit',
            'number',
            'identdn',
            'egrid',
            'subunit_of_land_register'
        ]
