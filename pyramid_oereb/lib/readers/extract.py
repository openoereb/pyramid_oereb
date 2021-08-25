# -*- coding: utf-8 -*-
import datetime
import logging
from pyramid.path import DottedNameResolver

from shapely.geometry import box
from timeit import default_timer as timer

from pyramid_oereb.lib.config import Config
from pyramid_oereb.lib.records.embeddable import EmbeddableRecord
from pyramid_oereb.lib.records.extract import ExtractRecord
from pyramid_oereb.lib.records.plr import PlrRecord, EmptyPlrRecord
from pyramid_oereb.lib.records.view_service import ViewServiceRecord

log = logging.getLogger(__name__)


class ExtractReader(object):
    """
    The class which generates *the extract* as a record
    (:ref:`api-pyramid_oereb-lib-records-extract-extractrecord`). This is the point where all necessary
    and extract related components are bound together.

    Attributes:
        extract (pyramid_oereb.lib.records.extract.ExtractRecord or None): The extract as a record
            representation. On initialisation this is None. It will be set by calling the read method of the
            instance.
    """

    def __init__(self, plr_sources, plr_cadastre_authority, certification=None,
                 certification_at_web=None):
        """
        Args:
            plr_sources (list of pyramid_oereb.lib.sources.plr.PlrBaseSource): The list of PLR source
                instances which the achieved extract should be about.
            plr_cadastre_authority (pyramid_oereb.lib.records.office.OfficeRecord): The authority responsible
                for the PLR cadastre.
            certification (dict of unicode or None): A mutlilingual dictionary of certification information.
            certification_at_web (dict of unicode or None): Multilingual list of certification uri.
        """
        self.extract = None
        self._plr_sources_ = plr_sources
        self._plr_cadastre_authority_ = plr_cadastre_authority
        self._certification = certification
        self._certification_at_web = certification_at_web
        self.law_status = Config.get_law_status_codes()

    @property
    def plr_cadastre_authority(self):
        """
        Returns the authority responsible for the PLR cadastre.

        Returns:
            pyramid_oereb.lib.records.office.OfficeRecord: The authority responsible for the PLR
            cadastre.
        """
        return self._plr_cadastre_authority_

    @property
    def certification(self):
        """
        Returns the certification if it exists.

        Returns:
            dict: (dict of unicode or None) The multilingual list of certification or None.
        """
        return self._certification

    @property
    def certification_at_web(self):
        """
        Returns the web certification if it exists.

        Returns:
            dict: (dict of unicode or None) The multilingual list of certification uri None.
        """
        return self._certification_at_web

    def read(self, params, real_estate, municipality):
        """
        This method finally creates the extract.

        .. note:: If you subclass this class your implementation needs to offer this method in the same
            signature. Means the parameters must be the same and the return must be a
            :ref:`api-pyramid_oereb-lib-records-extract-extractrecord`. Otherwise the API like way the server
            works would be broken.

        Args:
            params (pyramid_oereb.views.webservice.Parameter): The parameters of the extract request.
            real_estate (pyramid_oereb.lib.records.real_estate.RealEstateRecord): The real
                estate for which the report should be generated
            municipality (pyramid_oereb.lib.records.municipiality.MunicipalityRecord): The municipality
                record.

        Returns:
            pyramid_oereb.lib.records.extract.ExtractRecord:
                The extract record containing all gathered data.
        """
        log.debug("read() start")

        bbox = ViewServiceRecord.get_bbox(real_estate.limit)
        bbox = box(bbox[0], bbox[1], bbox[2], bbox[3])

        datasource = list()
        concerned_themes = list()
        not_concerned_themes = list()
        themes_without_data = list()

        if municipality.published:

            for position, plr_source in enumerate(self._plr_sources_, start=1):
                if not params.skip_topic(plr_source.info.get('code')):
                    plr_source.read(params, real_estate, bbox, position)
                    for ds in plr_source.datasource:
                        if not params.skip_topic(ds.theme.code):
                            datasource.append(ds)

                    # Sort PLR records according to their law status
                    start_time = timer()
                    log.debug("sort plrs by law status start")
                    plr_source.records.sort(key=self._sort_plr_law_status)
                    end_time = timer()
                    log.debug(f"DONE with sort plrs by law status, time spent: {end_time-start_time} seconds")

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
                themes_without_data.append(Config.get_theme_by_code(plr_source.info.get('code')))

        # Load base data form configuration
        resolver = DottedNameResolver()
        date_method_string = Config.get('extract').get('base_data').get('methods').get('date')
        date_method = resolver.resolve(date_method_string)
        av_update_date = date_method(real_estate)
        base_data = Config.get_base_data(av_update_date)
        general_information = Config.get_general_information()

        oereb_logo = Config.get_oereb_logo()
        confederation_logo = Config.get_conferderation_logo()
        canton_logo = Config.get_canton_logo()
        municipality_logo = Config.get_municipality_logo(municipality.fosnr)

        av_provider_method_string = Config.get('extract').get('base_data').get('methods').get('provider')
        av_provider_method = resolver.resolve(av_provider_method_string)
        cadaster_state = datetime.datetime.now()
        embeddable = EmbeddableRecord(
            cadaster_state,
            self.plr_cadastre_authority,
            av_provider_method(real_estate),
            av_update_date,
            datasource
        )

        self.extract = ExtractRecord(
            real_estate,
            oereb_logo,
            confederation_logo,
            canton_logo,
            municipality_logo,
            self.plr_cadastre_authority,
            base_data,
            embeddable,
            self.certification,
            self.certification_at_web,
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
