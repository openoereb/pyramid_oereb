# -*- coding: utf-8 -*-

import logging
# import yappi

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPInternalServerError, HTTPNoContent, \
    HTTPNotFound
from pyramid.path import DottedNameResolver
from shapely.geometry import Point
from pyramid.renderers import render_to_response

from pyramid_oereb import route_prefix
from pyramid_oereb import Config
from pyreproj import Reprojector

from pyramid_oereb.core.processor import create_processor
from pyramid_oereb.core.readers.address import AddressReader
from pyramid_oereb.core.renderer import Base as Renderer
from timeit import default_timer as timer

from pyramid_oereb.contrib.stats.decorators import OerebStats

log = logging.getLogger(__name__)


class PlrWebservice(object):
    """
    This class provides the PLR webservice methods.

    Args:
        request (pyramid.request.Request or pyramid.testing.DummyRequest): The pyramid request instance.
    """

    _DEFAULT_FORMATS = ['xml', 'json']
    """list of str: The default formats for the service responses."""

    _EXTRACT_FORMATS = _DEFAULT_FORMATS + ['pdf', 'url']
    """list of str: The formats for the extract responses."""

    def __init__(self, request):
        self._request = request
        self._params = {k.upper(): v for k, v in request.params.items()}

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
                        u'version': u'extract-2.0',
                        u'serviceEndpointBase': endpoint
                    }
                ]
            }
        }
        output_format = self.__validate_format_param__(self._DEFAULT_FORMATS)
        renderer_name = 'json' if output_format == 'json' else 'pyramid_oereb_versions_xml'
        response = render_to_response(renderer_name, versions, request=self._request)
        if output_format == 'json':
            response.content_type = 'application/json; charset=UTF-8'
        response.extras = OerebStats(service='GetVersions', output_format=output_format)
        return response

    def get_capabilities(self):
        """
        Returns the capabilities of this service.

        Returns:
            pyramid.response.Response: The `capabilities` response.
        """

        output_format = self.__validate_format_param__(self._DEFAULT_FORMATS)

        supported_languages = Config.get_language()
        themes = list()
        for theme in Config.get_themes():
            text = list()
            for lang in theme.title:
                if lang in supported_languages:
                    text.append({
                        'Language': lang,
                        'Text': theme.title[lang]
                    })
            themes.append({
                'Code': theme.code,
                'Text': text
            })
        capabilities = {
            u'GetCapabilitiesResponse': {
                u'topic': Config.get_themes() if output_format == 'xml' else themes,
                u'municipality': [record.fosnr for record in Config.municipalities],
                u'flavour': Config.get_flavour(),
                u'language': supported_languages,
                u'crs': [Config.get_crs()]
            }
        }

        renderer_name = 'json' if output_format == 'json' else 'pyramid_oereb_capabilities_xml'  # noqa: E501
        response = render_to_response(renderer_name, capabilities, request=self._request)
        if output_format == 'json':
            response.content_type = 'application/json; charset=UTF-8'
        response.extras = OerebStats(service='GetCapabilities', output_format=output_format)
        return response

    def get_egrid(self):
        """
        Validates the request parameters and calls the query method
        according to the specified parameters.

        Returns:
            pyramid.response.Response: The `getegrid` response.
        """
        try:
            output_format = self.__validate_format_param__(self._DEFAULT_FORMATS)
            service = None
            with_geometry = False
            if self.__has_params__(['GEOMETRY']):
                if self._params.get('GEOMETRY').lower() == 'true':
                    with_geometry = True
            params = Parameter(
                output_format,
                with_geometry=with_geometry
            )
            # Type A
            if self.__has_params__(['EN']):
                service = 'GetEgridCoord'
                records = self._get_egrid_coord(params)
            # Type B
            elif self.__has_params__(['IDENTDN', 'NUMBER']):
                service = 'GetEgridIdent'
                records = self._get_egrid_ident(params)
            # Type C
            elif self.__has_params__(['POSTALCODE', 'LOCALISATION', 'NUMBER']):
                service = 'GetEgridAddress'
                records = self._get_egrid_address(params)
            # Type D
            elif self.__has_params__(['GNSS']):
                service = 'GetEgridCoord'
                records = self._get_egrid_coord(params)
            # Raise exception
            else:
                raise HTTPBadRequest(
                    'Invalid parameters. You need one of the following combinations: '
                    'EN or GNSS or IDENTDN and NUMBER or POSTALCODE, LOCALISATION and NUMBER.'
                )
            response = self.__get_egrid_response__(records, params)
        except HTTPNoContent as err:
            response = HTTPNoContent('{}'.format(err))
        except HTTPBadRequest as err:
            response = HTTPBadRequest('{}'.format(err))
        response.extras = OerebStats(
            service=service,
            params=dict(self._params),
            output_format=output_format
        )
        return response

    def _get_egrid_coord(self, params):
        """
        Returns a list with the matched EGRIDs for the given coordinates.

        Args:
            params (pyramid_oereb.views.webservice.Parameter): The parameter object.

        Returns:
            list of pyramid_oereb.core.records.real_estate.RealEstateRecord:
                The list of all found records filtered by the passed criteria.
        """
        en = self._params.get('EN')
        gnss = self._params.get('GNSS')
        if en or gnss:
            geom_wkt = 'SRID={0};{1}'
            if en:
                geom_wkt = geom_wkt.format(
                    Config.get('srid'),
                    self.__parse_en__(en, buffer_dist=1.0).wkt
                )
            elif gnss:
                geom_wkt = geom_wkt.format(
                    Config.get('srid'),
                    self.__parse_gnss__(gnss).wkt
                )
            processor = create_processor()
            return processor.real_estate_reader.read(params, **{'geometry': geom_wkt})
        else:
            raise HTTPBadRequest('EN or GNSS must be defined.')

    def _get_egrid_ident(self, params):
        """
        Returns a list with the matched EGRIDs for the given NBIdent and property number.

        Args:
            params (pyramid_oereb.views.webservice.Parameter): The parameter object.

        Returns:
            list of pyramid_oereb.core.records.real_estate.RealEstateRecord:
                The list of all found records filtered by the passed criteria.
        """
        identdn = self._params.get('IDENTDN')
        number = self._params.get('NUMBER')
        if identdn and number:
            processor = create_processor()
            return processor.real_estate_reader.read(
                params,
                **{
                    'nb_ident': identdn,
                    'number': number
                }
            )
        else:
            raise HTTPBadRequest('IDENTDN and NUMBER must be defined.')

    def _get_egrid_address(self, params):
        """
        Returns a list with the matched EGRIDs for the given postal address.

        Args:
            params (pyramid_oereb.views.webservice.Parameter): The parameter object.

        Returns:
            list of pyramid_oereb.core.records.real_estate.RealEstateRecord:
                The list of all found records filtered by the passed criteria.
        """
        postalcode = self._params.get('POSTALCODE')
        localisation = self._params.get('LOCALISATION')
        number = self._params.get('NUMBER')
        if postalcode and localisation and number:
            reader = AddressReader(
                Config.get_address_config().get('source').get('class'),
                **Config.get_address_config().get('source').get('params')
            )
            addresses = reader.read(params, localisation, int(postalcode), number)
            if len(addresses) == 0:
                raise HTTPNoContent()
            geometry = 'SRID={srid};{wkt}'.format(
                srid=Config.get('srid'),
                wkt=addresses[0].geom.wkt
            )
            processor = create_processor()
            return processor.real_estate_reader.read(params, **{'geometry': geometry})
        else:
            raise HTTPBadRequest('POSTALCODE, LOCALISATION and NUMBER must be defined.')

    def get_extract_by_id(self):
        """
        Returns the extract in the specified format and flavour.

        Returns:
            pyramid.response.Response: The `extract` response.
        """
        start_time = timer()
        log.debug("get_extract_by_id() start")
        try:
            params = self.__validate_extract_params__()
            processor = create_processor()
            # read the real estate from configured source by the passed parameters
            real_estate_reader = processor.real_estate_reader
            if params.egrid:
                real_estate_records = real_estate_reader.read(params, egrid=params.egrid)
            elif params.identdn and params.number:
                real_estate_records = real_estate_reader.read(
                    params,
                    nb_ident=params.identdn,
                    number=params.number
                )
            else:
                raise HTTPBadRequest("Missing required argument")
            # check if result is strictly one (we queried with primary keys)
            if len(real_estate_records) == 1:

                # Redirect for format URL
                if params.format == 'url':
                    log.debug("get_extract_by_id() calling url")
                    return self.__redirect_to_dynamic_client__(real_estate_records[0])
                # yappi.set_clock_type("cpu")
                # yappi.start()
                extract = processor.process(
                    real_estate_records[0],
                    params,
                    self._request.route_url('{0}/sld'.format(route_prefix))
                )
                # yappi.get_func_stats().save('/workspace/processor_function_stats.prof', "pstat")
                # yappi.get_thread_stats().save('/workspace/processor_thread_stats.prof', "pstat")

                if params.format == 'json':
                    log.debug("get_extract_by_id() calling json")
                    response = render_to_response(
                        'pyramid_oereb_extract_json',
                        (extract, params),
                        request=self._request
                    )
                elif params.format == 'xml':
                    log.debug("get_extract_by_id() calling xml")
                    response = render_to_response(
                        'pyramid_oereb_extract_xml',
                        (extract, params),
                        request=self._request
                    )
                elif params.format == 'pdf':
                    log.debug("get_extract_by_id() calling pdf")
                    response = render_to_response(
                        'pyramid_oereb_extract_print',
                        (extract, params),
                        request=self._request
                    )
                else:
                    raise HTTPBadRequest("The format '{}' is wrong".format(params.format))
                end_time = timer()
                log.debug("DONE with extract, time spent: {} seconds".format(end_time - start_time))
            else:
                raise HTTPNoContent("No real estate found")
        except HTTPNoContent as err:
            response = HTTPNoContent('{}'.format(err))
        except HTTPBadRequest as err:
            response = HTTPBadRequest('{}'.format(err))
        try:
            response.extras = OerebStats(service='GetExtractById',
                                         output_format=params.format,
                                         params=vars(params))
        except UnboundLocalError:
            response.extras = OerebStats(service='GetExtractById', params={'error': response.message})
        except Exception:
            # if params is not set we get UnboundLocalError
            # or we could get ValueError
            # in any case, the logging should never crash the response delivery
            try:
                response.extras = OerebStats(service='GetExtractById', params={'error': response.message})
            except AttributeError:
                response.extras = OerebStats(service='GetExtractById')
        return response

    def __validate_extract_params__(self):
        """
        Validates the input parameters for get_extract_by_id.

        Returns:
            pyramid_oereb.views.webservice.Parameter: The validated parameters.
        """

        # Get and check format
        extract_format = self.__validate_format_param__(self._EXTRACT_FORMATS)

        # With geometry?
        with_geometry = False
        user_requested_geometry = False
        if self._params.get('GEOMETRY', 'false').lower() == 'true':
            with_geometry = True
            user_requested_geometry = True

        # Check for invalid combinations
        if extract_format == 'pdf' and user_requested_geometry:
            raise HTTPBadRequest('Geometry is not available for format PDF.')

        # If PDF is to be produced, check if geometry should be included
        # (this override can be needed for the print service. Note that, to be compliant to specification,
        # the URL for a PDF request should not contain the geometry parameter)
        if extract_format == 'pdf':
            with_geometry = Config.get('print', {}).get('with_geometry', True) or with_geometry

        # With images?
        with_images = self._params.get('WITHIMAGES', 'false').lower() == 'true'

        # Signed?
        signed = self._params.get('SIGNED', 'false').lower() == 'true'

        params = Parameter(
            extract_format,
            with_geometry=with_geometry,
            images=with_images,
            signed=signed
        )

        # Get id
        if self.__has_params__(['EGRID']):
            params.set_egrid(self._params['EGRID'])
        elif self.__has_params__(['IDENTDN', 'NUMBER']):
            params.set_identdn(self._params['IDENTDN'])
            params.set_number(self._params['NUMBER'])
        else:
            raise HTTPBadRequest(
                'Invalid parameters. You need one of the following combinations: '
                'EGRID or IDENTDN and NUMBER.'
            )

        # Language
        if 'LANG' in self._params:
            language = str(self._params.get('LANG')).lower()
            if language not in Config.get_language():
                raise HTTPBadRequest(
                    'Requested language is not available. Following languages are '
                    'configured: {languages}. The '
                    'requested language was: {language}.'.format(
                        languages=str(Config.get_language()),
                        language=language
                    )
                )
            params.set_language(language)

        # Topics
        topics = self._params.get('TOPICS')
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
        Transforms the specified coordinates from the specified CRS to the configured target
        CRS and creates a point geometry.

        Args:
            coord (tuple): The coordinates to transform (x, y).
            source_crs (intorstr): The source CRS

        Returns:
            shapely.geometry.Point or shapely.geometry.Polygon: The transformed coordinates as
            Point.
        """
        log.debug('----- Transforming Coordinates: -----')
        log.debug('----- X/Y Coordinates: {0} -----'.format(coord))
        epsg = 'epsg:{0}'
        srid = Config.get('srid')
        log.debug('----- srid from config (to_srs): {0} -----'.format(srid))
        log.debug('----- srid from source (from_srs): {0} -----'.format(source_crs))
        rp = Reprojector()
        x, y = rp.transform(coord, from_srs=epsg.format(source_crs), to_srs=epsg.format(srid))
        log.debug('----- X/Y coordinates after transformation: ({0}, {1}) -----'.format(x, y))
        return Point(x, y)

    def __get_egrid_response__(self, records, params):
        """
        Creates a valid GetEGRID response from a list of real estate records.

        Args:
            records (list of pyramid_oereb.lib.records.real_estate.RealEstateRecord): List of real
                estate records.
            params (pyramid_oereb.views.webservice.Parameter): The parameter object.

        Returns:
            pyramid.response.Response: The `getegrid` response.
        """

        if len(records) == 0:
            return HTTPNoContent()
        output_format = self.__validate_format_param__(self._DEFAULT_FORMATS)
        real_estates = list()
        supported_languages = Config.get_language()
        for r in records:
            real_estate_type = Config.get_real_estate_type_by_data_code(getattr(r, 'type'))
            text = []
            for lang in real_estate_type.title:
                if lang in supported_languages:
                    text.append({
                        'Language': lang,
                        'Text': real_estate_type.title[lang]
                    })
            real_estate = {
                'egrid': getattr(r, 'egrid'),
                'number': getattr(r, 'number'),
                'identDN': getattr(r, 'identdn'),
                'type': {
                    'Code': real_estate_type.code,
                    'Text': text
                }
            }
            if params.with_geometry and output_format == 'json':
                real_estate.update({
                    'limit': Renderer.from_shapely(getattr(r, 'limit'))
                })
            elif params.with_geometry and output_format == 'xml':
                real_estate.update({
                    'limit': getattr(r, 'limit')
                })
            elif params.with_geometry and output_format not in ['json', 'xml']:
                raise HTTPInternalServerError('Format for GetEgrid not correct: {}'.format(output_format))
            real_estates.append(real_estate)
        egrid = {'GetEGRIDResponse': real_estates}
        if output_format == 'json':
            response = render_to_response('json', egrid, request=self._request)
            response.content_type = 'application/json; charset=UTF-8'
        else:
            response = render_to_response(
                'pyramid_oereb_getegrid_xml',
                (egrid, params),
                request=self._request
            )

        response.extras = OerebStats(service='GetEGRID', output_format=output_format)
        return response

    @staticmethod
    def __parse_en__(en, buffer_dist=None):
        """
        Parses the coordinates from the XY parameter and creates a point geometry.
        If a buffer distance is defined, a buffer with the specified distance will be applied.

        Args:
            en (str): EN parameter from the getegrid request.
            buffer_dist (float or None): Distance for the buffer applied to the
                point. If None, no buffer will be applied.

        Returns:
            shapely.geometry.Point or shapely.geometry.Polygon: The coordinates as
                Point or, if using a buffer, as Polygon.
        """
        coords = en.split(',')

        if len(coords) != 2:
            raise HTTPBadRequest(
                'The parameter EN has to be a comma-separated pair of coordinates.')

        x = float(coords[0])
        y = float(coords[1])
        p = Point(x, y)
        if buffer_dist:
            return p.buffer(buffer_dist)
        else:
            return p

    def __parse_gnss__(self, gnss):
        """
        Parses the coordinates from the GNSS parameter, transforms them to target CRS and
        creates a Point with a 1 meter buffer.

        Args:
            gnss (str): GNSS parameter from the getegrid request.

        Returns:
            shapely.geometry.Point or shapely.geometry.Polygon: The transformed coordinates as
            Point.
        """
        coords = gnss.split(',')

        if len(coords) != 2:
            raise HTTPBadRequest(
                'The parameter GNSS has to be a comma-separated pair of coordinates.')

        # Coordinates provided as "latitude,longitude"
        return self.__coord_transform__(coords, 4326).buffer(1.0)

    def __has_params__(self, needed):
        """
        Checks if the request contains all needed parameters.

        Args:
            needed (list of str): The parameters to check.

        Returns:
            bool: True if all needed parameters are available, false otherwise.
        """
        for p in needed:
            if p not in self._params:
                return False
        return True

    @staticmethod
    def __redirect_to_dynamic_client__(real_estate):
        """
        Returns a redirect to the configured dynamic client.

        Args:
            real_estate (pyramid_oereb.lib.records.real_estate.RealEstateRecord):
                The found real estate.

        Returns:
            pyramid.httpexceptions.HTTPFound: The redirect response.
        """
        url = Config.get_extract_config().get('redirect')
        if url is None:
            raise HTTPInternalServerError('Missing configuration for redirect to dynamic client.')
        return HTTPFound(url.format(**vars(real_estate)))


class Parameter(object):
    def __init__(self, response_format, with_geometry=False, images=False, signed=False, identdn=None,
                 number=None, egrid=None, language=None, topics=None):
        """
        Creates a new parameter instance.

        Args:
            response_format (str): The extract format.
            with_geometry (bool): Extract with/without geometry.
            images (bool): Extract with/without images.
            signed (bool): True for a signed extract.
            identdn (str): The IdentDN as real estate identifier.
            number (str): The parcel number as real estate identifier.
            egrid (str): The EGRID as real estate identifier.
            language (str): The requested language.
            topics (list of str): The list of requested topics.
        """
        self.__format__ = response_format
        self.__with_geometry__ = with_geometry
        self.__images__ = images
        self.__signed__ = signed
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
    def format(self):
        """
        Returns:
            str: The requested format.
        """
        return self.__format__

    @property
    def with_geometry(self):
        """
        Returns:
            bool: Extract requested with geometries.
        """
        return self.__with_geometry__

    @property
    def images(self):
        """
        Returns:
            bool: Extract requested with images.
        """
        return self.__images__

    @property
    def signed(self):
        """
        Returns:
            bool: Signed extract requested.
        """
        return self.__signed__

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
        return '<%s -- format: %s geometry: %s images: %s identdn: %s' \
                    ' number: %s egrid: %s language: %s topics: %s>' % (
                        self.__class__.__name__,
                        self.format, self.with_geometry, self.images, self.identdn,
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
        Returns a response containing the binary logo image content using the configured "get_logo_method".

        Returns:
            pyramid.response.Response: Response containing the binary image content.
        """
        logo_key = self._request.matchdict.get('logo')
        logo_language = self._request.matchdict.get('language')
        if(logo_key.upper() == 'CONFEDERATION'):
            logo = Config.get_conferderation_logo()
        elif(logo_key.upper() == 'OEREB'):
            logo = Config.get_oereb_logo()
        elif(logo_key.upper() == 'CANTON'):
            logo = Config.get_canton_logo()
        elif(logo_key.upper() == 'MUNICIPALITY'):
            fosnr = self._request.params['fosnr']
            logo = Config.get_municipality_logo(fosnr)
        else:
            raise HTTPNotFound('This logo does not exist.')
        response = self._request.response
        response.status_int = 200
        response.body = logo.image_dict[logo_language].content
        response.content_type = logo.image_dict[logo_language].mimetype
        return response


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
        theme_code = self._request_.matchdict.get('theme_code')
        method = self.get_method(theme_code)
        theme_config = Config.get_theme_config_by_code(str(theme_code))
        if method:
            body, mimetype = method(dict(self._request_.params), theme_config)
            response = self._request_.response
            response.status_int = 200
            response.body = body
            response.content_type = mimetype
            return response
        log.error('"get_symbol_method" not found')
        raise HTTPNotFound()

    @staticmethod
    def get_method(theme_code):
        dnr = DottedNameResolver()
        theme_config = Config.get_theme_config_by_code(str(theme_code))
        return dnr.resolve(theme_config.get('hooks').get('get_symbol'))


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
        Webservice which delivers an SLD file from parameter input. However
        this is a proxy pass through only. We use it to call the real method
        configured in the dedicated yaml file and hope that this method is
        accepting a pyramid.request.Request as input and is returning a
        pyramid.response.Response which encapsulates a well designed SLD.

        .. note:: The config path to define this hook method is:
            *pyramid_oereb.real_estate.visualisation.method*

        Returns:
             pyramid.response.Response: The response provided by the hooked method provided by the
                configuration

        Raises:
            pyramid.httpexceptions.HTTPInternalServerError: When the return
            value of the hooked method was not of type pyramid.response.Response
            pyramid.httpexceptions.HTTPNotFound: When the configured method was not found.
        """
        real_estate_config = Config.get_real_estate_config()
        params = {}
        for param in real_estate_config['visualisation']['url_params']:
            params.update({param: self._request_.params.get(param)})
        method = self.get_method()
        response = self._request_.response
        response.content_type = 'application/xml'
        if method:
            response.body = method(params, real_estate_config)
            return response
        log.error(u'method in path "{path}" not found'.format(
            path=real_estate_config['visualisation']['method'])
        )
        raise HTTPNotFound()

    @staticmethod
    def get_method():
        dnr = DottedNameResolver()
        visualisation_config = Config.get_real_estate_config().get('visualisation')
        method_path = visualisation_config.get('method')
        return dnr.resolve(method_path)
