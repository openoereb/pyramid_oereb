# -*- coding: utf-8 -*-

import logging

from pyramid.httpexceptions import HTTPBadRequest, HTTPNoContent, HTTPServerError, HTTPNotFound, \
    HTTPInternalServerError
from pyramid.path import DottedNameResolver
from shapely.geometry import Point
from pyramid.renderers import render_to_response
from pyramid.response import Response

from pyramid_oereb import route_prefix
from pyramid_oereb import Config
from pyramid_oereb.lib.processor import Processor
from pyreproj import Reprojector

from pyramid_oereb.lib.readers.address import AddressReader

log = logging.getLogger(__name__)


class PlrWebservice(object):
    """
    This class provides the PLR webservice methods.

    Args:
        request (pyramid.request.Request or pyramid.testing.DummyRequest): The pyramid request instance.
    """
    def __init__(self, request):
        if not isinstance(request.pyramid_oereb_processor, Processor):
            raise HTTPServerError('Missing processor instance')
        self._request = request
        self._real_estate_reader = request.pyramid_oereb_processor.real_estate_reader
        self._municipality_reader = request.pyramid_oereb_processor.municipality_reader

    # For backward compatibility with old specification.
    def _is_json(self):
        """
        Returns True if the requests format is JSON.

        Returns:
            bool: True if requested format is JSON.
        """
        url = self._request.current_route_url().split('?')
        return url[0].endswith('.json')

    def get_versions(self):
        """
        Returns the available versions of this service.

        Returns:
            pyramid.response.Response: The `versions` response.
        """
        if route_prefix:
            endpoint = u'{application}/{route_prefix}'.format(
                application=self._request.application_url,
                route_prefix=route_prefix
            )
        else:
            endpoint = u'{application}'.format(application=self._request.application_url)
        versions = {
            u'GetVersionsResponse': {
                u'supportedVersion': [
                    {
                        u'version': u'1.0',
                        u'serviceEndpointBase': endpoint
                    }
                ]
            }
        }
        # Try - catch for backward compatibility with old specification.
        try:
            output_format = self.__validate_format_param__(['xml', 'json'])
            renderer_name = 'json' if output_format == 'json' else 'pyramid_oereb_versions_xml'
        except HTTPBadRequest:
            renderer_name = 'json' if self._is_json() else 'pyramid_oereb_versions_xml'
            log.warn('Deprecated way to specify the format. Use "/versions/{format}" instead')

        response = render_to_response(renderer_name, versions, request=self._request)
        if self._is_json():
            response.content_type = 'application/json; charset=UTF-8'
        return response

    def get_capabilities(self):
        """
        Returns the capabilities of this service.

        Returns:
            pyramid.response.Response: The `capabilities` response.
        """
        supported_languages = Config.get_language()
        themes = list()
        for theme in Config.get_themes():
            text = list()
            for lang in theme.text:
                if lang in supported_languages:
                    text.append({
                        'Language': lang,
                        'Text': theme.text[lang]
                    })
            themes.append({
                'Code': theme.code,
                'Text': text
            })
        capabilities = {
            u'GetCapabilitiesResponse': {
                u'topic': themes,
                u'municipality': [record.fosnr for record in self._municipality_reader.read()],
                u'flavour': Config.get_flavour(),
                u'language': supported_languages,
                u'crs': [Config.get_crs()]
            }
        }

        # Try - catch for backward compatibility with old specification.
        try:
            output_format = self.__validate_format_param__(['xml', 'json'])
            renderer_name = 'json' if output_format == 'json' else 'pyramid_oereb_capabilities_xml'
        except HTTPBadRequest:
            renderer_name = 'json' if self._is_json() else 'pyramid_oereb_capabilities_xml'
            log.warn('Deprecated way to specify the format. Use "/capabilities/{format}" instead')

        response = render_to_response(renderer_name, capabilities, request=self._request)
        if self._is_json():
            response.content_type = 'application/json; charset=UTF-8'
        return response

    def get_egrid_coord(self):
        """
        Returns a list with the matched EGRIDs for the given coordinates.

        Returns:
            pyramid.response.Response: The `getegrid` response.
        """
        xy = self._request.params.get('XY')
        gnss = self._request.params.get('GNSS')
        if xy or gnss:
            geom_wkt = 'SRID={0};{1}'
            if xy:
                geom_wkt = geom_wkt.format(Config.get('srid'),
                                           self.__parse_xy__(xy, buffer_dist=1.0).wkt)
            elif gnss:
                geom_wkt = geom_wkt.format(Config.get('srid'), self.__parse_gnss__(gnss).wkt)
            records = self._real_estate_reader.read(**{'geometry': geom_wkt})
            return self.__get_egrid_response__(records)
        else:
            raise HTTPBadRequest('XY or GNSS must be defined.')

    def get_egrid_ident(self):
        """
        Returns a list with the matched EGRIDs for the given NBIdent and property number.

        Returns:
            pyramid.response.Response: The `getegrid` response.
        """
        identdn = self._request.matchdict.get('identdn')
        number = self._request.matchdict.get('number')
        if identdn and number:
            records = self._real_estate_reader.read(**{
                'nb_ident': identdn,
                'number': number
            })
            return self.__get_egrid_response__(records)
        else:
            raise HTTPBadRequest('IDENTDN and NUMBER must be defined.')

    def get_egrid_address(self):
        """
        Returns a list with the matched EGRIDs for the given postal address.

        Returns:
            pyramid.response.Response: The `getegrid` response.
        """
        postalcode = self._request.matchdict.get('postalcode')
        localisation = self._request.matchdict.get('localisation')
        number = self._request.matchdict.get('number')
        if postalcode and localisation and number:
            reader = AddressReader(
                Config.get_address_config().get('source').get('class'),
                **Config.get_address_config().get('source').get('params')
            )
            addresses = reader.read(localisation, int(postalcode), number)
            if len(addresses) == 0:
                return HTTPNoContent()
            geometry = 'SRID={srid};{wkt}'.format(srid=Config.get('srid'), wkt=addresses[0].geom.wkt)
            records = self._real_estate_reader.read(**{'geometry': geometry})
            return self.__get_egrid_response__(records)
        else:
            raise HTTPBadRequest('POSTALCODE, LOCALISATION and NUMBER must be defined.')

    def get_extract_by_id(self):
        """
        Returns the extract in the specified format and flavour.

        Returns:
            pyramid.response.Response: The `extract` response.
        """
        log.debug("get_extract_by_id() start")
        params = self.__validate_extract_params__()
        processor = self._request.pyramid_oereb_processor
        # read the real estate from configured source by the passed parameters
        real_estate_reader = processor.real_estate_reader
        if params.egrid:
            real_estate_records = real_estate_reader.read(egrid=params.egrid)
        elif params.identdn and params.number:
            real_estate_records = real_estate_reader.read(
                nb_ident=params.identdn,
                number=params.number
            )
        else:
            raise HTTPBadRequest("Missing required argument")

        # check if result is strictly one (we queried with primary keys)
        if len(real_estate_records) == 1:
            extract = processor.process(
                real_estate_records[0],
                params,
                self._request.route_url('{0}/sld'.format(route_prefix))
            )
            if params.format == 'json':
                log.debug("get_extract_by_id() calling json")
                return render_to_response(
                    'pyramid_oereb_extract_json',
                    (extract, params),
                    request=self._request
                )
            elif params.format == 'xml':
                log.debug("get_extract_by_id() calling xml")
                return render_to_response(
                    'pyramid_oereb_extract_xml',
                    (extract, params),
                    request=self._request
                )
            elif params.format == 'pdf':
                log.debug("get_extract_by_id() calling pdf")
                return render_to_response(
                    'pyramid_oereb_extract_print',
                    (extract, params),
                    request=self._request
                )
            else:
                raise HTTPBadRequest("The format '{}' is wrong".format(params.format))
        else:
            return HTTPNoContent("No real estate found")

    def __validate_extract_params__(self):
        """
        Validates the input parameters for get_extract_by_id.

        Returns:
            pyramid_oereb.views.webservice.Parameter: The validated parameters.
        """

        # Check flavour
        extract_flavour = self._request.matchdict.get('flavour').lower()
        if extract_flavour not in ['reduced', 'full', 'signed', 'embeddable']:
            raise HTTPBadRequest('Invalid flavour: {0}'.format(extract_flavour))

        # Get and check format
        extract_format = self.__validate_format_param__(['pdf', 'xml', 'json'])

        # With geometry?
        with_geometry = False
        if self._request.matchdict.get('param1').lower() == 'geometry':
            with_geometry = True

        # Check for invalid combinations
        if extract_flavour in ['full', 'signed'] and extract_format != 'pdf':
            raise HTTPBadRequest('The flavours full and signed are only available for format PDF.')
        if extract_flavour == 'embeddable' and extract_format == 'pdf':
            raise HTTPBadRequest('The flavour embeddable is not available for format PDF.')
        if extract_format == 'pdf' and with_geometry:
            raise HTTPBadRequest('Geometry is not available for format PDF.')

        # With images?
        with_images = self._request.params.get('WITHIMAGES') is not None

        params = Parameter(extract_flavour, extract_format, with_geometry, with_images)

        # Get id
        if with_geometry:
            id_param_1 = 'param2'
            id_param_2 = 'param3'
        else:
            id_param_1 = 'param1'
            id_param_2 = 'param2'
        id_part_1 = self._request.matchdict.get(id_param_1)
        id_part_2 = self._request.matchdict.get(id_param_2)
        if id_part_2:
            params.set_identdn(id_part_1)
            params.set_number(id_part_2)
        else:
            params.set_egrid(id_part_1)

        # Language
        language = str(self._request.params.get('LANG')).lower()
        if language not in Config.get_language() and self._request.params.get('LANG') is not \
                None:
            raise HTTPBadRequest(
                'Requested language is not available. Following languages are configured: {languages} The '
                'requested language was: {language}'.format(
                    languages=str(Config.get_language()),
                    language=language
                )
            )
        if self._request.params.get('LANG'):
            params.set_language(language)

        # Topics
        topics = self._request.params.get('TOPICS')
        if topics:
            params.set_topics(topics.split(','))

        return params

    def __validate_format_param__(self, accepted_formats):
        """
        Get format in the url and validate that it's one accepted.

        Args:
            accepted_formats (list): A list of accepted format (str).

        Returns:
            str: The validated format parameter.
        """
        output_format = self._request.matchdict.get('format', '').lower()
        if output_format not in accepted_formats:
            raise HTTPBadRequest('Invalid format: {0}'.format(output_format))
        return output_format

    def __coord_transform__(self, coord, source_crs):
        """
        Transforms the specified coordinates from the specified CRS to the configured target CRS and creates a
        point geometry.

        Args:
            coord (tuple): The coordinates to transform (x, y).
            source_crs (intorstr): The source CRS

        Returns:
            shapely.geometry.Point or shapely.geometry.Polygon: The transformed coordinates as
            Point.
        """
        epsg = 'epsg:{0}'
        srid = Config.get('srid')
        rp = Reprojector()
        x, y = rp.transform(coord, from_srs=epsg.format(source_crs), to_srs=epsg.format(srid))
        return Point(x, y)

    def __get_egrid_response__(self, records):
        """
        Creates a valid GetEGRID response from a list of real estate records.

        Args:
            records (list of pyramid_oereb.lib.records.real_estate.RealEstateRecord): List of real
                estate records.

        Returns:
            pyramid.response.Response: The `getegrid` response.
        """

        if len(records) == 0:
            return HTTPNoContent()

        real_estates = list()
        for r in records:
            real_estates.append({
                'egrid': getattr(r, 'egrid'),
                'number': getattr(r, 'number'),
                'identDN': getattr(r, 'identdn')
            })
        egrid = {'GetEGRIDResponse': real_estates}

        # Try - catch for backward compatibility with old specification.
        try:
            output_format = self.__validate_format_param__(['xml', 'json'])
            renderer_name = 'json' if output_format == 'json' else 'pyramid_oereb_getegrid_xml'
        except HTTPBadRequest:
            renderer_name = 'json' if self._is_json() else 'pyramid_oereb_getegrid_xml'
            log.warn('Deprecated way to specify the format. Use "/getegrid/{format}/..." instead')

        response = render_to_response(renderer_name, egrid, request=self._request)
        if self._is_json():
            response.content_type = 'application/json; charset=UTF-8'
        return response

    def __parse_xy__(self, xy, buffer_dist=None):
        """
        Parses the coordinates from the XY parameter, transforms them to target CRS and creates a point
        geometry. If a buffer distance is defined, a buffer with the specified distance will be applied.

        Args:
            xy (str): XY parameter from the getegrid request.
            buffer_dist (float or None): Distance for the buffer applied to the transformed
                point.If None, no buffer will be applied.

        Returns:
            shapely.geometry.Point or shapely.geometry.Polygon: The transformed coordinates as
            Point.
        """
        coords = xy.split(',')

        if len(coords) != 2:
            raise HTTPBadRequest('The parameter XY has to be a comma-separated pair of coordinates.')

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

        Args:
            gnss (str): GNSS parameter from the getegrid request.

        Returns:
            shapely.geometry.Point or shapely.geometry.Polygon: The transformed coordinates as
            Point.
        """
        coords = gnss.split(',')

        if len(coords) != 2:
            raise HTTPBadRequest('The parameter GNSS has to be a comma-separated pair of coordinates.')

        # Coordinates provided as "latitude,longitude"
        lon = float(coords[1])
        lat = float(coords[0])
        return self.__coord_transform__((lon, lat), 4326).buffer(1.0)


class Parameter(object):
    def __init__(self, flavour, format, geometry, images, identdn=None, number=None, egrid=None,
                 language=None, topics=None):
        """
        Creates a new parameter instance.

        Args:
            flavour (str): The extract flavour.
            format (str): The extract format.
            geometry (bool): Extract with/without geometry.
            images (bool): Extract with/without images.
            identdn (str): The IdentDN as real estate identifier.
            number (str): The parcel number as real estate identifier.
            egrid (str): The EGRID as real estate identifier.
            language (str): The requested language.
            topics (list of str): The list of requested topics.
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

        Args:
            identdn (str): The IdentDN as real estate identifier.
        """
        self.__identdn__ = identdn

    def set_number(self, number):
        """
        Updates the parcel number.

        Args:
            number (str): The parcel number as real estate identifier.
        """
        self.__number__ = number

    def set_egrid(self, egrid):
        """
        Updates the EGRID.

        Args:
            egrid (str): The EGRID as real estate identifier.
        """
        self.__egrid__ = egrid

    def set_language(self, language):
        """
        Updates the language.

        Args:
            language (str): The requested language.
        """
        self.__language__ = language

    def set_topics(self, topics):
        """
        Updates the requested topics.

        Args:
            topics (list of str): The list of requested topics.
        """
        self.__topics__ = topics

    @property
    def flavour(self):
        """
        Returns:
            str: The requested flavour.
        """
        return self.__flavour__

    @property
    def format(self):
        """
        Returns:
            str: The requested format.
        """
        return self.__format__

    @property
    def geometry(self):
        """
        Returns:
            bool: Extract requested with geometries.
        """
        return self.__geometry__

    @property
    def images(self):
        """
        Returns:
            bool: Extract requested with images.
        """
        return self.__images__

    @property
    def identdn(self):
        """
        Returns:
            str: The requested IdentDN.
        """
        return self.__identdn__

    @property
    def number(self):
        """
        Returns:
            str: The requested number.
        """
        return self.__number__

    @property
    def egrid(self):
        """
        Returns:
            str: The requested EGRID.
        """
        return self.__egrid__

    @property
    def language(self):
        """
        Returns:
            str: The requested language.
        """
        return self.__language__

    @property
    def topics(self):
        """
        Returns:
            list of str: The requested topics.
        """
        return self.__topics__

    def skip_topic(self, theme_code):
        """
        Check if the topic should be skipped in extract.

        Args:
            theme_code (str): The PLR theme code.

        Returns:
            bool: True if the topic should be skipped.
        """
        if not self.topics or 'ALL' in self.topics:
            return False
        if theme_code in self.topics:
            return False
        if 'ALL_FEDERAL' in self.topics and theme_code in Config.get_all_federal():
            return False
        return True

    def __str__(self):
        return '<%s -- flavour: %s format: %s geometry: %s images: %s identdn: %s' \
                    ' number: %s egrid: %s language: %s topics: %s>' % (
                        self.__class__.__name__,
                        self.flavour, self.format, self.geometry, self.images, self.identdn,
                        self.number, self.egrid, self.language, self.topics)


class Logo(object):
    """
    Webservice to deliver logo images.

    Args:
        request (pyramid.request.Request or pyramid.testing.DummyRequest): The pyramid request instance.
    """
    def __init__(self, request):
        self._request = request

    def get_image(self):
        """
        Returns a response containing the binary image content using the configured "get_logo_method".

        Returns:
            pyramid.response.Response: Response containing the binary image content.
        """
        method = Config.get('get_logo_method')
        if method:
            return DottedNameResolver().resolve(method)(self._request)
        log.error('"get_logo_method" not found')
        raise HTTPNotFound()


class Municipality(object):
    """
    Webservice to deliver municipality images.

    Args:
        request (pyramid.request.Request or pyramid.testing.DummyRequest): The pyramid request instance.
    """
    def __init__(self, request):
        self._request_ = request

    def get_image(self):
        """
        Returns a response containing the binary image content using the configured "get_municipality_method".

        Returns:
            pyramid.response.Response: Response containing the binary image content.
        """
        method = Config.get('get_municipality_method')
        if method:
            return DottedNameResolver().resolve(method)(self._request_)
        log.error('"get_municipality_method" not found')
        raise HTTPNotFound()


class Symbol(object):
    """
    Webservice to deliver legend entry images.

    Args:
        request (pyramid.request.Request or pyramid.testing.DummyRequest): The pyramid request instance.
    """
    def __init__(self, request):
        self._request_ = request

    def get_image(self):
        """
        Returns a response containing the binary image content using the configured "get_symbol_method".

        Returns:
            pyramid.response.Response: Response containing the binary image content.
        """
        method = None
        dnr = DottedNameResolver()
        for plr in Config.get('plrs'):
            if str(plr.get('code')).lower() == str(self._request_.matchdict.get('theme_code')).lower():
                method = dnr.resolve(plr.get('hooks').get('get_symbol'))
                break
        if method:
            return method(self._request_)
        log.error('"get_symbol_method" not found')
        raise HTTPNotFound()


class Sld(object):
    """
    Webservice to deliver a valid sld content to filter a av base layer to only one dedicated real estate.

    """

    def __init__(self, request):
        """
        Args:
            request (pyramid.request.Request or pyramid.testing.DummyRequest): The pyramid request instance.
        """
        self._request_ = request

    def get_sld(self):
        """
        Webservice which delivers an SLD file from parameter input. However this is a proxy pass through only.
        We use it to call the real method configured in the dedicated yaml file and hope that this method is
        accepting a pyramid.request.Request as input and is returning a pyramid.response.Response which
        encapsulates a well designed SLD.

        .. note:: The config path to define this hook method is:
            *pyramid_oereb.real_estate.visualisation.method*

        Returns:
             pyramid.response.Response: The response provided by the hooked method provided by the
                configuration

        Raises:
            pyramid.httpexceptions.HTTPInternalServerError: When the return value of the hooked method was not
                of type pyramid.response.Response
            pyramid.httpexceptions.HTTPNotFound: When the configured method was not found.
        """
        dnr = DottedNameResolver()
        visualisation_config = Config.get_real_estate_config().get('visualisation')
        method_path = visualisation_config.get('method')
        method = dnr.resolve(method_path)
        if method:
            result = method(self._request_)
            if isinstance(result, Response):
                return result
            else:
                log.error(
                    u'The called method {path} does not returned the expected '
                    u'pyramid.response.Response instance. Returned value was {type}'.format(
                        path=method_path,
                        type=type(result)
                    )
                )
                raise HTTPInternalServerError()
        log.error(u'method in path "{path}" not found'.format(path=method_path))
        raise HTTPNotFound()
