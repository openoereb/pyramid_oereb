# -*- coding: utf-8 -*-
from pyramid.httpexceptions import HTTPBadRequest
from shapely.geometry import Point

from pyramid_oereb import route_prefix
from pyreproj import Reprojector


class PlrWebservice(object):
    def __init__(self, request):
        """
        This class provides the PLR webservice methods.
        :param request: The pyramid request instance.
        :type request:  pyramid.request.Request or pyramid.testing.DummyRequest
        """
        self._request_ = request

    def get_versions(self):
        """
        Returns the available versions of this service.
        :return: The available service versions.
        :rtype:  dict
        """
        endpoint = self._request_.application_url
        if route_prefix:
            endpoint += '/' + route_prefix  # pragma: no cover
        return {
            u'supportedVersion': [
                {
                    u'version': u'1.0.0',
                    u'serviceEndpointBase': unicode(endpoint)
                }
            ]
        }

    def get_capabilities(self):
        """
        Returns the capabilities of this service.
        :return: The service capabilities.
        :rtype:  dict
        """
        from pyramid_oereb import config_reader, municipality_reader
        return {
            u'topic': config_reader.get_topic(),
            u'municipality': [record.fosnr for record in municipality_reader.read()],
            u'flavour': config_reader.get_flavour(),
            u'language': config_reader.get_language(),
            u'crs': config_reader.get_crs()
        }

    def get_egrid_coord(self):
        """
        Returns a list with the matched EGRIDs for the given coordinates.
        :return: The matched EGRIDs.
        :rtype:  list of dict
        """
        from pyramid_oereb import config_reader
        xy = self._request_.params.get('XY')
        gnss = self._request_.params.get('GNSS')
        if xy or gnss:
            from pyramid_oereb import real_estate_reader
            geom_wkt = 'SRID={0};{1}'
            if xy:
                geom_wkt = geom_wkt.format(config_reader.get('srid'), __parse_xy__(xy, buffer_dist=1.0).wkt)
            elif gnss:
                geom_wkt = geom_wkt.format(config_reader.get('srid'), __parse_gnss__(gnss).wkt)
            records = real_estate_reader.read(**{'geometry': geom_wkt})
            return __get_egrid_response__(records)
        else:
            raise HTTPBadRequest('XY or GNSS must be defined.')

    def get_egrid_ident(self):
        """
        Returns a list with the matched EGRIDs for the given NBIdent and property number.
        :return: The matched EGRIDs.
        :rtype:  list of dict
        """
        identdn = self._request_.matchdict.get('identdn')
        number = self._request_.matchdict.get('number')
        if identdn and number:
            from pyramid_oereb import real_estate_reader
            records = real_estate_reader.read(**{
                'nb_ident': identdn,
                'number': number
            })
            return __get_egrid_response__(records)
        else:
            raise HTTPBadRequest('IDENTDN and NUMBER must be defined.')

    def get_egrid_address(self):
        """
        Returns a list with the matched EGRIDs for the given postal address.
        :return: The matched EGRIDs.
        :rtype:  list of dict
        """
        postalcode = self._request_.matchdict.get('postalcode')
        localisation = self._request_.matchdict.get('localisation')
        number = self._request_.matchdict.get('number')
        if postalcode and localisation and number:
            # TODO: Collect the EGRIDs using the property source
            return []
        else:
            raise HTTPBadRequest('POSTALCODE, LOCALISATION and NUMBER must be defined.')

    def get_extract_by_id(self):
        """
        Returns the extract in the specified format and flavour.
        :return: The requested extract.
        :rtype:  dict
        """
        params = self.__validate_extract_params__()
        return params  # TODO: Replace with extract

    def __validate_extract_params__(self):
        """
        Validates the input parameters for get_extract_by_id.
        :return: The validated parameters.
        :rtype: dict
        """

        # Check flavour
        extract_flavour = self._request_.matchdict.get('flavour').lower()
        if extract_flavour not in ['reduced', 'full', 'signed', 'embeddable']:
            raise HTTPBadRequest('Invalid flavour: {0}'.format(extract_flavour))

        # Check format
        extract_format = self._request_.matchdict.get('format').lower()
        if extract_format not in ['pdf', 'xml', 'json']:
            raise HTTPBadRequest('Invalid format: {0}'.format(extract_format))

        # With geometry?
        with_geometry = False
        if self._request_.matchdict.get('param1').lower() == 'geometry':
            with_geometry = True

        # Check for invalid combinations
        if extract_flavour in ['full', 'signed'] and extract_format != 'pdf':
            raise HTTPBadRequest('The flavours full and signed are only available for format PDF.')
        if extract_flavour == 'embeddable' and extract_format == 'pdf':
            raise HTTPBadRequest('The flavour embeddable is not available for format PDF.')
        if extract_format == 'pdf' and with_geometry:
            raise HTTPBadRequest('Geometry is not available for format PDF.')

        # With images?
        with_images = self._request_.params.get('WITHIMAGES') is not None

        params = {
            'flavour': extract_flavour,
            'format': extract_format,
            'geometry': with_geometry,
            'images': with_images
        }

        # Get id
        if with_geometry:
            id_param_1 = 'param2'
            id_param_2 = 'param3'
        else:
            id_param_1 = 'param1'
            id_param_2 = 'param2'
        id_part_1 = self._request_.matchdict.get(id_param_1)
        id_part_2 = self._request_.matchdict.get(id_param_2)
        if id_part_2:
            params.update({'identdn': id_part_1, 'number': id_part_2})
        else:
            params.update({'egrid': id_part_1})

        # Language
        language = self._request_.params.get('LANG')
        if language:
            params.update({'language': language})

        # Topics
        topics = self._request_.params.get('TOPICS')
        if topics:
            params.update({'topics': topics.split(',')})

        return params


