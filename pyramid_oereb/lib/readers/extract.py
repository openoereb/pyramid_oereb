# -*- coding: utf-8 -*-
from pyramid_oereb.lib.records.extract import ExtractRecord
from pyramid_oereb.lib.records.plr import PlrRecord, EmptyPlrRecord


class ExtractReader(object):

    def __init__(self, plr_sources, plr_cadastre_authority, logos):
        """
        The central reader accessor for the extract inside the application.

        :param dotted_source_class_path: The path to the class which represents the source used by this
            reader. This class must exist and it must implement basic source behaviour.
        :type dotted_source_class_path: str or pyramid_oereb.lib.sources.extract.ExtractBaseSource
        :param plr_cadastre_authority: The authority responsible for the PLR cadastre.
        :type plr_cadastre_authority: pyramid_oereb.lib.records.office.OffcieRecord
        :param logos: The logos of confederation, canton and oereb wrapped in a LogoRecord
        :type logos: dict
        """
        self.extract = None
        self._plr_sources_ = plr_sources
        self._plr_cadastre_authority_ = plr_cadastre_authority
        self._logos_ = logos

    @property
    def plr_cadastre_authority(self):
        """
        Returns the authority responsible for the PLR cadastre.

        :return: The authority responsible for the PLR cadastre.
        :rtype: pyramid_oereb.lib.records.office.OffcieRecord
        """
        return self._plr_cadastre_authority_

    @property
    def logo_plr_cadastre(self):
        """

        :return: The logo for oereb as a LogoRecord.
        :rtype: pyramid_oereb.lib.records.logo.LogoRecord
        """
        return self._logos_.get('oereb')

    @property
    def federal_logo(self):
        """

        :return: The federal logo as a LogoRecord.
        :rtype: pyramid_oereb.lib.records.logo.LogoRecord
        """
        return self._logos_.get('confederation')

    @property
    def cantonal_logo(self):
        """

        :return: The cantonal logos as a LogoRecord.
        :rtype: pyramid_oereb.lib.records.logo.LogoRecord
        """
        return self._logos_.get('canton')

    def read(self, real_estate, municipality_logo):
        """
        The central read accessor method to get all desired records from configured source.

        :param real_estate: The real estate for which the report should be generated
        :type real_estate: pyramid_oereb.lib.records.real_estate.RealEstateRecord
        :param municipality_logo: The municipality logo.
        :type municipality_logo: pyramid_oereb.lib.records.logo.LogoRecord
        :return: The extract record containing all gathered data.
        :rtype: pyramid_oereb.lib.records.extract.ExtractRecord
        """

        for plr_source in self._plr_sources_:
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

        self.extract = ExtractRecord(
            real_estate,
            self.logo_plr_cadastre,
            self.federal_logo,
            self.cantonal_logo,
            municipality_logo,
            self.plr_cadastre_authority,
            concerned_theme=concerned_themes,
            not_concerned_theme=not_concerned_themes,
            theme_without_data=themes_without_data
        )

        return self.extract
