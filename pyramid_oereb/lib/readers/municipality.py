# -*- coding: utf-8 -*-
from pyramid.path import DottedNameResolver


class MunicipalityReader(object):

    def __init__(self, dotted_source_class_path, **params):

        """
        The central reader accessor for municipalities inside the application.
        :param dotted_source_class_path: The path to the class which represents the source used by this
        reader. This class must exist and it must implement basic source behaviour.
        :type dotted_source_class_path: str
        :param params: kwargs, which are necessary as configuration parameter for the above by dotted name
        defined class.
        :type: kwargs
        """
        source_class = DottedNameResolver().resolve(dotted_source_class_path)
        self._source_ = source_class(**params)

    def read(self, **kwargs):
        """
        The central read accessor method to get all desired records from configured source.
        :param kwargs: the kwargs which are necessary as parameters for querying the municipality source.
        :type kwargs: dict
        :return: the list of all found records
        :rtype: list of pyramid_oereb.lib.records.municipality.MunicipalityRecord
        """
        self._source_.read(**kwargs)
        return self._source_.records
