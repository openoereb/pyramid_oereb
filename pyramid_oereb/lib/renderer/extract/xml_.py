# -*- coding: utf-8 -*-
from mako.lookup import TemplateLookup
from pyramid.path import AssetResolver

from pyramid.response import Response

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
                'localized': self.get_localized_text,
                'multilingual': self.get_multilingual_text,
                'request': self._request,
                'get_symbol_ref': self.get_symbol_ref
            })
            return content
        except ValueError as e:
            # TODO: use error mapping to provide HTTP errors
            raise e
        except Exception:
            response.content_type = 'text/html'
            return exceptions.html_error_template().render()
