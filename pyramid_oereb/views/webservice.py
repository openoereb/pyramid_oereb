# -*- coding: utf-8 -*-
from pyramid.httpexceptions import HTTPBadRequest, HTTPNoContent, HTTPServerError
from shapely.geometry import Point
from pyramid.renderers import render_to_response
from sqlalchemy.orm.exc import NoResultFound

from pyramid_oereb import route_prefix
from pyramid_oereb.lib.processor import Processor
from pyreproj import Reprojector


class PlrWebservice(object):
    def __init__(self, request):
        """
        This class provides the PLR webservice methods.

        :param request: The pyramid request instance.
        :type request:  pyramid.request.Request or pyramid.testing.DummyRequest
        """
        from pyramid_oereb import config_reader
        if not isinstance(request.pyramid_oereb_processor, Processor):
            raise HTTPServerError('Missing processor instance')
        self._request_ = request
        self._real_estate_reader_ = request.pyramid_oereb_processor.real_estate_reader
        self._municipality_reader_ = request.pyramid_oereb_processor.municipality_reader
        self._config_reader_ = config_reader

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
        themes = list()
        for theme in self._config_reader_.get_themes():
            text = list()
            for k, v in theme.text.iteritems():
                text.append({
                    'Language': k,
                    'Text': v
                })
            themes.append({
                'Code': theme.code,
                'Text': text
            })
        return {
            u'topic': themes,
            u'municipality': [record.fosnr for record in self._municipality_reader_.read()],
            u'flavour': self._config_reader_.get_flavour(),
            u'language': self._config_reader_.get_language(),
            u'crs': self._config_reader_.get_crs()
        }

    def get_egrid_coord(self):
        """
        Returns a list with the matched EGRIDs for the given coordinates.

        :return: The matched EGRIDs.
        :rtype:  list of dict
        """
        xy = self._request_.params.get('XY')
        gnss = self._request_.params.get('GNSS')
        if xy or gnss:
            geom_wkt = 'SRID={0};{1}'
            if xy:
                geom_wkt = geom_wkt.format(self._config_reader_.get('srid'),
                                           self.__parse_xy__(xy, buffer_dist=1.0).wkt)
            elif gnss:
                geom_wkt = geom_wkt.format(self._config_reader_.get('srid'), self.__parse_gnss__(gnss).wkt)
            records = self._real_estate_reader_.read(**{'geometry': geom_wkt})
            return self.__get_egrid_response__(records)
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
            records = self._real_estate_reader_.read(**{
                'nb_ident': identdn,
                'number': number
            })
            return self.__get_egrid_response__(records)
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
        processor = self._request_.pyramid_oereb_processor
        # read the real estate from configured source by the passed parameters
        real_estate_reader = processor.real_estate_reader
        if params.egrid:
            try:
                real_estate_records = real_estate_reader.read(egrid=params.egrid)
            except LookupError:
                raise HTTPNoContent()
        elif params.identdn and params.number:
            try:
                real_estate_records = real_estate_reader.read(
                    nb_ident=params.identdn,
                    number=params.number
                )
            except LookupError:
                raise HTTPNoContent()
        else:
            raise HTTPBadRequest()

        # check if result is strictly one (we queried with primary keys)
        if len(real_estate_records) == 1:
            try:
                extract = processor.process(real_estate_records[0])
            except LookupError:
                raise HTTPNoContent()
            except NotImplementedError:
                raise HTTPServerError()
            except NoResultFound:
                raise HTTPServerError()
            if params.format == 'json':
                return render_to_response(
                    'pyramid_oereb_extract_json',
                    (extract, params),
                    request=self._request_
                )
            elif params.format == 'xml':
                return render_to_response(
                    'pyramid_oereb_extract_xml',
                    (extract, params),
                    request=self._request_
                )
            elif params.format == 'pdf':
                # TODO: implement way to produce pdf
                return render_to_response(
                    'string',
                    'Not implemented by now...',
                    request=self._request_
                )
            else:
                raise HTTPBadRequest()
        else:
            raise HTTPBadRequest()

    def __validate_extract_params__(self):
        """
        Validates the input parameters for get_extract_by_id.

        :return: The validated parameters.
        :rtype: pyramid_oereb.views.webservice.Parameter
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

        params = Parameter(extract_flavour, extract_format, with_geometry, with_images)

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
            params.set_identdn(id_part_1)
            params.set_number(id_part_2)
        else:
            params.set_egrid(id_part_1)

        # Language
        language = str(self._request_.params.get('LANG')).lower()
        if language not in self._config_reader_.get_language():
            raise HTTPBadRequest(
                'Requested language is not available. Following languages are configured: {languages} The '
                'requested language was: {language}'.format(
                    languages=str(self._config_reader_.get_language()),
                    language=language
                )
            )
        if language:
            params.set_language(language)

        # Topics
        topics = self._request_.params.get('TOPICS')
        if topics:
            params.set_topics(topics.split(','))

        return params

    def __coord_transform__(self, coord, source_crs):
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
        epsg = 'epsg:{0}'
        srid = self._config_reader_.get('srid')
        rp = Reprojector()
        x, y = rp.transform(coord, from_srs=epsg.format(source_crs), to_srs=epsg.format(srid))
        return Point(x, y)

    def __get_egrid_response__(self, records):
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

    def __parse_xy__(self, xy, buffer_dist=None):
        """
        Parses the coordinates from the XY parameter, transforms them to target CRS and creates a point
        geometry. If a buffer distance is defined, a buffer with the specified distance will be applied.

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
        p = self.__coord_transform__((x, y), src_crs)
        if buffer_dist:
            return p.buffer(buffer_dist)
        else:
            return p

    def __parse_gnss__(self, gnss):
        """
        Parses the coordinates from the GNSS parameter, transforms them to target CRS and creates a Point with
        a 1 meter buffer.

        :param gnss: GNSS parameter from the getegrid request.
        :type gnss: str
        :return: The transformed coordinates as Point.
        :rtype: shapely.geometry.Point or shapely.geometry.Polygon
        """
        coords = gnss.split(',')
        x = float(coords[0])
        y = float(coords[1])
        return self.__coord_transform__((x, y), 4326).buffer(1.0)


