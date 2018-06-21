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

log = logging.getLogger(__name__)


class PlrBaseSource(Base):
    """
    Base class for public law restriction sources.

    Attributes:
        records (list of pyramid_oereb.lib.records.plr.EmptyPlrRecord): List of public law restriction
            records.
        datasource (list of pyramid_oereb.lib.records.embeddable.DatasourceRecord): List of data source
            records used for the additional data in flavour `embeddable`.
    """
    _documents_record_class = DocumentRecord
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
        """
        Keyword Arguments:
            name (str): The name. You are free to choose one.
            code (str): The official code. Regarding to the federal specifications.
            geometry_type (str): The geometry type. Possible are: POINT, POLYGON, LINESTRING,
                GEOMETRYCOLLECTION
            thresholds (dict): The configuration of limits and units used for processing.
            text (dict of str): The speaking title. It must be a dictionary containing language (as
                configured) as key and text as value.
            language (str): The language this public law restriction is originally shipped whith.
            federal (bool): Switch if it is a federal topic. This will be taken into account in processing
                steps.
            source (dict): The configuration dictionary of the public law restriction
            hooks (dict of str): The hook methods: get_symbol, get_symbol_ref. They have to be provided as
                dotted string for further use with dotted name resolver of pyramid package.
            law_status (dict of str): The multiple match configuration to provide more flexible use of the
                federal specified classifiers 'inForce' and 'runningModifications'.
        """
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
        Every public law restriction source has to implement a read method. This method must accept the two
        key word parameters. If you want adapt to your own source for real estates, this is the point where
        to hook in.

        Args:
            real_estate (pyramid_oereb.lib.records.real_estate.RealEstateRecord): The real estate which is
                used as filter to find all related public law restrictions.
            bbox (shapely.geometry.base.BaseGeometry): The bounding box which is used as a pre-filter to find
                all public law restrictions. This is related to the fact that we need to provide not only the
                public law restrictions that are related to the real estate but also the ones which are in
                the visible extent of the map.
        """
        self.records = list()