def __get_egrid_response__(records):
    """
    Creates a valid GetEGRID response from a list of real estate records.
    :param records: List of real estate records.
    :type records: list of pyramid_oereb.lib.records.real_estate.RealEstateRecord
    :return: Valid GetEGRID response.
    :rtype: list of dict
    """
    response = list()
    for r in records:
        response.append({
            'egrid': getattr(r, 'egrid'),
            'number': getattr(r, 'number'),
            'identDN': getattr(r, 'identdn')
        })
    return response


def __coord_transform__(coord, source_crs):
    """
    Transforms the specified coordinates from the specified CRS to the configured target CRS and creates a
    point geometry.
    :param coord: The coordinates to transform (x, y).
    :type coord: tuple
    :param source_crs: The source CRS
    :type source_crs: int or str
    :return: The transformed coordinates as Point.
    :rtype: shapely.geometry.Point or shapely.geometry.Polygon
    """
    from pyramid_oereb import config_reader
    epsg = 'epsg:{0}'
    srid = config_reader.get('srid')
    rp = Reprojector()
    x, y = rp.transform(coord, from_srs=epsg.format(source_crs), to_srs=epsg.format(srid))
    return Point(x, y)


def __parse_xy__(xy, buffer_dist=None):
    """
    Parses the coordinates from the XY parameter, transforms them to target CRS and creates a point geometry.
    If a buffer distance is defined, a buffer with the specified distance will be applied.
    :param xy: XY parameter from the getegrid request.
    :type xy: str
    :param buffer_dist: Distance for the buffer applied to the transformed point.
                        If None, no buffer will be applied.
    :type buffer_dist: float or None
    :return: The transformed coordinates as Point.
    :rtype: shapely.geometry.Point or shapely.geometry.Polygon
    """
    coords = xy.split(',')
    x = float(coords[0])
    y = float(coords[1])
    src_crs = 21781
    if x > 1000000 and y > 1000000:
        src_crs = 2056
    p = __coord_transform__((x, y), src_crs)
    if buffer_dist:
        return p.buffer(buffer_dist)
    else:
        return p


def __parse_gnss__(gnss):
    """
    Parses the coordinates from the GNSS parameter, transforms them to target CRS and creates a Point with a
    1 meter buffer.
    :param gnss: GNSS parameter from the getegrid request.
    :type gnss: str
    :return: The transformed coordinates as Point.
    :rtype: shapely.geometry.Point or shapely.geometry.Polygon
    """
    coords = gnss.split(',')
    x = float(coords[0])
    y = float(coords[1])
    return __coord_transform__((x, y), 4326).buffer(1.0)
