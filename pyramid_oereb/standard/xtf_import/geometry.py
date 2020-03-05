# -*- coding: utf-8 -*-
import logging

from geoalchemy2.shape import from_shape
from pyreproj import Reprojector
from shapely.geometry import MultiPoint, MultiLineString, MultiPolygon, GeometryCollection, Point, \
    LineString, Polygon

from pyramid_oereb.standard.xtf_import.util import parse_string, parse_ref, get_tag, stroke_arc


class Geometry(object):

    TAG_POINT_LV03 = 'Punkt_LV03'
    TAG_POINT_LV95 = 'Punkt_LV95'
    TAG_LINE_LV03 = 'Linie_LV03'
    TAG_LINE_LV95 = 'Linie_LV95'
    TAG_AREA_LV03 = 'Flaeche_LV03'
    TAG_AREA_LV95 = 'Flaeche_LV95'
    TAG_LAW_STATUS = 'Rechtsstatus'
    TAG_PUBLISHED_FROM = 'publiziertAb'
    TAG_GEO_METADATA = 'MetadatenGeobasisdaten'
    TAG_PUBLIC_LAW_RESTRICTION = 'Eigentumsbeschraenkung'
    TAG_RESPONSIBLE_OFFICE = 'ZustaendigeStelle'
    TAG_COORD = 'COORD'
    TAG_ARC = 'ARC'

    def __init__(self, session, model, geometry_type, srid, arc_max_diff=0.001, arc_precision=3):
        self._session = session
        self._model = model
        self._geometry_type = geometry_type
        self._to_srs = srid
        self._arc_max_diff = arc_max_diff
        self._arc_precision = arc_precision
        self._log = logging.getLogger('import_federal_topic')
        self._reprojector = Reprojector()

    def parse(self, geometry):  # pragma: no cover
        instance = self._model(
            id=geometry.attrib['TID'],
            law_status=parse_string(geometry, self.TAG_LAW_STATUS),
            published_from=parse_string(geometry, self.TAG_PUBLISHED_FROM),
            geo_metadata=parse_string(geometry, self.TAG_GEO_METADATA),
            public_law_restriction_id=parse_ref(geometry, self.TAG_PUBLIC_LAW_RESTRICTION),
            office_id=parse_ref(geometry, self.TAG_RESPONSIBLE_OFFICE),
            geom=self._parse_geom(geometry)
        )
        self._session.add(instance)

    def _parse_geom(self, geometry):
        geom_type = self._geometry_type.upper()
        geom = None

        # Check for LV95 geometry
        for element in geometry:
            tag = get_tag(element)
            if tag == self.TAG_POINT_LV95:
                geom = self._parse_point(element, 2056)
            elif tag == self.TAG_LINE_LV95:
                geom = self._parse_line(element, 2056)
            elif tag == self.TAG_AREA_LV95:
                geom = self._parse_area(element, 2056)

        # Check for LV03 geometry as fallback
        if geom is None:
            for element in geometry:
                tag = get_tag(element)
                if tag == self.TAG_POINT_LV03:
                    geom = self._parse_point(element, 21781)
                elif tag == self.TAG_LINE_LV03:
                    geom = self._parse_line(element, 21781)
                elif tag == self.TAG_AREA_LV03:
                    geom = self._parse_area(element, 21781)

        # Wrap in collection if necessary
        if geom is not None:
            if geom_type == 'MULTIPOINT':
                geom = MultiPoint([geom])
            elif geom_type == 'MULTILINESTRING':
                geom = MultiLineString([geom])
            elif geom_type == 'MULTIPOLYGON':
                geom = MultiPolygon([geom])
            elif geom_type == 'GEOMETRYCOLLECTION':
                geom = GeometryCollection([geom])

        # Return geometry or None
        return None if geom is None else from_shape(geom, srid=2056)

    def _parse_coord(self, coord, srs):
        p = dict()
        for c in coord:
            if get_tag(c) == 'C1':
                p['x'] = float(c.text)
            elif get_tag(c) == 'C2':
                p['y'] = float(c.text)
        if srs == self._to_srs:
            return p['x'], p['y']
        else:
            return self._reprojector.transform((p['x'], p['y']), from_srs=srs, to_srs=self._to_srs)

    def _parse_point(self, point, srs):
        for coord in point:
            return Point(self._parse_coord(coord, srs))
        return None

    def _parse_line(self, line, srs):
        for polyline in line:
            coords = list()
            for coord in polyline:
                tag = get_tag(coord)
                if tag == self.TAG_COORD:
                    coords.append(self._parse_coord(coord, srs))
                elif tag == self.TAG_ARC:
                    coords.extend(self._parse_arc(coord, coords[-1], srs))
                else:
                    self._log.warning('Found unsupported geometry element: {0}'.format(tag))

            return LineString(coords)
        return None

    def _parse_area(self, area, srs):
        for surface in area:
            boundaries = list()
            for boundary in surface:
                boundaries.append(self._parse_line(boundary, srs))
            exterior = boundaries[0].coords
            if len(boundaries) > 1:
                interiors = [interior.coords for interior in boundaries[1:]]
            else:
                interiors = None
            return Polygon(shell=exterior, holes=interiors)
        return None

    def _parse_arc(self, arc, start_point, srs):
        e = dict()
        a = dict()
        for element in arc:
            tag = get_tag(element)
            if tag == 'C1':
                e['x'] = float(element.text)
            elif tag == 'C2':
                e['y'] = float(element.text)
            elif tag == 'A1':
                a['x'] = float(element.text)
            elif tag == 'A2':
                a['y'] = float(element.text)
        if srs == self._to_srs:
            arc_point = (a['x'], a['y'])
            end_point = (e['x'], e['y'])
        else:
            arc_point = self._reprojector.transform((a['x'], a['y']), from_srs=srs, to_srs=self._to_srs)
            end_point = self._reprojector.transform((e['x'], e['y']), from_srs=srs, to_srs=self._to_srs)
        return stroke_arc(start_point, arc_point, end_point, self._arc_max_diff, self._arc_precision)
