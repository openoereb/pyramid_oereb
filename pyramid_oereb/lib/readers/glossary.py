# -*- coding: utf-8 -*-
from pyramid.path import DottedNameResolver


class GlossaryReader(object):

    def __init__(self, dotted_source_class_path, **params):
        """
        The central reader for the glossary definitions inside the application.

        Args:
            dotted_source_class_path
                (strorpyramid_oereb.lib.sources.glossary.GlossaryBaseSource): The path to
                the class which represents the source used by thisreader. This class must
                exist and it must implement basic source behaviour.
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
            title (unicode): The term or abbreviation to be defined or explained.
            content (unicode): The definition or explanation to a given term or abbreviation.

        Returns:
            list of pyramid_oereb.lib.records.glossary.GlossaryRecord: The list of found records.
        """
        self._source_.read()
        return self._source_.records
