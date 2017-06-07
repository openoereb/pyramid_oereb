# -*- coding: utf-8 -*-

from pyramid.path import DottedNameResolver


class RealEstateReader(object):

    def __init__(self, dotted_source_class_path, **params):
        """
        The central reader accessor for real estates inside the application.

        Args:
            dotted_source_class_path (str): The path to the class which represents the source
                used by thisreader. This class must exist and it must implement basic source
                behaviour.
            (kwargs): kwargs, which are necessary as configuration parameter for the above by
                dotted namedefined class.
        """
        source_class = DottedNameResolver().resolve(dotted_source_class_path)
        self._source_ = source_class(**params)

    def read(self, nb_ident=None, number=None, egrid=None, geometry=None):
        """
        The central read accessor method to get all desired records from configured source.

        Args:
            nb_ident (int or None): The identification number of the desired real estate. This
                parameter is directlyrelated to the number parameter and both must be set!
                Combination will deliver only one result orcrashes.
            number (str or None): The number of parcel or also known real estate. This parameter
                is directlyrelated to the nb_ident parameter and both must be set!
                Combination will deliver only one result orcrashes.
            (str or None): The unique identifier of the desired real estate. This will deliver
                only one result orcrashes.
            geometry (str): A geometry as WKT string which is used to obtain intersected real
                estates. This maydeliver several results.

        Returns:
            list of pyramid_oereb.lib.records.real_estate.RealEstateRecord: the list of all found
            records
        """

        self._source_.read(nb_ident=nb_ident, number=number, egrid=egrid, geometry=geometry)
        return self._source_.records
