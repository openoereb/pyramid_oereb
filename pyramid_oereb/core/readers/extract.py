# -*- coding: utf-8 -*-
import logging
from pyramid.path import DottedNameResolver

from shapely.geometry import box
from timeit import default_timer as timer

from pyramid_oereb.core.config import Config
from pyramid_oereb.core.records.extract import ExtractRecord
from pyramid_oereb.core.records.plr import PlrRecord, EmptyPlrRecord

log = logging.getLogger(__name__)


class ExtractReader(object):
    """
    The class which generates *the extract* as a record
    (:ref:`api-pyramid_oereb-core-records-extract-extractrecord`). This is the point where all necessary
    and extract related components are bound together.

    Attributes:
        extract (pyramid_oereb.lib.records.extract.ExtractRecord or None): The extract as a record
            representation. On initialisation this is None. It will be set by calling the read method of the
            instance.
    """

    def __init__(self, plr_sources, plr_cadastre_authority):
        """
        Args:
            plr_sources (list of pyramid_oereb.lib.sources.plr.PlrBaseSource): The list of PLR source
                instances which the achieved extract should be about.
            plr_cadastre_authority (pyramid_oereb.lib.records.office.OfficeRecord): The authority responsible
                for the PLR cadastre.
        """
        self.extract = None
        self._plr_sources_ = plr_sources
        self._plr_cadastre_authority_ = plr_cadastre_authority
        self.law_status = Config.get_law_status_codes()

    @property
    def plr_cadastre_authority(self):
        """
        Returns:
            pyramid_oereb.lib.records.office.OfficeRecord: The authority responsible for the PLR
            cadastre.
        """
        return self._plr_cadastre_authority_

    def read(self, params, real_estate, municipality):
        """
        This method finally creates the extract.

        Note:
            If you subclass this class your implementation needs to offer this method in the same
            signature. Means the parameters must be the same and the return must be a
            :ref:`api-pyramid_oereb-core-records-extract-extractrecord`. Otherwise the API like way the server
            works would be broken.

        Args:
            params (pyramid_oereb.views.webservice.Parameter): The parameters of the extract request.
            real_estate (pyramid_oereb.lib.records.real_estate.RealEstateRecord): The real
                estate for which the report should be generated
            municipality (pyramid_oereb.lib.records.municipality.MunicipalityRecord): The municipality
                record.

        Returns:
            pyramid_oereb.lib.records.extract.ExtractRecord:
                The extract record containing all gathered data.
        """
        log.debug("read() start")

        bbox = Config.get_bbox(real_estate.limit)
        bbox = box(bbox[0], bbox[1], bbox[2], bbox[3])

        concerned_themes = list()
        not_concerned_themes = list()
        themes_without_data = list()

        if municipality.published:

            for plr_source in self._plr_sources_:
                if not params.skip_topic(plr_source.info.get('code')):
                    plr_source.read(params, real_estate, bbox)

                    real_estate.public_law_restrictions.extend(plr_source.records)

            for plr in real_estate.public_law_restrictions:

                # Filter topics due to topics parameter
                if not params.skip_topic(plr.theme.code):
                    if isinstance(plr, PlrRecord):
                        if plr.theme.code not in [theme.code for theme in concerned_themes]:
                            concerned_themes.append(plr.theme)
                    elif isinstance(plr, EmptyPlrRecord):
                        if plr.has_data:
                            not_concerned_themes.append(plr.theme)
                        else:
                            themes_without_data.append(plr.theme)

        else:
            for plr_source in self._plr_sources_:
                themes_without_data.append(Config.get_theme_by_code_sub_code(plr_source.info.get('code')))

        # sort plr according to theme, sub-theme and law-status
        start_time = timer()
        log.debug("sort plrs by theme and law status start")
        real_estate.public_law_restrictions.sort(key=lambda element: (
            self._sort_plr_theme(element), self._sort_plr_law_status(element)
        ))
        end_time = timer()
        log.debug(f"DONE with sort plrs by theme and law status, time spent: {end_time-start_time} seconds")

        # Load base data form configuration
        resolver = DottedNameResolver()
        date_method_string = Config.get('extract').get('base_data').get('methods').get('date')
        date_method = resolver.resolve(date_method_string)
        update_date_os = date_method(real_estate)
        general_information = Config.get_general_information()

        oereb_logo = Config.get_oereb_logo()
        confederation_logo = Config.get_conferderation_logo()
        canton_logo = Config.get_canton_logo()
        municipality_logo = Config.get_municipality_logo(municipality.fosnr)

        self.extract = ExtractRecord(
            real_estate,
            oereb_logo,
            confederation_logo,
            canton_logo,
            municipality_logo,
            self.plr_cadastre_authority,
            update_date_os,
            concerned_theme=concerned_themes,
            not_concerned_theme=not_concerned_themes,
            theme_without_data=themes_without_data,
            general_information=general_information
        )

        log.debug("read() done")
        return self.extract

    def _sort_plr_law_status(self, plr_element):
        """
        This method generates the sorting key for plr_elements according to their law_status code.
        The value is generated from the index the plr_element.law_status.code has in the law_status
        list. The law_status list corresponds to the law status taken from the DB

        If the argument is not a PlrRecord or its law_status.code is not contained in the law_status list,
        the method will return the length of the law_status list so it can be sorted at the end of the list.

        Args:
            plr_element (PlrRecord or EmptyPlrRecord) a plr record element.

        Returns:
            int: Value which can be used to sort the record depending on its law_status.code.

        """
        if (isinstance(plr_element, PlrRecord) and plr_element.law_status.code in self.law_status):
            return self.law_status.index(plr_element.law_status.code)
        else:
            return len(self.law_status)

    @staticmethod
    def _sort_plr_theme(plr_element):
        """
        This method generates a sorting key to sort PLRs in to themes and sub-themes.
        The value is generated using the extract_index given for each theme.
        Currently it is assumed that the extract_index for a sub-theme is in accord to
        its theme so that the order will be correct.

        If the plr_element is not a PlrRecord 10 000 will be returned so that it is
        added at the end of the list

        Args:
            plr_element (PlrRecord or EmptyPlrRecord) a plr record element.

        Returns:
            int: Value which can be used to sort the record depending on its theme/sub-theme.
        """
        if (isinstance(plr_element, PlrRecord)):
            index = plr_element.sub_theme.extract_index \
                if (plr_element.sub_theme is not None) \
                else plr_element.theme.extract_index
            return index
        return 10000
