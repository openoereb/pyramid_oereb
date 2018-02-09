# -*- coding: utf-8 -*-
from mako.lookup import TemplateLookup
from pyramid.path import AssetResolver

from pyramid.response import Response

from pyramid_oereb.lib.records.documents import LegalProvisionRecord
from pyramid_oereb.lib.renderer import Base
from mako import exceptions

from pyramid_oereb.views.webservice import Parameter


class Renderer(Base):

    def __init__(self, info):
        """
        Creates a new XML renderer instance for extract rendering.

        Args:
            info (pyramid.interfaces.IRendererInfo): Info object.
        """
        a = AssetResolver('pyramid_oereb')
        resolver = a.resolve('lib/renderer/extract/templates/xml')
        self.template_dir = resolver.abspath()
        self._gml_id = 0
        super(Renderer, self).__init__(info)

    def __call__(self, value, system):
        """
        Returns the XML encoded extract, according to the specification.

        Args:
            value (tuple): A tuple containing the generated extract record and the params
                dictionary.
            system (dict): The available system properties.

        Returns:
            str: The XML encoded extract.
        """
        self._request = self.get_request(system)
        response = self.get_response(system)
        if isinstance(response, Response) and response.content_type == response.default_content_type:
            response.content_type = 'application/xml'

        self._params_ = value[1]
        if not isinstance(self._params_, Parameter):
            raise TypeError('Missing parameter definition; Expected {0}, got {1} instead'.format(
                Parameter,
                self._params_.__class__
            ))
        if self._params_.language:
            self._language = str(self._params_.language).lower()

        templates = TemplateLookup(
            directories=[self.template_dir],
            output_encoding='utf-8',
            input_encoding='utf-8'
        )
        template = templates.get_template('extract.xml')
        try:
            content = template.render(**{
                'extract': value[0],
                'params': value[1],
                'sort_by_localized_text': self.sort_by_localized_text,
                'localized': self.get_localized_text,
                'multilingual': self.get_multilingual_text,
                'request': self._request,
                'get_symbol_ref': self.get_symbol_ref,
                'get_gml_id': self._get_gml_id,
                'get_document_type': self._get_document_type,
                'date_format': '%Y-%m-%dT%H:%M:%S'
            })
            return content
        except ValueError as e:
            # TODO: use error mapping to provide HTTP errors
            raise e
        except Exception:
            response.content_type = 'text/html'
            return exceptions.html_error_template().render()

    def _get_gml_id(self):
        """
        Returns the next GML ID.

        Returns:
             int: The next GML ID.

        """
        self._gml_id += 1
        return 'gml{0}'.format(self._gml_id)

    @classmethod
    def _get_document_type(cls, document):
        """
        Returns the documents xsi type.

        Args:
            document (pyramid_oereb.lib.records.documents.DocumentRecord): The document record.

        Returns:
            str: The documents xsi type

        """
        if isinstance(document, LegalProvisionRecord):
            return 'data:LegalProvisions'
        return 'data:Document'
