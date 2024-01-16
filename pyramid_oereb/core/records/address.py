# -*- coding: utf-8 -*-
from geoalchemy2.elements import _SpatialElement
from geoalchemy2.shape import to_shape
from shapely import is_geometry


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
        self.geom = None
        if is_geometry(geom) or isinstance(geom, str):
            self.geom = geom
        elif isinstance(geom, _SpatialElement):
            self.geom = to_shape(geom)
