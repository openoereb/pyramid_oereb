# -*- coding: utf-8 -*-
import datetime
from pyramid.path import DottedNameResolver

from shapely.geometry import box

from pyramid_oereb.lib.config import Config
from pyramid_oereb.lib.records.embeddable import EmbeddableRecord
from pyramid_oereb.lib.records.extract import ExtractRecord
from pyramid_oereb.lib.records.image import ImageRecord
from pyramid_oereb.lib.records.plr import PlrRecord, EmptyPlrRecord
from pyramid_oereb.lib.records.view_service import ViewServiceRecord


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

    def __init__(self, plr_sources, plr_cadastre_authority, logos):
        """
        Args:
            plr_sources (list of pyramid_oereb.lib.sources.plr.PlrBaseSource): The list of PLR source
                instances which the achieved extract should be about.
            plr_cadastre_authority (pyramid_oereb.lib.records.office.OffcieRecord): The authority responsible
                for the PLR cadastre.
            logos (dict): The logos of confederation, canton and oereb wrapped in a ImageRecord.
        """
        self.extract = None
        self._plr_sources_ = plr_sources
        self._plr_cadastre_authority_ = plr_cadastre_authority
        self._logos_ = logos

    @property
    def plr_cadastre_authority(self):
        """
        Returns the authority responsible for the PLR cadastre.

        Returns:
            pyramid_oereb.lib.records.office.OffcieRecord: The authority responsible for the PLR
            cadastre.
        """
        return self._plr_cadastre_authority_

    @property
    def logo_plr_cadastre(self):
        """
        The logo of the PLR-Cadastre.

        Returns:
            pyramid_oereb.lib.records.image.ImageRecord: The logo for oereb as a ImageRecord.
        """
        return self._logos_.get('oereb')

    @property
    def federal_logo(self):
        """
        The logo of the confederation.

        Returns:
            pyramid_oereb.lib.records.image.ImageRecord: The federal logo as a ImageRecord.
        """
        return self._logos_.get('confederation')

    @property
    def cantonal_logo(self):
        """
        The cantonal logo.

        Returns:
            pyramid_oereb.lib.records.image.ImageRecord: The cantonal logos as a ImageRecord.
        """
        return self._logos_.get('canton')

    def read(self, real_estate, municipality_logo, params):
        """
        This method finally creates the extract.

        .. note:: If you subclass this class your implementation needs to offer this method in the same
            signature. Means the parameters must be the same and the return must be a
            :ref:`api-pyramid_oereb-lib-records-extract-extractrecord`. Otherwise the API like way the server
            works would be broken.

        Args:
            real_estate (pyramid_oereb.lib.records.real_estate.RealEstateRecord): The real
                estate for which the report should be generated
            municipality_logo (pyramid_oereb.lib.records.image.ImageRecord): The municipality
                logo.
            params (pyramid_oereb.views.webservice.Parameter): The parameters of the extract
                request.

        Returns:
            pyramid_oereb.lib.records.extract.ExtractRecord:
                The extract record containing all gathered data.
        """
        assert isinstance(municipality_logo, ImageRecord)

        print_conf = Config.get_object_path('print', required=['buffer'])
        map_size = ViewServiceRecord.get_map_size(params.format)
        bbox = ViewServiceRecord.get_bbox(real_estate.limit, map_size, print_conf['buffer'])
        bbox = box(bbox[0], bbox[1], bbox[2], bbox[3])

        datasource = list()
        for plr_source in self._plr_sources_:
            if not params.skip_topic(plr_source.info.get('code')):
                plr_source.read(real_estate, bbox)
                for ds in plr_source.datasource:
                    if not params.skip_topic(ds.theme.code):
                        datasource.append(ds)
                real_estate.public_law_restrictions.extend(plr_source.records)

        concerned_themes = list()
        not_concerned_themes = list()
        themes_without_data = list()
        for plr in real_estate.public_law_restrictions:

            # Filter topics due to topics parameter
            if not params.skip_topic(plr.theme.code):
                if isinstance(plr, PlrRecord):
                    contained = False
                    for theme in concerned_themes:
                        if theme.code == plr.theme.code:
                            contained = True
                    if not contained:
                        concerned_themes.append(plr.theme)
                elif isinstance(plr, EmptyPlrRecord):
                    if plr.has_data:
                        not_concerned_themes.append(plr.theme)
                    else:
                        themes_without_data.append(plr.theme)

        # Load base data form configuration
        resolver = DottedNameResolver()
        date_method_string = Config.get('extract').get('base_data').get('methods').get('date')
        date_method = resolver.resolve(date_method_string)
        av_update_date = date_method(real_estate)
        base_data = Config.get_base_data(av_update_date)

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
            self.logo_plr_cadastre,
            self.federal_logo,
            self.cantonal_logo,
            municipality_logo,
            self.plr_cadastre_authority,
            base_data,
            embeddable,
            concerned_theme=concerned_themes,
            not_concerned_theme=not_concerned_themes,
            theme_without_data=themes_without_data
        )

        return self.extract
