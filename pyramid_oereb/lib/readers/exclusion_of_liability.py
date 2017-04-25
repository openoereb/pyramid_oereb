# -*- coding: utf-8 -*-
from pyramid.path import DottedNameResolver


class ExclusionOfLiabilityReader(object):

    def __init__(self, dotted_source_class_path, **params):
        """
        The central reader for the exclusion of liability definitions.
        :param dotted_source_class_path: The path to the class which represents the source used by this
        reader. This class must exist and it must implement basic source behaviour.
        :type dotted_source_class_path: str or
            pyramid_oereb.lib.sources.exclusion_of_liability.ExclusionOfLiabiltyBaseSource
        :param params: kwargs, which are necessary as configuration parameter for the above by dotted name
        defined class.
        :type: kwargs
        """
        source_class = DottedNameResolver().maybe_resolve(dotted_source_class_path)
        self._source_ = source_class(**params)

    def read(self):
        """
        The central read accessor method to get all desired records from configured source.
        :param id: The identifier of the entry.
        :type id: int
        :param title: The label of the disclaimer message.
        :type title: unicode
        :param content: The disclaimer message.
        :type content: unicode
        :returns: The list of found records.
        :rtype: list of pyramid_oereb.lib.records.exclusion_of_liability.ExclusionOfLiabiltyRecord
        """
        self._source_.read()
        return self._source_.records
