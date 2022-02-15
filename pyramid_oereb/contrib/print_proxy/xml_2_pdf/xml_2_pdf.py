# -*- coding: utf-8 -*-
import requests
import logging

from pyramid.exceptions import ConfigurationError
from pyramid.httpexceptions import HTTPBadRequest
from pyramid_oereb import Config
from pyramid_oereb.core.renderer.extract.xml_ import Renderer as XmlRenderer


log = logging.getLogger(__name__)


class Renderer(XmlRenderer):

    def __call__(self, value, system):
        """
        Implements a subclass of pyramid_oereb.core.renderer.extract.xml_.Renderer to create a print result
        out of a xml. The xml extract is reformatted to fit the structure of xml2pdf.

        Args:
            value (tuple): A tuple containing the generated extract record and the params
                dictionary.
            system (dict): The available system properties.

        Returns:
            pyramid.response.Response: The pdf content as received from configured mapfish print instance url.

        Raises:
            ConfigurationError
        """
        print_config = Config.get('print', {})
        if not print_config:
            raise ConfigurationError('No print config section in config file was found.')
        print_service_url = print_config.get('base_url', '')
        if not print_service_url:
            raise ConfigurationError('No print service url ("base_url") was found in the config.')
        print_service_token = print_config.get('token', '')
        if not print_service_token:
            raise ConfigurationError('No print service token ("token") was found in the config.')
        verify_certificate = print_config.get('verify_certificate', True)

        self.headers = {
            'token': print_service_token
        }
        self.parameters = {
            'validate': print_config.get('validate', 'false'),
            'usewms': print_config.get('use_wms', 'false'),
        }

        log.debug("Parameter webservice is {}".format(value[1]))

        if value[1].images:
            raise HTTPBadRequest('With image is not allowed in the print')

        self._request = self.get_request(system)
        # If language present in request, use that. Otherwise, keep language from base class
        if 'lang' in self._request.GET:
            self._language = self._request.GET.get('lang')

        self.parameters['language'] = self._language
        self.parameters['flavour'] = self._request.matchdict['flavour']

        # Based on extract record and webservice parameter, render the extract data as JSON
        extract_record = value[0]
        extract_as_xml = self._render(extract_record, value[1])

        response = self.get_response(system)

        if self._request.GET.get('getspec', 'no') != 'no':
            response.headers['Content-Type'] = 'application/xml; charset=UTF-8'
            return extract_as_xml

        prepared_extraxt_as_xml = self.prepare_xml(extract_as_xml)
        print_result = self.request_pdf(
            print_service_url,
            prepared_extraxt_as_xml,
            self.headers,
            self.parameters,
            verify_certificate
        )

        response.status_code = print_result.status_code
        response.headers = print_result.headers
        if 'Transfer-Encoding' in response.headers:
            del response.headers['Transfer-Encoding']
        if 'Connection' in response.headers:
            del response.headers['Connection']
        return print_result

    @staticmethod
    def request_pdf(url, data_extract, headers, parameters, verify_certificate):
        """
        Posts the print request to the configured print server to return the pdf extract.

        Args:
            url (str): URl to the print webservice.
            data_extract (xml): The rendered xml extract.
            headers (dict): Request headers for print request.
            parameters (dict): Additional print parameters, such as language or flavour.
            verify_certificate (boolean): Define if certificate should be verified.

        Returns:
            file: The pdf file as received from configured mapfish print instance url.

        Raises:
            Exception: Request failed.
        """
        try:
            backend_answer = requests.post(
                url,
                verify=verify_certificate,
                headers=headers,
                files={'file': ('xml', data_extract, 'text/xml')},
                data=parameters,
                proxies=Config.get('proxies')
            )
            if backend_answer.status_code != requests.codes.ok:
                log.warning("request_pdf failed for url {}, data_extract was {}".format(url, data_extract))
            return backend_answer
        except Exception as e:
            log.exception(e)
            log.warning("request_pdf failed for url {}, data_extract was {}".format(url, data_extract))
            raise e

    @staticmethod
    def prepare_xml(extract_as_xml):
        """
        Hook method in order to manipulate xml that is sent to print webservice.

        Args:
            extract_as_xml(xml): Variable containing the xml content for print werbservice.

        Returns:
            str: Data of extract.
        """
        return extract_as_xml