class Parameter(object):
    def __init__(self, flavour, format, geometry, images, identdn=None, number=None, egrid=None,
                 language=None, topics=None):
        """
        Creates a new parameter instance.

        :param flavour: The extract flavour.
        :type flavour: str
        :param format: The extract format.
        :type format: str
        :param geometry: Extract with/without geometry.
        :type geometry: bool
        :param images: Extract with/without images.
        :type images: bool
        :param identdn: The IdentDN as real estate identifier.
        :type identdn: str
        :param number: The parcel number as real estate identifier.
        :type number: str
        :param egrid: The EGRID as real estate identifier.
        :type egrid: str
        :param language: The requested language.
        :type language: str
        :param topics: The list of requested topics.
        :type topics: list of str
        """
        self.__flavour__ = flavour
        self.__format__ = format
        self.__geometry__ = geometry
        self.__images__ = images
        self.__identdn__ = identdn
        self.__number__ = number
        self.__egrid__ = egrid
        self.__language__ = language
        self.__topics__ = topics

    def set_identdn(self, identdn):
        """
        Updates the IdentDN.

        :param identdn: The IdentDN as real estate identifier.
        :type identdn: str
        """
        self.__identdn__ = identdn

    def set_number(self, number):
        """
        Updates the parcel number.

        :param number: The parcel number as real estate identifier.
        :type number: str
        """
        self.__number__ = number

    def set_egrid(self, egrid):
        """
        Updates the EGRID.

        :param egrid: The EGRID as real estate identifier.
        :type egrid: str
        """
        self.__egrid__ = egrid

    def set_language(self, language):
        """
        Updates the language.

        :param language: The requested language.
        :type language: str
        """
        self.__language__ = language

    def set_topics(self, topics):
        """
        Updates the requested topics.

        :param topics: The list of requested topics.
        :type topics: list of str
        """
        self.__topics__ = topics

    @property
    def flavour(self):
        """

        :return: The requested flavour.
        :rtype: str
        """
        return self.__flavour__

    @property
    def format(self):
        """

        :return: The requested format.
        :rtype: str
        """
        return self.__format__

    @property
    def geometry(self):
        """

        :return: Extract requested with geometries.
        :rtype: bool
        """
        return self.__geometry__

    @property
    def images(self):
        """

        :return: Extract requested with images.
        :rtype: bool
        """
        return self.__images__

    @property
    def identdn(self):
        """

        :return: The requested IdentDN.
        :rtype: str
        """
        return self.__identdn__

    @property
    def number(self):
        """

        :return: The requested number.
        :rtype: str
        """
        return self.__number__

    @property
    def egrid(self):
        """

        :return: The requested EGRID.
        :rtype: str
        """
        return self.__egrid__

    @property
    def language(self):
        """

        :return: The requested language.
        :rtype: str
        """
        return self.__language__

    @property
    def topics(self):
        """

        :return: The requested topics.
        :rtype: list of str
        """
        return self.__topics__
