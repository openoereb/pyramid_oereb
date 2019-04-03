# -*- coding: utf-8 -*-
import sys
import requests
import logging

from pyramid.httpexceptions import HTTPBadRequest
from pyramid_oereb import Config
from pyramid_oereb.lib.renderer.extract.xml_ import Renderer as XmlRenderer
if sys.version_info.major == 2:
    import urlparse
else:
    from urllib import parse as urlparse


log = logging.getLogger(__name__)


class Renderer(XmlRenderer):

    def __call__(self, value, system):
        """
        Implements a subclass of pyramid_oereb.lib.renderer.extract.json_.Renderer to create a print result
        out of a json. The json extract is reformatted to fit the structure of mapfish print.

        Args:
            value (tuple): A tuple containing the generated extract record and the params
                dictionary.
            system (dict): The available system properties.

        Returns:
            buffer: The pdf content as received from configured mapfish print instance url.
        """
        log.debug("Parameter webservice is {}".format(value[1]))

        if value[1].images:
            raise HTTPBadRequest('With image is not allowed in the print')

        self._request = self.get_request(system)
        # If language present in request, use that. Otherwise, keep language from base class
        if 'lang' in self._request.GET:
            self._language = self._request.GET.get('lang')

        # Based on extract record and webservice parameter, render the extract data as JSON
        extract_record = value[0]
        extract_as_xml = self._render(extract_record, value[1])

        response = self.get_response(system)

        if self._request.GET.get('getspec', 'no') != 'no':
            response.headers['Content-Type'] = 'application/xml; charset=UTF-8'
            return extract_as_xml

        print_result = requests.post(
            urlparse.urljoin(Config.get('print', {})['base_url'] + '/', 'buildreport.pdf'),
            headers=Config.get('print', {})['headers'],
            data=extract_as_xml
        )

        response.status_code = print_result.status_code
        response.headers = print_result.headers
        if 'Transfer-Encoding' in response.headers:
            del response.headers['Transfer-Encoding']
        if 'Connection' in response.headers:
            del response.headers['Connection']
        return print_result
