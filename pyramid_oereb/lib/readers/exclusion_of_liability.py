# -*- coding: utf-8 -*-
from pyramid.path import DottedNameResolver


class ExclusionOfLiabilityReader(object):

    def __init__(self, dotted_source_class_path, **params):
        """
        The central reader for the exclusion of liability definitions.

        Args:
            dotted_source_class_path (str or
                pyramid_oereb.lib.sources.exclusion_of_liability.ExclusionOfLiabiltyBaseSource):
                The path to the class which represents the source used by thisreader. This
                class must exist and it must implement basic source behaviour.
            (kwargs): kwargs, which are necessary as configuration parameter for the above by
                dotted namedefined class.
        """
        source_class = DottedNameResolver().maybe_resolve(dotted_source_class_path)
        self._source_ = source_class(**params)

    def read(self):
        """
        The central read accessor method to get all desired records from configured source.

        Args:
            id (int): The identifier of the entry.
            title (unicode): The label of the disclaimer message.
            content (unicode): The disclaimer message.

        Returns:
            list of pyramid_oereb.lib.records.exclusion_of_liability.ExclusionOfLiabiltyRecord:
            The list of found records.
        """
        self._source_.read()
        return self._source_.records
