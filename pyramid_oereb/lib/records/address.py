# -*- coding: utf-8 -*-


class AddressRecord(object):
    """
    The record for handling the address entity inside the application. An address is exactly defined by
    street name, zip code and street number. In addition it must have a geometry which must be a point from
    the shapely library (https://pypi.python.org/pypi/Shapely).

    Attributes:
        street_name (unicode): The name of the street for this address.
        zip_code (int): The zipcode for this address.
        street_number (unicode): The house number for this address.
        geom (shapely.geometry.Point): The point which is representing this address.
    """
    def __init__(self, street_name, zip_code, street_number, geom):
        """
        Args:
            street_name (unicode): The name of the street for this address.
            zip_code (int): The zipcode for this address.
            street_number (unicode): The house number for this address.
            geom (shapely.geometry.Point): The point which is representing this address.
        """
        self.street_name = street_name
        self.zip_code = zip_code
        self.street_number = street_number
        self.geom = geom
