# -*- coding: utf-8 -*-
from datetime import datetime
from pyramid_oereb.lib.config import Config


class GeometryRecord(object):

    def __init__(
            self, legal_state, published_from, geom, geo_metadata=None, public_law_restriction=None,
            office=None):
        """
        Geometry record

        Args:
            legal_state (unicode): The PLR record's legal state.
            published_from (datetime.date): Date from/since when the PLR record is published.
            geom (shapely.geometry.base.BaseGeometry): The geometry
            geo_metadata (uri): The metadata.
            public_law_restriction (pyramid_oereb.lib.records.plr.PlrRecord): The public law
                restriction
            office (pyramid_oereb.lib.records.office.Office): The office
        """

        self.legal_state = legal_state
        self.published_from = published_from
        self.geo_metadata = geo_metadata
        self.geom = geom
        self.public_law_restriction = public_law_restriction
        self.office = office
        self._units = None
        self._area = None
        self._length = None
        self._part_in_percent = None
        self._test_passed = False

    @property
    def published(self):
        """bool: True if geometry is published."""
        return not self.published_from > datetime.now().date()

    @staticmethod
    def _is_multi_geometry(geometry):
        # TODO: Make this read from config singleton provided by sbrunner
        multi_geometry_types = ['MultiPoint', 'MultiLineString', 'MultiPolygon', 'GeometryCollection']
        if geometry.type in multi_geometry_types:
            return True
        else:
            return False

    @staticmethod
    def _sum_multi_line_length(multi_line, limit=0.0):
        """

        Args:
            multi_line (shapely.geometry.MultiLineString): The multi line string which parts
                should be summed.
            limit (float): The cutting limit which is sorting parts.

        Returns:
            float: The summed length.
        """
        lengths_to_sum = []
        for part in multi_line.geoms:
            length = part.length
            if length > limit:
                lengths_to_sum.append(length)
        return sum(lengths_to_sum)

    @staticmethod
    def _sum_multi_polygon_area(multi_polygon, limit=0.0):
        """

        Args:
            multi_polygon (shapely.geometry.MultiPolygon): The multi line string which parts
                should be summed.
            limit (float): The cutting limit which is sorting parts.

        Returns:
            float: The summed area.
        """
        areas_to_sum = []
        for part in multi_polygon.geoms:
            area = part.area
            if area > limit:
                areas_to_sum.append(area)
        return sum(areas_to_sum)

    # TODO: Make this read from config singleton provided by sbrunner
    def calculate(self, real_estate, plr_thresholds):
        """
        Calculates intersection area and checks if it fits the configured limits.

        Args:
            real_estate (pyramid_oereb.lib.records.real_estate.RealEstateRecord): The real
                estate record.
            plr_thresholds (dict): The configured limits.

        Returns:
            bool: True if intersection fits the limits.
        """
        geometry_types = Config.get('geometry_types')
        point_types = geometry_types.get('point').get('types')
        line_types = geometry_types.get('line').get('types')
        polygon_types = geometry_types.get('polygon').get('types')
        min_length = plr_thresholds.get('min_length')
        min_area = plr_thresholds.get('min_area')
        if self.geom.type in point_types:
            pass
        else:
            result = self.geom.intersection(real_estate.limit)
            if self.geom.type in line_types:
                # TODO: load this from config
                self._units = 'm'
                if self._is_multi_geometry(result):
                    length = self._sum_multi_line_length(result)
                else:
                    length = result.length
                if length > min_length:
                    self._length = length
                    self._test_passed = True
            elif self.geom.type in polygon_types:
                # TODO: load this from config
                self._units = 'm2'
                if self._is_multi_geometry(result):
                    area = self._sum_multi_polygon_area(result)
                else:
                    area = result.area
                compensated_area = area * real_estate.areas_ratio
                if compensated_area > min_area:
                    self._area = compensated_area
                    self._part_in_percent = round(((compensated_area / real_estate.limit.area) * 100), 1)
                    self._test_passed = True
            else:
                # TODO: configure a proper error message
                print 'Error: unknown geometry type'
        return self._test_passed
