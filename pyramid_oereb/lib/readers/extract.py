# -*- coding: utf-8 -*-
from pyramid_oereb.lib.records.extract import ExtractRecord


class ExtractReader(object):

    def __init__(self, plr_sources):

        """
        The central reader accessor for the extract inside the application.
        :param dotted_source_class_path: The path to the class which represents the source used by this
        reader. This class must exist and it must implement basic source behaviour.
        :type dotted_source_class_path: str or pyramid_oereb.lib.sources.extract.ExtractBaseSource
        """
        self.extract = None
        self._plr_sources_ = plr_sources

    def read(self, real_estate):
        """
        The central read accessor method to get all desired records from configured source.
        :param real_estate: The real estate for which the report should be generated
        :type real_estate: pyramid_oereb.lib.records.real_estate.RealEstateRecord
        :return: The extract record containing all gathered data.
        :rtype: pyramid_oereb.lib.records.extract.ExtractRecord
        """
        for plr_source in self._plr_sources_:
            plr_source.read(real_estate)
        self.extract = ExtractRecord(
            real_estate,
            bin(100),
            bin(100),
            bin(100),
            bin(100)
        )
        return self.extract
