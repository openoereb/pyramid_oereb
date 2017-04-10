# -*- coding: utf-8 -*-


class AddressRecord(object):

    def __init__(self, street_name, zip_code, number, geometry):
        """
        The base document class.
        :param street_name: The name of the street for this address.
        :type street_name: unicode
        :param zip_code: The zipcode for this address.
        :type zip_code: int
        :param number: The house number for this address.
        :type number: str
        :param number: The geometry (point) which is representing this address as a WKT.
        :type number: str
        """
        self.street_name = street_name
        self.zip_code = zip_code
        self.number = number
        self.geometry = geometry

    @classmethod
    def get_fields(cls):
        """
        Returns a list of available field names.
        :return: List of available field names.
        :rtype: list of str
        """
        return [
            'street_name',
            'zip_code',
            'number',
            'geometry'
        ]
