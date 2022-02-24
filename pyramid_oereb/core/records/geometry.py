# -*- coding: utf-8 -*-
import logging
from datetime import datetime

from shapely.ops import linemerge, cascaded_union

from shapely.geometry import Point, MultiPoint, LineString, Polygon, GeometryCollection, MultiLineString, \
    MultiPolygon

log = logging.getLogger(__name__)


class GeometryRecord(object):
    """
    Geometry record

    Attributes:
        law_status (pyramid_oereb.lib.records.law_status.LawStatusRecord): The law status of this record.
        published_from (datetime.date): Date from/since when the PLR record is published.
        published_until (datetime.date): Date until the PLR record is published.
        geom (Point or LineString or Polygon): The geometry which must be of type POINT, LINESTRING
            or POLYGON, everything else will raise an error.
        geo_metadata (uri): The metadata.
        public_law_restriction (pyramid_oereb.lib.records.plr.PlrRecord): The public law restriction
        calculated (boole): True if there was an access on property before calculation was done.

    Raises:
        AttributeError: Error when a wrong geometry type was passed.
    """
    def __init__(
            self, law_status, published_from, published_until, geom, geo_metadata=None,
            public_law_restriction=None):
        """
        Args:
            law_status (pyramid_oereb.lib.records.law_status.LawStatusRecord): The law status of this record.
            published_from (datetime.date): Date from/since when the PLR record is published.
            published_until (datetime.date): Date until the PLR record is published.
            geom (Point or LineString or Polygon):
            The geometry which must be of type POINT, LINESTRING or POLYGON, everything else
                will raise an error.
            geo_metadata (uri): The metadata.
            public_law_restriction (pyramid_oereb.lib.records.plr.PlrRecord): The public law
                restriction
        """
        self.law_status = law_status
        self.published_from = published_from
        self.published_until = published_until
        self.geo_metadata = geo_metadata
        if isinstance(geom, (Point, MultiPoint, LineString, Polygon)):
            self.geom = geom
        else:
            raise AttributeError(u'The passed geometry is not supported: {type}'.format(type=geom.type))
        self.public_law_restriction = public_law_restriction
        self._units = None
        self._area_share = None
        self._length_share = None
        self._nr_of_points = None
        self._test_passed = False
        self.calculated = False

    @property
    def published(self):
        """
        Returns:
            bool: True if geometry is published.
        """
        if self.published_until is None:
            return self.published_from <= datetime.now().date()
        else:
            return self.published_from <= datetime.now().date() and \
                   self.published_until >= datetime.now().date()

    @staticmethod
    def geom_dim(geom):
        """
        Returns the topological dimension of the specified geometry.

        Args:
            geom (shapely.geometry.base.BaseGeometry): The geometry to be evaluated.

        Returns:
            int: The geometry's topological dimension.
        """
        if isinstance(geom, Point) or isinstance(geom, MultiPoint):
            return 0
        if isinstance(geom, LineString) or isinstance(geom, MultiLineString):
            return 1
        if isinstance(geom, Polygon) or isinstance(geom, MultiPolygon):
            return 2
        if isinstance(geom, GeometryCollection):
            return 3
        else:
            return -1

    @property
    def dim(self):
        """
        Returns:
            int: The topological dimension.
        """
        return self.geom_dim(self.geom)

    def _extract_collection(self, result):
        """
        Extracts all geometries with the same topological dimension as the input geometry from a collection.

        Args:
            result (shapely.geometry.base.BaseGeometry): The intersection result.

        Returns:
            shapely.geometry.base.BaseGeometry: The extracted geometries with matching topological dimension.
        """
        if isinstance(result, GeometryCollection):
            matching_geometries = list()
            for part in result:
                if self.geom_dim(part) == self.dim:
                    matching_geometries.append(part)
            if self.dim == 0:
                points = list()
                for geom in matching_geometries:
                    if isinstance(geom, Point):
                        points.append(geom)
                    elif isinstance(geom, MultiPoint):
                        points.extend(geom.geoms)
                return MultiPoint(points)
            elif self.dim == 1:
                return linemerge(matching_geometries)
            elif self.dim == 2:
                return cascaded_union(matching_geometries)
        else:
            return result

    def calculate(self, real_estate, min_length, min_area, length_unit, area_unit, geometry_types):
        """
        Entry method for calculation. It checks if the geometry type of this instance is a geometry
        collection which has to be unpacked first in case of collection.

        Args:
            real_estate (pyramid_oereb.lib.records.real_estate.RealEstateRecord): The real estate record.
            min_length (float): The threshold to consider or not a line element.
            min_area (float): The threshold to consider or not a surface element.
            length_unit (unicode): The thresholds unit for area calculation.
            area_unit (unicode): The thresholds unit for area calculation.
            geometry_types (dict): The allowed geometry types for the to match the simple feature
                types point, line, polygon

        Returns:
            bool: True if intersection fits the limits.
        """
        line_types = geometry_types.get('line').get('types')
        polygon_types = geometry_types.get('polygon').get('types')
        point_types = geometry_types.get('point').get('types')
        if self.published:
            intersection = self.geom.intersection(real_estate.limit)
            if not intersection.is_empty:
                result = self._extract_collection(intersection)
                if self.geom.type not in point_types + line_types + polygon_types:
                    supported_types = ', '.join(point_types + line_types + polygon_types)
                    raise AttributeError(
                        u'The passed geometry is not supported: {type}. It should be one of: {types}'.format(
                            type=self.geom.type, types=supported_types
                        )
                    )
                elif self.geom.type in point_types:
                    if result.type == point_types[1]:
                        # If it is a multipoint make a list and count the number of elements in the list
                        self._nr_of_points = len(list(result.geoms))
                        self._test_passed = True
                    elif result.type == point_types[0]:
                        # If it is a single point the number of points is one
                        self._nr_of_points = 1
                        self._test_passed = True
                elif self.geom.type in line_types and result.type in line_types:
                    self._units = length_unit
                    length_share = result.length
                    if length_share >= min_length:
                        self._length_share = length_share
                        self._test_passed = True
                elif self.geom.type in polygon_types and result.type in polygon_types:
                    self._units = area_unit
                    area_share = result.area
                    compensated_area = area_share / real_estate.areas_ratio
                    if compensated_area >= min_area:
                        self._area_share = compensated_area
                        self._test_passed = True
                else:
                    # This intersection result should not be used for the OEREB extract:
                    # for example, if two polygons are touching each other, the intersection geometry will be
                    # the point or linestring representing the touching part.
                    log.debug(
                        u'Intersection result changed geometry type. '
                        u'Original geometry was {0} and result is {1}'.format(
                            self.geom.type,
                            result.type
                        )
                    )
        self.calculated = True
        return self._test_passed

    @property
    def area_share(self):
        """
        Returns:
            float or None: the area of this geometry.
        """
        if not self.calculated:
            log.warning(u'There was an access on property "area_share" before calculation was done.')
        return self._area_share

    @property
    def length_share(self):
        """
        Returns:
            float or None: the length of this geometry.
        """
        if not self.calculated:
            log.warning(u'There was an access on property "length_share" before calculation was done.')
        return self._length_share

    @property
    def nr_of_points(self):
        """
        Returns:
            float or None: the total amount of points/this geometry.
        """
        if not self.calculated:
            log.warning(u'There was an access on property "nr_of_points" before calculation was done.')
        return self._nr_of_points
