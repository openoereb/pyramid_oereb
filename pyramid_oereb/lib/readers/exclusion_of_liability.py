# -*- coding: utf-8 -*-
from pyramid.path import DottedNameResolver


class ExclusionOfLiabilityReader(object):
    """
    The central reader for the exclusion of liability definitions. It is directly bound to a so called source
    which is defined by a pythonic dotted string to the class definition of this source.
    An instance of the passed source will be created on instantiation of this reader class by passing through
    the parameter kwargs.
    """

    def __init__(self, dotted_source_class_path, **params):
        """
        Args:
            dotted_source_class_path (str or
                pyramid_oereb.lib.records.exclusion_of_liability.ExclusionOfLiabilityRecord):
                The path to the class which represents the source used by this reader. This
                class must exist and it must implement basic source behaviour.
            (kwargs): kwargs, which are necessary as configuration parameter for the above by
                dotted name defined class.
        """
        source_class = DottedNameResolver().maybe_resolve(dotted_source_class_path)
        self._source_ = source_class(**params)

    def read(self):
        """
        The central read accessor method to get all desired records from configured source.

        Returns:
            list of pyramid_oereb.lib.records.exclusion_of_liability.ExclusionOfLiabilityRecord: The list of
                found records.
        """
        self._source_.read()
        return self._source_.records
