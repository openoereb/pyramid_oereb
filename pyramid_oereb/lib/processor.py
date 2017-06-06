# -*- coding: utf-8 -*-
import logging

from pyramid.config import ConfigurationError
from sqlalchemy.orm.exc import NoResultFound

from pyramid_oereb.lib.records.documents import DocumentRecord
from pyramid_oereb.lib.records.plr import PlrRecord


log = logging.getLogger('pyramid_oereb')


class Processor(object):

    def __init__(self, real_estate_reader, municipality_reader, exclusion_of_liability_reader,
                 glossary_reader, plr_sources, extract_reader, min_area=1.0, min_length=1.0,
                 plr_limits=None):
        """
        The Processor class is directly bound to the get_extract_by_id service in this application. It's task
        is to unsnarl the difficult model of the oereb extract and handle all objects inside this extract
        correctly. In addition it provides an easy to use method interface to access the information.
        It is also used to wrap all accessors in one point to have a processing interface.

        :param real_estate_reader: The real estate reader instance for runtime use.
        :type real_estate_reader: pyramid_oereb.lib.readers.real_estate.RealEstateReader
        :param municipality_reader: The municipality reader instance for runtime use.
        :type municipality_reader: pyramid_oereb.lib.readers.municipality.MunicipalityReader
        :param exclusion_of_liability_reader: The exclusion of liability reader instance for runtime use.
        :type exclusion_of_liability_reader:
            pyramid_oereb.lib.readers.exclusion_of_liability.ExclusionOfLiabilityReader
        :param glossary_reader: The glossary reader instance for runtime use.
        :type glossary_reader: pyramid_oereb.lib.readers.glossary.GlossaryReader
        :param plr_sources: The public law restriction source instances for runtime use wrapped in a list.
        :type plr_sources: list of pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
        :param extract_reader: The extract reader instance for runtime use.
        :type extract_reader: pyramid_oereb.lib.readers.extract.ExtractReader
        :param plr_limits: The configuration for limiting the intersection.
        :type plr_limits: dict or None
        :param min_area: The minimal area for a public law restriction to be displayed in the cadastre
        :type min_area: decimal
        :param min_length: The minimal length for a public law restriction to be displayed in the cadastre
        :type min_length: decimal
        """
        self._real_estate_reader_ = real_estate_reader
        self._municipality_reader_ = municipality_reader
        self._exclusion_of_liability_reader_ = exclusion_of_liability_reader
        self._glossary_reader_ = glossary_reader
        self._plr_sources_ = plr_sources
        self._extract_reader_ = extract_reader
        self._min_area_ = min_area
        self._min_length_ = min_length
        if plr_limits:
            self.plr_limits = plr_limits
        else:
            raise ConfigurationError()

    def filter_published_documents(self, record):
        """
        Filter only published documents.

        :param record: The public law restriction or document record.
        :type record: pyramid_oereb.lib.records.plr.PlrRecord or
            pyramid_oereb.lib.records.documents.DocumentRecord
        """
        published_docs = list()
        if isinstance(record, PlrRecord):
            for doc in record.documents:
                if doc.published:
                    doc = self.filter_published_documents(doc)
                    published_docs.append(doc)
            record.documents = published_docs
        elif isinstance(record, DocumentRecord):
            for doc in record.references:
                if doc.published:
                    doc = self.filter_published_documents(doc)
                    published_docs.append(doc)
            record.references = published_docs
        return record

    def plr_tolerance_check(self, extract):
        """
        The function checking if the found plr results exceed the minimal surface or length
        value defined in the configuration and should therefor be represented in the extract
        or considered 'false trues' and be removed from the results.

        :param extract: The extract in it's unvalidated form
        :type extract: pyramid_oereb.lib.records.extract.ExtractRecord
        :return: Returns the updated extract
        :rtype: pyramid_oereb.lib.records.extract.ExtractRecord
        """

        real_estate = extract.real_estate
        tested_plrs = []

        for index, public_law_restriction in enumerate(real_estate.public_law_restrictions):
            if isinstance(public_law_restriction, PlrRecord):
                tested_geometries = []
                for geometry in public_law_restriction.geometries:
                    # TODO: Remove the plr_limits when they are consumed directly from config
                    if geometry.published and geometry.calculate(real_estate, self.plr_limits):
                        tested_geometries.append(geometry)

                # Test if the geometries list is now empty - if so remove plr from plr list
                if len(tested_geometries) > 0 and public_law_restriction.published:
                    public_law_restriction.geometries = tested_geometries
                    tested_plrs.append(self.filter_published_documents(public_law_restriction))
        real_estate.public_law_restrictions = tested_plrs

        return extract

    def view_service_handling(self, extract):
        """
        Handles all view service related stuff. In the moment this is:
            * construction of the correct url (link_wms) depending on the real estate
            * downloading of the image if parameter was set

        :param extract:
        :return:
        """

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
    def exclusion_of_liability_reader(self):
        """

        :return: The exclusion of liability reader reader instance.
        :rtype municipality_reader:
            pyramid_oereb.lib.readers.exclusion_of_liability.ExclusionOfLiabilityReader
        """
        return self._exclusion_of_liability_reader_

    @property
    def glossary_reader(self):
        """

        :return: The glossary reader reader instance.
        :rtype municipality_reader: pyramid_oereb.lib.readers.glossary.GlossaryReader
        """
        return self._glossary_reader_

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

    def process(self, real_estate, params):
        """
        Central processing method to hook in from webservice.

        :param real_estate: The real estate reader to obtain the real estates record.
        :type real_estate: pyramid_oereb.lib.records.real_estate.RealEstateRecord
        :param params: The parameters of the extract request.
        :type params: pyramid_oereb.views.webservice.Parameter
        :return: The generated extract record.
        :rtype: pyramid_oereb.lib.records.extract.ExtractRecord
        """
        municipalities = self._municipality_reader_.read()
        exclusions_of_liability = self._exclusion_of_liability_reader_.read()
        glossaries = self._glossary_reader_.read()
        for municipality in municipalities:
            if municipality.fosnr == real_estate.fosnr:
                if not municipality.published:
                    raise NotImplementedError  # TODO: improve message
                extract_raw = self._extract_reader_.read(real_estate, municipality.logo, params)
                extract = self.plr_tolerance_check(extract_raw)
                extract.exclusions_of_liability = exclusions_of_liability
                extract.glossaries = glossaries
                return extract
        raise NoResultFound()
