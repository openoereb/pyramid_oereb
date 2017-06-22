# -*- coding: utf-8 -*-
import logging

from sqlalchemy.orm.exc import NoResultFound

from pyramid_oereb.lib.records.documents import DocumentRecord
from pyramid_oereb.lib.records.plr import PlrRecord


log = logging.getLogger('pyramid_oereb')


class Processor(object):

    def __init__(self, real_estate_reader, municipality_reader, exclusion_of_liability_reader,
                 glossary_reader, plr_sources, extract_reader):
        """
        The Processor class is directly bound to the get_extract_by_id service in this application. It's task
        is to unsnarl the difficult model of the oereb extract and handle all objects inside this extract
        correctly. In addition it provides an easy to use method interface to access the information.
        It is also used to wrap all accessors in one point to have a processing interface.

        Args:
            real_estate_reader (pyramid_oereb.lib.readers.real_estate.RealEstateReader): The
                real estate reader instance for runtime use.
            municipality_reader (pyramid_oereb.lib.readers.municipality.MunicipalityReader): The
                municipality reader instance for runtime use.
            exclusion_of_liability_reader
                (pyramid_oereb.lib.readers.exclusion_of_liability.ExclusionOfLiabilityReader):
                The exclusion of liability reader instance for runtime use.
            glossary_reader (pyramid_oereb.lib.readers.glossary.GlossaryReader): The glossary
                reader instance for runtime use.
            plr_sources (list of pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource): The
                public law restriction source instances for runtime use wrapped in a list.
            extract_reader (pyramid_oereb.lib.readers.extract.ExtractReader): The extract reader
                instance for runtime use.
        """
        self._real_estate_reader_ = real_estate_reader
        self._municipality_reader_ = municipality_reader
        self._exclusion_of_liability_reader_ = exclusion_of_liability_reader
        self._glossary_reader_ = glossary_reader
        self._plr_sources_ = plr_sources
        self._extract_reader_ = extract_reader

    def filter_published_documents(self, record):
        """
        Filter only published documents.

        Args:
            record (pyramid_oereb.lib.records.plr.PlrRecord or
                pyramid_oereb.lib.records.documents.DocumentRecord): The public law restriction or
                document record.
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

        Args:
            extract (pyramid_oereb.lib.records.extract.ExtractRecord): The extract in it's
                unvalidated form

        Returns:
            pyramid_oereb.lib.records.extract.ExtractRecord: Returns the updated extract
        """

        real_estate = extract.real_estate
        tested_plrs = []

        for public_law_restriction in real_estate.public_law_restrictions:
            if isinstance(public_law_restriction, PlrRecord):
                public_law_restriction.calculate(real_estate)
                # Test if the geometries list is now empty - if so remove plr from plr list
                if len(public_law_restriction.geometries) > 0 and public_law_restriction.published:
                    tested_plrs.append(self.filter_published_documents(public_law_restriction))
        real_estate.public_law_restrictions = tested_plrs
        return extract

    @staticmethod
    def view_service_handling(real_estate, images):
        """
        Handles all view service related stuff. In the moment this is:
            * construction of the correct url (link_wms) depending on the real estate
            * downloading of the image if parameter was set

        Args:
            real_estate (pyramid_oereb.lib.records.real_estate.RealEstateRecord):
                The real estate record to be updated.
            images (bool): Switch whether the images should be downloaded or not.

        Returns:
            pyramid_oereb.lib.records.real_estate.RealEstateRecord: The updated extract.
        """
        # TODO: uncomment this when issue GSOREB-194 is solved.
        # extract.real_estate.plan_for_land_register.get_full_wms_url(extract.real_estate)
        # if images:
        # extract.real_estate.plan_for_land_register.download_wms_content()
        for public_law_restriction in real_estate.public_law_restrictions:
            public_law_restriction.view_service.get_full_wms_url(real_estate)
            if images:
                public_law_restriction.view_service.download_wms_content()
        return real_estate

    @staticmethod
    def get_legend_entries(real_estate):
        """
        TODO
        """
        # Get all plr that intersect (and are completely inside) the real_estate limit.
        real_estate_plr = []

        outside_real_estate_plr = []

        for public_law_restriction in real_estate.public_law_restrictions:
            intersect = False
            for geometry in public_law_restriction.geometries:
                # TODO Not sur of that, I consider the PLR as in the real_estate as soon as ONE
                # geometry touch the limit of the real_estate. Is that correct ?
                if geometry.geom.intersects(real_estate.limit):
                    intersect = True
            if intersect:
                real_estate_plr.append(public_law_restriction)
            else:
                outside_real_estate_plr.append(public_law_restriction)

        # Get the legend entries
        # TODO

        # return all array ?

    @property
    def real_estate_reader(self):
        """
        Returns:
            pyramid_oereb.lib.readers.real_estate.RealEstateReader: The real estate reader
            instance.
        """
        return self._real_estate_reader_

    @property
    def municipality_reader(self):
        """
        Returns:
            pyramid_oereb.lib.readers.municipality.MunicipalityReader: The municipality reader
            reader instance.
        """
        return self._municipality_reader_

    @property
    def exclusion_of_liability_reader(self):
        """
        Returns:
            pyramid_oereb.lib.readers.exclusion_of_liability.ExclusionOfLiabilityReader:
            The exclusion of liability reader reader instance.
        """
        return self._exclusion_of_liability_reader_

    @property
    def glossary_reader(self):
        """
        Returns:
            pyramid_oereb.lib.readers.glossary.GlossaryReader: The glossary reader reader
            instance.
        """
        return self._glossary_reader_

    @property
    def plr_sources(self):
        """
        Returns:
            list of pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource: The list of plr
            source instances.
        """
        return self._plr_sources_

    @property
    def extract_reader(self):
        """
        Returns:
            pyramid_oereb.lib.readers.extract.ExtractReader: The extract reader instance.
        """
        return self._extract_reader_

    def process(self, real_estate, params):
        """
        Central processing method to hook in from webservice.

        Args:
            real_estate (pyramid_oereb.lib.records.real_estate.RealEstateRecord): The real
                estate reader to obtain the real estates record.
            params (pyramid_oereb.views.webservice.Parameter): The parameters of the extract
                request.

        Returns:
            pyramid_oereb.lib.records.extract.ExtractRecord: The generated extract record.
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
                self.view_service_handling(extract.real_estate, params.images)
                self.get_legend_entries(extract.real_estate)
                extract.exclusions_of_liability = exclusions_of_liability
                extract.glossaries = glossaries
                return extract
        raise NoResultFound()
