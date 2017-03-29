# -*- coding: utf-8 -*-
from pyramid.httpexceptions import HTTPBadRequest

from pyramid.httpexceptions import HTTPBadRequest
from pyramid_oereb import route_prefix
from pyramid_oereb.lib.config import ConfigReader


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
            endpoint += '/' + route_prefix
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
        settings = self._request_.registry.settings
        cfg = ConfigReader(
            settings.get('pyramid_oereb.cfg.file'),
            settings.get('pyramid_oereb.cfg.section')
        )
        return {
            u'topic': cfg.get_topic(),
            # TODO: Add municipalities when municipality reader is available
            u'municipality': [],
            u'flavour': cfg.get_flavour(),
            u'language': cfg.get_language(),
            u'crs': cfg.get_crs()
        }

    def get_egrid_coord(self):
        """
        Returns a list with the matched EGRIDs for the given coordinates.
        :return: The matched EGRIDs.
        :rtype:  list
        """
        xy = self._request_.params.get('XY')
        gnss = self._request_.params.get('GNSS')
        if xy or gnss:
            # TODO: Collect the EGRIDs using the property source
            return []
        else:
            raise HTTPBadRequest('XY or GNSS must be defined.')

    def get_egrid_ident(self):
        """
        Returns a list with the matched EGRIDs for the given NBIdent and property number.
        :return: The matched EGRIDs.
        :rtype:  list
        """
        identdn = self._request_.matchdict.get('identdn')
        number = self._request_.matchdict.get('number')
        if identdn and number:
            # TODO: Collect the EGRIDs using the property source
            return []
        else:
            raise HTTPBadRequest('IDENTDN and NUMBER must be defined.')

    def get_egrid_address(self):
        """
        Returns a list with the matched EGRIDs for the given postal address.
        :return: The matched EGRIDs.
        :rtype:  list
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
        with_images = False
        if self._request_.params.get('WITHIMAGES'):
            with_images = True

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
            params.update({'language': topics.split(',')})

        return params
