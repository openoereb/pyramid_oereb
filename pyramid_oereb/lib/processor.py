# -*- coding: utf-8 -*-


class Processor(object):

    def __init__(self, real_estate_reader, municipality_reader, plr_sources, extract_reader,
                 plr_cadastre_authority):
        """
        The Processor class is directly bound to the get_extract_by_id service in this application. It's task
        is to unsnarl the difficult model of the oereb extract and handle all objects inside this extract
        correctly. In addition it provides an easy to use method interface to access the information.
        It is also used to wrap all accessors in one point to have a processing interface.
        :param real_estate_reader: The real estate reader instance for runtime use.
        :type real_estate_reader: pyramid_oereb.lib.readers.real_estate.RealEstateReader
        :param municipality_reader: The municipality reader instance for runtime use.
        :type municipality_reader: pyramid_oereb.lib.readers.municipality.MunicipalityReader
        :param plr_sources: The public law restriction source instances for runtime use wrapped in a list.
        :type plr_sources: list of pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
        :param extract_reader: The extract reader instance for runtime use.
        :type extract_reader: pyramid_oereb.lib.readers.extract.ExtractReader
        :param plr_cadastre_authority: The authority responsible for the PLR cadastre.
        :type plr_cadastre_authority: pyramid_oereb.lib.records.office.OffcieRecord
        """
        self._real_estate_reader_ = real_estate_reader
        self._municipality_reader_ = municipality_reader
        self._plr_sources_ = plr_sources
        self._extract_reader_ = extract_reader
        self._plr_cadastre_authority_ = plr_cadastre_authority

    @property
    def real_estate_reader(self):
        """

        :return: The real estate reader instance.
        :rtype real_estate_reader: pyramid_oereb.lib.readers.real_estate.RealEstateReader
        """
        return self._real_estate_reader_

    @property
    def municipality_reader(self):
        """

        :return: The municipality reader reader instance.
        :rtype municipality_reader: pyramid_oereb.lib.readers.municipality.MunicipalityReader
        """
        return self._municipality_reader_

    @property
    def plr_sources(self):
        """

        :return: The list of plr source instances.
        :rtype plr_sources: list of pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
        """
        return self._plr_sources_

    @property
    def extract_reader(self):
        """

        :return: The extract reader instance.
        :rtype extract_reader: pyramid_oereb.lib.readers.extract.ExtractReader
        """
        return self._extract_reader_

    @property
    def plr_cadastre_authority(self):
        """
        Returns the authority responsible for the PLR cadastre.
        :return: The authority responsible for the PLR cadastre.
        :rtype: pyramid_oereb.lib.records.office.OffcieRecord
        """
        return self._plr_cadastre_authority_

    def process(self, real_estate, plr_cadastre_authority):
        """
        Central processing method to hook in from webservice.
        :param real_estate: The real estate reader to obtain the real estates record.
        :type real_estate: pyramid_oereb.lib.records.real_estate.RealEstateRecord
        :param plr_cadastre_authority: The authority responsible for the PLR cadastre.
        :type plr_cadastre_authority: pyramid_oereb.lib.records.office.OffcieRecord
        :return:
        """
        extract = self._extract_reader_.read(real_estate, plr_cadastre_authority)
        return extract.to_extract()
