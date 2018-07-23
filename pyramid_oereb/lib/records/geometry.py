# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from pyramid_oereb.lib.config import Config
from shapely.geometry import Point, MultiPoint, LineString, Polygon

log = logging.getLogger(__name__)


class GeometryRecord(object):
    """
    Geometry record

    Args:
        law_status (pyramid_oereb.lib.records.law_status.LawStatusRecord): The law status of this record.
        published_from (datetime.date): Date from/since when the PLR record is published.
        geom (Point or LineString or Polygon):
            The geometry which must be of type POINT, LINESTRING or POLYGON, everything else
             will raise an error.
        geo_metadata (uri): The metadata.
        public_law_restriction (pyramid_oereb.lib.records.plr.PlrRecord): The public law
            restriction
        office (pyramid_oereb.lib.records.office.Office): The office

    Raises:
        AttributeError: Error when a wrong geometry type was passed.
    """
    def __init__(
            self, law_status, published_from, geom, geo_metadata=None, public_law_restriction=None,
            office=None):

        self.law_status = law_status
        self.published_from = published_from
        self.geo_metadata = geo_metadata
        if isinstance(geom, (Point, MultiPoint, LineString, Polygon)):
            self.geom = geom
        else:
            raise AttributeError(u'The passed geometry is not supported: {type}'.format(type=geom.type))
        self.public_law_restriction = public_law_restriction
        self.office = office
        self._units = None
        self._area_share = None
        self._length_share = None
        self._nr_of_points = None
        self._test_passed = False
        self.calculated = False

    @property
    def published(self):
        """bool: True if geometry is published."""
        return not self.published_from > datetime.now().date()

    def calculate(self, real_estate, min_length, min_area, length_unit, area_unit):
        """
        Entry method for calculation. It checks if the geometry type of this instance is a geometry
        collection which has to be unpacked first in case of collection.

        Args:
            real_estate (pyramid_oereb.lib.records.real_estate.RealEstateRecord): The real estate record.
            min_length (float): The threshold to consider or not a line element.
            min_area (float): The threshold to consider or not a surface element.
            length_unit (unicode): The thresholds unit for area calculation.
            area_unit (unicode): The thresholds unit for area calculation.

        Returns:
            bool: True if intersection fits the limits.
        """
        geometry_types = Config.get('geometry_types')
        line_types = geometry_types.get('line').get('types')
        polygon_types = geometry_types.get('polygon').get('types')
        point_types = geometry_types.get('point').get('types')
        if self.published:
            result = self.geom.intersection(real_estate.limit)
            # differentiate between Points and MultiPoint
            if result.type == point_types[1]:
                # If it is a multipoint make a list and count the number of elements in the list
                self._nr_of_points = len(list(result.geoms))
                self._test_passed = True
            elif result.type == point_types[0]:
                # If it is a single point the number of points is one
                self._nr_of_points = 1
                self._test_passed = True
            elif self.geom.type in line_types:
                self._units = length_unit
                length_share = result.length
                if length_share >= min_length:
                    self._length_share = length_share
                    self._test_passed = True
            elif self.geom.type in polygon_types:
                self._units = area_unit
                area_share = result.area
                compensated_area = area_share / real_estate.areas_ratio
                if compensated_area >= min_area:
                    self._area_share = compensated_area
                    self._test_passed = True
            else:
                    # TODO: configure a proper error message
                    log.error('Unknown geometry type')
        self.calculated = True
        return self._test_passed

    @property
    def area_share(self):
        """
        float or None: Returns the area of this geometry.
        """
        if not self.calculated:
            log.warning(u'There was an access on property "area_share" before calculation was done.')
        return self._area_share

    @property
    def length_share(self):
        """
        float or None: Returns the length of this geometry.
        """
        if not self.calculated:
            log.warning(u'There was an access on property "length_share" before calculation was done.')
        return self._length_share

    @property
    def nr_of_points(self):
        """
        float or None: Returns the number of this geometry.
        """
        if not self.calculated:
            log.warning(u'There was an access on property "nr_of_points" before calculation was done.')
        return self._nr_of_points
