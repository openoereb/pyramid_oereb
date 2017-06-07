# -*- coding: utf-8 -*-
from pyramid.path import DottedNameResolver


class MunicipalityReader(object):

    def __init__(self, dotted_source_class_path, **params):

        """
        The central reader accessor for municipalities inside the application.

        Args:
            dotted_source_class_path
                (strorpyramid_oereb.lib.sources.municipality.MunicipalityBaseSource): The
                path to the class which represents the source used by thisreader. This class
                must exist and it must implement basic source behaviour.
            (kwargs): kwargs, which are necessary as configuration parameter for the above by
                dotted namedefined class.
        """
        source_class = DottedNameResolver().maybe_resolve(dotted_source_class_path)
        self._source_ = source_class(**params)

    def read(self):
        """
        The central read accessor method to get all desired records from configured source.

        Returns:
            list of pyramid_oereb.lib.records.municipality.MunicipalityRecord: the list of all
            found records
        """
        self._source_.read()
        return self._source_.records
