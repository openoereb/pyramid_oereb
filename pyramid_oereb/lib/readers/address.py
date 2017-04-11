# -*- coding: utf-8 -*-
from pyramid.path import DottedNameResolver


class AddressReader(object):

    def __init__(self, dotted_source_class_path, **params):
        """
        The central reader accessor for addresses inside the application.
        :param dotted_source_class_path: The path to the class which represents the source used by this
        reader. This class must exist and it must implement basic source behaviour.
        :type dotted_source_class_path: str or pyramid_oereb.lib.sources.address.AddressBaseSource
        :param params: kwargs, which are necessary as configuration parameter for the above by dotted name
        defined class.
        :type: kwargs
        """
        source_class = DottedNameResolver().maybe_resolve(dotted_source_class_path)
        self._source_ = source_class(**params)

    def read(self, street_name, zip_code, street_number):
        """
        The central read accessor method to get all desired records from configured source.
        :param street_name: The name of the street for the desired address.
        :type street_name: unicode
        :param zip_code: The postal zipcode for the desired address.
        :type zip_code: int
        :param street_number: The house or so called street number of the desired address.
        :type street_number: str
        :returns: The list of found records.
        :rtype: list of pyramid_oereb.lib.records.address.AddressRecord
        """
        self._source_.read(street_name, zip_code, street_number)
        return self._source_.records
