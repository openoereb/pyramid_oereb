# -*- coding: utf-8 -*-


class GeometryRecord(object):

    def __init__(
            self, legal_state, published_from, geom, geo_metadata=None, public_law_restriction=None,
            office=None):
        """
        Geometry record
        :param legal_state: The PLR record's legal state.
        :type legal_state: str
        :param published_from: Date from/since when the PLR record is published.
        :type published_from: datetime.date
        :param geom: The geometry
        :type geom: shapely.geometry.base.BaseGeometry
        :param geo_metadata: The metadata
        :type geo_metadata: str
        :param public_law_restriction: The public law restriction
        :type public_law_restriction: pyramid_oereb.lib.records.plr.PlrRecord
        :param office: The office
        :type office: pyramid_oereb.lib.records.office.Office
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

    @classmethod
    def get_fields(cls):
        """
        Returns a list of available field names.
        :return: List of available field names.
        :rtype: list of str
        """
        return [
            'legal_state',
            'published_from',
            'geo_metadata',
            'geom',
            'public_law_restriction',
            'office'
        ]

    def to_extract(self):
        """
        Returns a dictionary with all available values needed for the extract.
        :return: Dictionary with values for the extract.
        :rtype: dict
        """
        extract = dict()
        for key in [
            'legal_state',
            'geo_metadata',
            'geom'
        ]:
            value = getattr(self, key)
            if value:
                extract[key] = value
        key = 'office'
        record = getattr(self, key)
        if record:
            extract[key] = record.to_extract()
        key = 'geom'
        extract[key] = str(getattr(self, key))
        return extract

    @staticmethod
    def _is_multi_geometry(geometry):
        multi_geometry_types = ['MultiPoint', 'MultiLineString', 'MultiPolygon', 'GeometryCollection']
        if geometry.type in multi_geometry_types:
            return True
        else:
            return False

    @staticmethod
    def _sum_multi_line_length(multi_line, limit=0.0):
        """

        :param multi_line: The multi line string which parts should be summed.
        :type multi_line: shapely.geometry.MultiLineString
        :param limit: The cutting limit which is sorting parts.
        :type limit: float
        :return: The summed length.
        :rtype: float
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

        :param multi_polygon: The multi line string which parts should be summed.
        :type multi_polygon: shapely.geometry.MultiPolygon
        :param limit: The cutting limit which is sorting parts.
        :type limit: float
        :return: The summed area.
        :rtype: float
        """
        areas_to_sum = []
        for part in multi_polygon.geoms:
            area = part.area
            if area > limit:
                areas_to_sum.append(area)
        return sum(areas_to_sum)

    # TODO: Make this read from config singleton provided by sbrunner
    def calculate(self, real_estate, plr_limits):
        point_types = plr_limits.get('point').get('types')
        line_types = plr_limits.get('line').get('types')
        min_length = plr_limits.get('line').get('min_length')
        polygon_types = plr_limits.get('polygon').get('types')
        min_area = plr_limits.get('polygon').get('min_area')
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
