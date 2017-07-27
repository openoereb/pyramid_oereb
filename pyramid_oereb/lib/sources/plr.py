# -*- coding: utf-8 -*-
import logging

from pyramid_oereb.lib.records.documents import DocumentRecord, ArticleRecord
from pyramid_oereb.lib.records.embeddable import DatasourceRecord
from pyramid_oereb.lib.records.exclusion_of_liability import ExclusionOfLiabilityRecord
from pyramid_oereb.lib.records.geometry import GeometryRecord
from pyramid_oereb.lib.records.glossary import GlossaryRecord
from pyramid_oereb.lib.records.law_status import LawStatusRecord
from pyramid_oereb.lib.records.office import OfficeRecord
from pyramid_oereb.lib.records.plr import PlrRecord
from pyramid_oereb.lib.records.view_service import ViewServiceRecord, LegendEntryRecord
from pyramid_oereb.lib.sources import Base

log = logging.getLogger('pyramid_oereb')


class PlrBaseSource(Base):
    """
    Base class for public law restriction sources.

    Attributes:
        records (list of pyramid_oereb.lib.records.plr.EmptyPlrRecord): List of public law restriction
            records.
        datasource (list of pyramid_oereb.lib.records.embeddable.DatasourceRecord): List of data source
            records used for the additional data in flavour `embeddable`.
    """
    _documents_reocord_class = DocumentRecord
    _article_record_class = ArticleRecord
    _exclusion_of_liability_record_class = ExclusionOfLiabilityRecord
    _geometry_record_class = GeometryRecord
    _glossary_record_class = GlossaryRecord
    _legend_entry_record_class = LegendEntryRecord
    _office_record_class = OfficeRecord
    _plr_record_class = PlrRecord
    _view_service_record_class = ViewServiceRecord
    _law_status_record_class = LawStatusRecord
    _datasource_record_class = DatasourceRecord

    datasource = list()

    def __init__(self, **kwargs):
        self._plr_info = kwargs

    @property
    def info(self):
        """
        Return the info dictionary.

        Returns:
            dict: The info dictionary.
        """
        return self._plr_info

    def read(self, real_estate, bbox):
        """
        The read point which creates a extract, depending on a passed real estate.

        Args:
            real_estate (pyramid_oereb.lib.records.real_estate.RealEstateRecord): The real
                estate in its record representation.
            bbox (shapely.geometry.base.BaseGeometry): The bbox to search the records.
        """
        self.records = list()
