# -*- coding: utf-8 -*-


class AddressRecord(object):

    def __init__(self, street_name, zip_code, street_number, geom):
        """
        The record for handling the address entity inside the application.

        Args:
            street_name (unicode): The name of the street for this address.
            zip_code (int): The zipcode for this address.
            street_number (unicode): The house number for this address.
            geom (unicode): The geometry (point) which is representing this address as a WKT.
        """
        self.street_name = street_name
        self.zip_code = zip_code
        self.street_number = street_number
        self.geom = geom
