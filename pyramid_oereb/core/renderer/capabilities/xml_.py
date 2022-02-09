# -*- coding: utf-8 -*-
from mako.lookup import TemplateLookup
from pyramid.path import AssetResolver

from pyramid.response import Response

from pyramid_oereb.core.renderer import Base
from mako import exceptions


class Renderer(Base):

    def __init__(self, info):
        """
        Creates a new XML renderer instance for versions rendering.

        Args:
            info (pyramid.interfaces.IRendererInfo): Info object.
        """
        a = AssetResolver('pyramid_oereb')
        resolver = a.resolve('core/renderer/capabilities/templates/xml')
        self.template_dirs = [resolver.abspath()]
        resolver = a.resolve('core/renderer/extract/templates/xml')
        self.template_dirs.append(resolver.abspath())
        super(Renderer, self).__init__(info)

    def __call__(self, value, system):
        """
        Returns the XML encoded versions response according to the specification.

        Args:
            value (dict): A dictionary containing the versions data.
            system (dict): The available system properties.

        Returns:
            str: The XML encoded versions response.
        """
        self._request = self.get_request(system)
        response = self.get_response(system)
        if isinstance(response, Response) and response.content_type == response.default_content_type:
            response.content_type = 'application/xml'

        templates = TemplateLookup(
            directories=self.template_dirs,
            output_encoding='utf-8',
            input_encoding='utf-8'
        )
        template = templates.get_template('capabilities.xml')
        try:
            content = template.render(**{
                'data': value,
                'sort_by_localized_text': self.sort_by_localized_text,
                'localized': self.get_localized_text,
                'multilingual': self.get_multilingual_text,
                'get_localized_image': self.get_localized_image,
                'request': self._request,
                'get_symbol_ref': self.get_symbol_ref
            })
            return content
        except Exception:
            response.content_type = 'text/html'
            return exceptions.html_error_template().render()
