# -*- coding: utf-8 -*-

import logging
import warnings
from datetime import datetime


log = logging.getLogger(__name__)


class EmptyPlrRecord(object):
    """
    Attributes:
        theme (pyramid_oereb.lib.records.theme.ThemeRecord): The theme to which the PLR belongs to.
        has_data (bool): True if the topic contains data.
    """

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
        theme (pyramid_oereb.lib.records.theme.ThemeRecord): The theme to which the PLR belongs to.
        legend_entry (pyramid_oereb.lib.records.view_service.LegendEntryRecord): The PLR record's
            corresponding legend record.
        law_status (pyramid_oereb.lib.records.law_status.LawStatusRecord): The law status of this record.
        published_from (datetime.date): Date from/since when the PLR record is published.
        published_until (datetime.date): Date from when the PLR record is not published anymore.
        responsible_office (pyramid_oereb.lib.records.office.OfficeRecord): Office which is responsible
            for this PLR.
        symbol (pyramid_oereb.lib.records.image.ImageRecord): Symbol of the restriction defined for the
            legend entry
        view_service (pyramid_oereb.lib.records.view_service.ViewServiceRecord): The view service instance
            associated with this record.
        geometries (list of pyramid_oereb.lib.records.geometry.GeometryRecord): List of geometry records
            associated with this record.
        sub_theme (pyramid_oereb.lib.records.theme.ThemeRecord or None): Optional subtopic.
        type_code (unicode): The PLR record's type code (also used by view service).
        type_code_list (unicode): URL to the PLR's list of type codes.
        documents (list of pyramid_oereb.core.records.documents.DocumentBaseRecord): List of documents
            associated with this record.
        info (dict or None): The information read from the config.
        min_length (float): The threshold for area calculation.
        min_area (float): The threshold for area calculation.
        length_unit (unicode): The threshold for area calculation.
        area_unit (unicode): The threshold for area calculation.
        view_service_id (int): The id to the connected view service. This is very important to be able to
        solve bug https://github.com/openoereb/pyramid_oereb/issues/521
    """

    def __init__(self, theme, legend_entry, law_status, published_from, published_until, responsible_office,
                 symbol, view_service, geometries, sub_theme=None, type_code=None,
                 type_code_list=None, documents=None, info=None, min_length=0.0,
                 min_area=0.0, length_unit=u'm', area_unit=u'm2', view_service_id=None):
        """
        Args:
            theme (pyramid_oereb.lib.records.theme.ThemeRecord): The theme to which the PLR belongs to.
            legend_entry (pyramid_oereb.lib.records.view_service.LegendEntryRecord): The PLR record's
                corresponding legend record.
            law_status (pyramid_oereb.lib.records.law_status.LawStatusRecord): The law status of this record.
            published_from (datetime.date): Date from/since when the PLR record is published.
            published_until (datetime.date): Date from when the PLR record is not published anymore.
            responsible_office (pyramid_oereb.lib.records.office.OfficeRecord): Office which is responsible
                for this PLR.
            symbol (pyramid_oereb.lib.records.image.ImageRecord): Symbol of the restriction defined for the
                legend entry
            view_service (pyramid_oereb.lib.records.view_service.ViewServiceRecord): The view service instance
                associated with this record.
            geometries (list of pyramid_oereb.lib.records.geometry.GeometryRecord): List of geometry records
                associated with this record.
            sub_theme (pyramid_oereb.lib.records.theme.ThemeRecord or None): Optional subtopic.
            type_code (unicode): The PLR record's type code (also used by view service).
            type_code_list (unicode): URL to the PLR's list of type codes.
            documents (list of pyramid_oereb.core.records.documents.DocumentBaseRecord): List of documents
                associated with this record.
            info (dict or None): The information read from the config.
            min_length (float): The threshold for area calculation.
            min_area (float): The threshold for area calculation.
            length_unit (unicode): The threshold for area calculation.
            area_unit (unicode): The threshold for area calculation.
            view_service_id (int): The id to the connected view service. This is very important to be able to
            solve bug https://github.com/openoereb/pyramid_oereb/issues/521
        """
        super(PlrRecord, self).__init__(theme)

        if not isinstance(legend_entry.legend_text, dict):
            warnings.warn('Type of "legend_text" should be "dict"')

        assert isinstance(geometries, list)
        assert len(geometries) > 0

        self.legend_entry = legend_entry
        self.law_status = law_status
        self.published_from = published_from
        self.published_until = published_until
        self.responsible_office = responsible_office
        self.type_code = type_code
        self.type_code_list = type_code_list
        self.view_service = view_service
        if documents is None:
            self.documents = []
        else:
            self.documents = documents
        self.geometries = geometries
        self.sub_theme = sub_theme
        self.info = info
        self.has_data = True
        self.min_length = min_length
        self.min_area = min_area
        self.area_unit = area_unit
        self.length_unit = length_unit
        self._area_share = None
        self._part_in_percent = None
        self._length_share = None
        self._nr_of_points = None
        self.symbol = symbol
        self.view_service_id = view_service_id

    @property
    def legend_text(self):
        """
        Returns:
            dict of unicode: the legend text
        """
        return self.legend_entry.legend_text

    @property
    def published(self):
        """
        Retruns:
            bool: True if PLR is published.
        """
        if self.published_until is None:
            return self.published_from <= datetime.now().date()
        else:
            return self.published_from <= datetime.now().date() \
                   and self.published_until >= datetime.now().date()

    def _sum_length(self):
        """
        Returns:
            float: The summed length.
        """
        lengths_to_sum = []
        for geometry in self.geometries:
            if geometry.length_share:
                lengths_to_sum.append(geometry.length_share)
        return sum(lengths_to_sum) if len(lengths_to_sum) > 0 else None

    def _sum_area(self):
        """
        Returns:
            float: The summed area.
        """
        areas_to_sum = []
        for geometry in self.geometries:
            if geometry.area_share:
                areas_to_sum.append(geometry.area_share)
        return sum(areas_to_sum) if len(areas_to_sum) > 0 else None

    def _sum_points(self):
        """
        Returns:
            int: The summed number of points of these geometry records.
        """
        points_to_sum = 0
        for geometry in self.geometries:
            if geometry.nr_of_points:
                points_to_sum += geometry.nr_of_points
        return points_to_sum

    @property
    def area_share(self):
        """
        Retruns:
            float or None: the summed area of all related geometry records of this PLR."""
        return self._area_share

    @property
    def part_in_percent(self):
        """
        Retruns:
            decimal or None: (decimal): Part of the property area touched by the restriction in percent."""
        return self._part_in_percent

    @part_in_percent.setter
    def part_in_percent(self, value):
        """
        Args:
            value (decimal): Part of the property area touched by the restriction in percent.
        """
        self._part_in_percent = value

    @property
    def length_share(self):
        """
        Returns:
            float or None: the summed length of all related geometry records of this PLR."""
        return self._length_share

    @property
    def nr_of_points(self):
        """
        Returns:
            float or None: the number of points of all related geometry records of this PLR."""
        return self._nr_of_points

    def calculate(self, real_estate, geometry_types):
        """
        Entry method for calculation. It checks if the geometry type of this instance is a geometry
        collection which has to be unpacked first in case of collection.

        Args:
            real_estate (pyramid_oereb.lib.records.real_estate.RealEstateRecord): The real estate record.
            geometry_types (dict): The allowed geometry types for the to match the simple
            feature types point, line, polygon

        Returns:
            bool: True if intersection fits the limits.
        """
        tested_geometries = []
        inside = False
        for geometry in self.geometries:
            if geometry.published and geometry.calculate(
                    real_estate,
                    self.min_length, self.min_area,
                    self.length_unit, self.area_unit,
                    geometry_types
            ):
                tested_geometries.append(geometry)
                inside = True
        self.geometries = tested_geometries

        # Points
        nr_of_points = self._sum_points()
        self._nr_of_points = nr_of_points if nr_of_points else None
        # Lines
        length_share = self._sum_length()
        if length_share is None:
            self._length_share = None
        else:
            self._length_share = int(round(length_share, 0))
        # Areas
        area_share = self._sum_area()
        if area_share is None:
            self._area_share = None
            self._part_in_percent = None
        else:
            self._area_share = int(round(area_share, 0))
            self._part_in_percent = round(
                ((float(self._area_share) / float(real_estate.land_registry_area)) * 100),
                1
            )
        return inside

    def __str__(self):
        legend_text = dict()
        for key in self.legend_text:
            if self.legend_text[key] is not None:
                legend_text[key] = self.legend_text[key].encode('utf-8')
        tpl = '<{} -- type_code: {} theme: {} legend_text: {} (further attributes not shown)>'
        return tpl.format(self.__class__.__name__, self.type_code, self.theme, legend_text)
