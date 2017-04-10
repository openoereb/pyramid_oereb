# -*- coding: utf-8 -*-


class AddressRecord(object):

    def __init__(self, street_name, zip_code, street_number, geom):
        """
        The record for handling the address entity inside the application.
        :param street_name: The name of the street for this address.
        :type street_name: unicode
        :param zip_code: The zipcode for this address.
        :type zip_code: int
        :param street_number: The house number for this address.
        :type street_number: str
        :param geom: The geometry (point) which is representing this address as a WKT.
        :type geom: str
        """
        self.street_name = street_name
        self.zip_code = zip_code
        self.street_number = street_number
        self.geom = geom

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
            'street_number',
            'geom'
        ]
