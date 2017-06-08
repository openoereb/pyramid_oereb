# -*- coding: utf-8 -*-
from pyramid.path import DottedNameResolver


class AddressReader(object):

    def __init__(self, dotted_source_class_path, **params):
        """
        The central reader accessor for addresses inside the application.

        Args:
            dotted_source_class_path (strorpyramid_oereb.lib.sources.address.AddressBaseSource):
                The path to the class which represents the source used by thisreader. This
                class must exist and it must implement basic source behaviour.
            (kwargs): kwargs, which are necessary as configuration parameter for the above by
                dotted namedefined class.
        """
        source_class = DottedNameResolver().maybe_resolve(dotted_source_class_path)
        self._source_ = source_class(**params)

    def read(self, street_name, zip_code, street_number):
        """
        The central read accessor method to get all desired records from configured source.

        Args:
            street_name (unicode): The name of the street for the desired address.
            zip_code (int): The postal zipcode for the desired address.
            street_number (str): The house or so called street number of the desired address.

        Returns:
            list of pyramid_oereb.lib.records.address.AddressRecord: The list of found records.
        """
        self._source_.read(street_name, zip_code, street_number)
        return self._source_.records
