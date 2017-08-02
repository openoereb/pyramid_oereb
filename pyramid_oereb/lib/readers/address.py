# -*- coding: utf-8 -*-
from pyramid.path import DottedNameResolver


class AddressReader(object):
    """
    The central reader accessor for addresses. It is directly bound to a so called source which is defined by
    a pythonic dotted string to the class definition of this source. An instance of the passed source will be
    created on instantiation of this reader class by passing through the parameter kwargs.

    The address is here the real combination of a street name, a zip code and a street number.
    """

    def __init__(self, dotted_source_class_path, **params):
        """
        Args:
            dotted_source_class_path (str or pyramid_oereb.lib.sources.address.AddressBaseSource):
                The path to the class which represents the source used by this reader. This
                class must exist and it must implement basic source behaviour of the
                :ref:`api-pyramid_oereb-lib-sources-address-addressbasesource`.
            (kwargs): kwargs, which are necessary as configuration parameter for the above by
                dotted name defined class.
        """
        source_class = DottedNameResolver().maybe_resolve(dotted_source_class_path)
        self._source_ = source_class(**params)

    def read(self, street_name, zip_code, street_number):
        """
        The read method of this reader. There we invoke the read method of the bound source.

        .. note:: If you subclass this class your implementation needs to offer this method in the same
            signature. Means the parameters must be the same and the return must be a list of
            :ref:`api-pyramid_oereb-lib-records-address-addressrecord`. Otherwise the API like way the server
            works would be broken.

        Args:
            street_name (unicode): The name of the street for the desired address.
            zip_code (int): The postal zipcode for the desired address.
            street_number (str): The house or so called street number of the desired address.

        Returns:
            list of pyramid_oereb.lib.records.address.AddressRecord:
                The list of found records filtered by the passed criteria.
        """
        self._source_.read(street_name, zip_code, street_number)
        return self._source_.records
