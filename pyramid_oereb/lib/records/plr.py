# -*- coding: utf-8 -*-

import logging
import warnings
from datetime import datetime


LOG = logging.getLogger(__name__)


class EmptyPlrRecord(object):

    def __init__(self, theme, has_data=True):
        """
        Record for empty topics.

        Args:
            theme (pyramid_oereb.lib.records.theme.ThemeRecord): The theme to which the PLR belongs to.
            has_data (bool): True if the topic contains data.
        """
        self.theme = theme
        self.has_data = has_data


class PlrRecord(EmptyPlrRecord):
    """
    Public law restriction record.

    Attributes:
        part_in_percent (decimal): Part of the property area touched by the restriction in percent.
        area (decimal): Area of the restriction touching the property calculated by the processor.
    """

    # Attributes added or calculated by the processor
    area = None

    part_in_percent = None

    def __init__(self, theme, information, law_status, published_from, responsible_office, symbol,
                 view_service, geometries, sub_theme=None, other_theme=None, type_code=None,
                 type_code_list=None, basis=None, refinements=None, documents=None, info=None, min_length=0.0,
                 min_area=0.0, length_unit=u'm', area_unit=u'm2'):
        """
        Args:
            information (dict of unicode): The PLR record's information (multilingual).
            theme (pyramid_oereb.lib.records.theme.ThemeRecord): The theme to which the PLR belongs to.
            law_status (pyramid_oereb.lib.records.law_status.LawStatusRecord): The law status of this record.
            published_from (datetime.date): Date from/since when the PLR record is published.
            responsible_office (pyramid_oereb.lib.records.office.OfficeRecord): Office which is responsible
                for this PLR.
            symbol (pyramid_oereb.lib.records.image.ImageRecord): Symbol of the restriction defined for the
                legend entry
            view_service (pyramid_oereb.lib.records.view_service.ViewServiceRecord): The view service instance
                associated with this record.
            geometries (list of pyramid_oereb.lib.records.geometry.GeometryRecord): List of geometry records
                associated with this record.
            sub_theme (unicode): Optional subtopic.
            other_theme (unicode): Optional additional topic.
            type_code (unicode): The PLR record's type code (also used by view service).
            type_code_list (unicode): URL to the PLR's list of type codes.
            basis (list of PlrRecord): List of PLR records as basis for this record.
            refinements (list of PlrRecord): List of PLR records as refinement of this record.
            documents (list of pyramid_oereb.lib.records.documents.DocumentBaseRecord): List of documents
                associated with this record.
            info (dict or None): The information read from the config.
            min_length (float): The threshold for area calculation.
            min_area (float): The threshold for area calculation.
            length_unit (unicode): The threshold for area calculation.
            area_unit (unicode): The threshold for area calculation.
        """
        super(PlrRecord, self).__init__(theme)

        if not isinstance(information, dict):
            warnings.warn('Type of "information" should be "dict"')

        assert isinstance(geometries, list)
        assert len(geometries) > 0

        self.information = information
        self.law_status = law_status
        self.published_from = published_from
        self.responsible_office = responsible_office
        self.sub_theme = sub_theme
        self.other_theme = other_theme
        self.type_code = type_code
        self.type_code_list = type_code_list
        self.view_service = view_service
        if basis is None:
            self.basis = []
        else:
            self.basis = basis
        if refinements is None:
            self.refinements = []
        else:
            self.refinements = refinements
        if documents is None:
            self.documents = []
        else:
            self.documents = documents
        if geometries is None:
            self.geometries = []
        else:
            self.geometries = geometries
        self.info = info
        self.has_data = True
        self.min_length = min_length
        self.min_area = min_area
        self.area_unit = area_unit
        self.length_unit = length_unit
        self._area = None
        self._length = None
        self.symbol = symbol

    @property
    def published(self):
        """bool: True if PLR is published."""
        return not self.published_from > datetime.now().date()

    def _sum_length(self):
        """
        Returns:
            float: The summed length.
        """
        lengths_to_sum = []
        for geometry in self.geometries:
            if geometry.length:
                lengths_to_sum.append(geometry.length)
        return sum(lengths_to_sum) if len(lengths_to_sum) > 0 else None

    def _sum_area(self):
        """
        Returns:
            float: The summed area.
        """
        areas_to_sum = []
        for geometry in self.geometries:
            if geometry.area:
                areas_to_sum.append(geometry.area)
        return sum(areas_to_sum) if len(areas_to_sum) > 0 else None

    @property
    def area(self):
        """
        Returns:
            float or None: Returns the summed area of all related geometry records of this PLR.
        """
        return self._area

    @property
    def length(self):
        """
        Returns:
            float or None: Returns the summed length of all related geometry records of this PLR.
        """
        return self._length

    def calculate(self, real_estate):
        tested_geometries = []
        inside = False
        for geometry in self.geometries:
            if geometry.calculate(
                    real_estate,
                    self.min_length, self.min_area,
                    self.length_unit, self.area_unit
            ):
                tested_geometries.append(geometry)
                inside = True
        self.geometries = tested_geometries
        length = self._sum_length()
        if length is None:
            self._length = None
        else:
            self._length = int(round(length, 0))
        area = self._sum_area()
        if area is None:
            self._area = None
            self.part_in_percent = None
        else:
            self._area = int(round(area, 0))
            self.part_in_percent = round(
                ((float(self._area) / float(real_estate.land_registry_area)) * 100),
                1
            )
        return inside

    def __str__(self):
        return '<{} -- type_code: {} theme: {} information: {}'\
                    ' (further attributes not shown)>'\
                    .format(self.__class__.__name__, self.type_code, self.theme,
                            self.information)
