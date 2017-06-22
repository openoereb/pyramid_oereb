# -*- coding: utf-8 -*-
import logging
from pyramid.httpexceptions import HTTPBadRequest, HTTPNoContent, HTTPServerError, HTTPNotFound
from pyramid.path import DottedNameResolver
from shapely.geometry import Point
from pyramid.renderers import render_to_response
from sqlalchemy.orm.exc import NoResultFound

from pyramid_oereb import route_prefix
from pyramid_oereb import Config
from pyramid_oereb.lib.processor import Processor
from pyreproj import Reprojector


log = logging.getLogger('pyramid_oereb')


class PlrWebservice(object):
    """
    This class provides the PLR webservice methods.

    Args:
        request (pyramid.request.Request or pyramid.testing.DummyRequest): The pyramid request instance.
    """
    def __init__(self, request):
        if not isinstance(request.pyramid_oereb_processor, Processor):
            raise HTTPServerError('Missing processor instance')
        self._request_ = request
        self._real_estate_reader_ = request.pyramid_oereb_processor.real_estate_reader
        self._municipality_reader_ = request.pyramid_oereb_processor.municipality_reader

    def get_versions(self):
        """
        Returns the available versions of this service.

        Returns:
            dict: The available service versions.
        """
        endpoint = self._request_.application_url
        if route_prefix:
            endpoint += '/' + route_prefix  # pragma: no cover
        return {
            u'GetVersionsResponse': {
                u'supportedVersion': [
                    {
                        u'version': u'1.0.0',
                        u'serviceEndpointBase': unicode(endpoint)
                    }
                ]
            }
        }

    def get_capabilities(self):
        """
        Returns the capabilities of this service.

        Returns:
            dict: The service capabilities.
        """
        themes = list()
        for theme in Config.get_themes():
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
            u'GetCapabilitiesResponse': {
                u'topic': themes,
                u'municipality': [record.fosnr for record in self._municipality_reader_.read()],
                u'flavour': Config.get_flavour(),
                u'language': Config.get_language(),
                u'crs': Config.get_crs()
            }
        }

    def get_egrid_coord(self):
        """
        Returns a list with the matched EGRIDs for the given coordinates.

        Returns:
            list of dict: The matched EGRIDs.
        """
        xy = self._request_.params.get('XY')
        gnss = self._request_.params.get('GNSS')
        if xy or gnss:
            geom_wkt = 'SRID={0};{1}'
            if xy:
                geom_wkt = geom_wkt.format(Config.get('srid'),
                                           self.__parse_xy__(xy, buffer_dist=1.0).wkt)
            elif gnss:
                geom_wkt = geom_wkt.format(Config.get('srid'), self.__parse_gnss__(gnss).wkt)
            records = self._real_estate_reader_.read(**{'geometry': geom_wkt})
            return self.__get_egrid_response__(records)
        else:
            raise HTTPBadRequest('XY or GNSS must be defined.')

    def get_egrid_ident(self):
        """
        Returns a list with the matched EGRIDs for the given NBIdent and property number.

        Returns:
            list of dict: The matched EGRIDs.
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

        Returns:
            list of dict: The matched EGRIDs.
        """
        postalcode = self._request_.matchdict.get('postalcode')
        localisation = self._request_.matchdict.get('localisation')
        number = self._request_.matchdict.get('number')
        if postalcode and localisation and number:
            # TODO: Collect the EGRIDs using the property source
            return {'GetEGRIDResponse': []}
        else:
            raise HTTPBadRequest('POSTALCODE, LOCALISATION and NUMBER must be defined.')

    def get_extract_by_id(self):
        """
        Returns the extract in the specified format and flavour.

        Returns:
            dict: The requested extract.
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
                extract = processor.process(real_estate_records[0], params)
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
                return render_to_response(
                    'pyramid_oereb_extract_print',
                    (extract, params),
                    request=self._request_
                )
            else:
                raise HTTPBadRequest()
        else:
            raise HTTPBadRequest()

    def __validate_extract_params__(self):
        """
        Validates the input parameters for get_extract_by_id.

        Returns:
            pyramid_oereb.views.webservice.Parameter: The validated parameters.
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
        if language not in Config.get_language() and self._request_.params.get('LANG') is not \
                None:
            raise HTTPBadRequest(
                'Requested language is not available. Following languages are configured: {languages} The '
                'requested language was: {language}'.format(
                    languages=str(Config.get_language()),
                    language=language
                )
            )
        if self._request_.params.get('LANG'):
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
            list of dict: Valid GetEGRID response.
        """
        response = list()
        for r in records:
            response.append({
                'egrid': getattr(r, 'egrid'),
                'number': getattr(r, 'number'),
                'identDN': getattr(r, 'identdn')
            })
        return {'GetEGRIDResponse': response}

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
        x = float(coords[0])
        y = float(coords[1])
        return self.__coord_transform__((x, y), 4326).buffer(1.0)


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


class Logo(object):
    """
    Webservice to deliver logo images.

    Args:
        request (pyramid.request.Request or pyramid.testing.DummyRequest): The pyramid request instance.
    """
    def __init__(self, request):
        self._request_ = request

    def get_image(self):
        """
        Returns a response containing the binary image content using the configured "get_logo_method".

        Returns:
            pyramid.response.Response: Response containing the binary image content.
        """
        method = Config.get('get_logo_method')
        if method:
            return DottedNameResolver().resolve(method)(self._request_)
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
                method = dnr.resolve(plr.get('get_symbol_method'))
                break
        if method:
            return method(self._request_)
        log.error('"get_symbol_method" not found')
        raise HTTPNotFound()
