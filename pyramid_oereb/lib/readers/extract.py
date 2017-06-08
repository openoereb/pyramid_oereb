# -*- coding: utf-8 -*-
import datetime

from pyramid_oereb.lib.config import Config
from pyramid_oereb.lib.records.extract import ExtractRecord
from pyramid_oereb.lib.records.plr import PlrRecord, EmptyPlrRecord


class ExtractReader(object):

    def __init__(self, plr_sources, plr_cadastre_authority, logos):
        """
        The central reader accessor for the extract inside the application.

        Args:
            plr_sources (list of pyramid_oereb.lib.sources.plr.PlrBaseSource): The list of
                configured PLR source instances.
            plr_cadastre_authority (pyramid_oereb.lib.records.office.OffcieRecord): The
                authority responsible for the PLR cadastre.
            logos (dict): The logos of confederation, canton and oereb wrapped in a ImageRecord
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

        Returns:
            pyramid_oereb.lib.records.logo.LogoRecord: The logo for oereb as a LogoRecord.
        """
        return self._logos_.get('oereb')

    @property
    def federal_logo(self):
        """

        Returns:
            pyramid_oereb.lib.records.logo.LogoRecord: The federal logo as a LogoRecord.
        """
        return self._logos_.get('confederation')

    @property
    def cantonal_logo(self):
        """

        Returns:
            pyramid_oereb.lib.records.logo.LogoRecord: The cantonal logos as a LogoRecord.
        """
        return self._logos_.get('canton')

    def read(self, real_estate, municipality_logo, params):
        """
        The central read accessor method to get all desired records from configured source.

        Args:
            real_estate (pyramid_oereb.lib.records.real_estate.RealEstateRecord): The real
                estate for which the report should be generated
            municipality_logo (pyramid_oereb.lib.records.logo.LogoRecord): The municipality
                logo.
            params (pyramid_oereb.views.webservice.Parameter): The parameters of the extract
                request.

        Returns:
            pyramid_oereb.lib.records.extract.ExtractRecord: The extract record containing all
            gathered data.
        """

        for plr_source in self._plr_sources_:
            if params.skip_topic(plr_source.info.get('code')):
                continue
            plr_source.read(real_estate)

        concerned_themes = list()
        not_concerned_themes = list()
        themes_without_data = list()
        for plr in real_estate.public_law_restrictions:
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
        # TODO: Set correct date for base data
        base_data = Config.get_base_data(datetime.date.today())

        self.extract = ExtractRecord(
            real_estate,
            self.logo_plr_cadastre,
            self.federal_logo,
            self.cantonal_logo,
            municipality_logo,
            self.plr_cadastre_authority,
            base_data,
            concerned_theme=concerned_themes,
            not_concerned_theme=not_concerned_themes,
            theme_without_data=themes_without_data
        )

        return self.extract
