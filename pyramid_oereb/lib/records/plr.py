# -*- coding: utf-8 -*-
import warnings
from datetime import datetime


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

    # Attributes added or calculated by the processor
    area = None
    """decimal: Area of the restriction touching the property calculated by the processor."""

    part_in_percent = None
    """decimal: Part of the property area touched by the restriction in percent."""

    def __init__(self, theme, content, legal_state, published_from, responsible_office, symbol, subtopic=None,
                 additional_topic=None, type_code=None, type_code_list=None, view_service=None, basis=None,
                 refinements=None, documents=None, geometries=None, info=None, min_length=0.0,
                 min_area=0.0, length_unit=u'm', area_unit=u'm2', length_precision=2, area_precision=2,
                 percentage_precision=1):
        """
        Public law restriction record.

        Args:
            content (dict of unicode): The PLR record's content (multilingual).
            theme (pyramid_oereb.lib.records.theme.ThemeRecord): The theme to which the PLR belongs to.
            legal_state (unicode): The PLR record's legal state.
            published_from (datetime.date): Date from/since when the PLR record is published.
            responsible_office (pyramid_oereb.lib.records.office.OfficeRecord): Office which is responsible
                for this PLR.
            symbol (pyramid_oereb.lib.records.image.ImageRecord): Symbol of the restriction defined for the
                legend entry
            subtopic (unicode): Optional subtopic.
            additional_topic (unicode): Optional additional topic.
            type_code (unicode): The PLR record's type code (also used by view service).
            type_code_list (unicode): URL to the PLR's list of type codes.
            view_service (pyramid_oereb.lib.records.view_service.ViewServiceRecord): The view service instance
                associated with this record.
            basis (list of PlrRecord): List of PLR records as basis for this record.
            refinements (list of PlrRecord): List of PLR records as refinement of this record.
            documents (list of pyramid_oereb.lib.records.documents.DocumentBaseRecord): List of documents
                associated with this record.
            geometries (list of pyramid_oereb.lib.records.geometry.GeometryRecord): List of geometry records
                associated with this record.
            info (dict or None): The information read from the config.
            min_length (float): The threshold for area calculation.
            min_area (float): The threshold for area calculation.
            length_unit (unicode): The threshold for area calculation.
            area_unit (unicode): The threshold for area calculation.
            length_precision (int): The precision how the length results will be rounded.
            area_precision (int): The precision how the area results will be rounded.
            percentage_precision (int): The precision how the percentage results will be rounded.
        """
        super(PlrRecord, self).__init__(theme)

        if not isinstance(content, dict):
            warnings.warn('Type of "content" should be "dict"')

        self.content = content
        self.legal_state = legal_state
        self.published_from = published_from
        self.responsible_office = responsible_office
        self.subtopic = subtopic
        self.additional_topic = additional_topic
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
        self.length_precision = length_precision
        self.area_precision = area_precision
        self.percentage_precision = percentage_precision
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
                length = geometry.length
                if length > self.min_length:
                    lengths_to_sum.append(length)
        return sum(lengths_to_sum)

    def _sum_area(self):
        """
        Returns:
            float: The summed area.
        """
        areas_to_sum = []
        for geometry in self.geometries:
            if geometry.area:
                area = geometry.area
                if area > self.min_area:
                    areas_to_sum.append(area)
        return sum(areas_to_sum)

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
            if geometry.calculate(real_estate, self.min_length, self.min_area, self.length_unit,
                                  self.area_unit):
                tested_geometries.append(geometry)
                inside = True
        self.geometries = tested_geometries
        self._length = round(self._sum_length(), self.length_precision)
        self._area = round(self._sum_area(), self.area_precision)
        self.part_in_percent = round(((self._area / real_estate.limit.area) * 100), self.percentage_precision)
        return inside
