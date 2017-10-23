# -*- coding: utf-8 -*-
from mako.lookup import TemplateLookup
from pyramid.path import AssetResolver

from pyramid.response import Response

from pyramid_oereb.lib.renderer import Base
from mako import exceptions


class Renderer(Base):

    def __init__(self, info):
        """
        Creates a new XML renderer instance for versions rendering.

        Args:
            info (pyramid.interfaces.IRendererInfo): Info object.
        """
        a = AssetResolver('pyramid_oereb')
        resolver = a.resolve('lib/renderer/versions/templates/xml')
        self.template_dir = resolver.abspath()
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
        response = self.get_response(system)
        if isinstance(response, Response) and response.content_type == response.default_content_type:
            response.content_type = 'application/xml'

        templates = TemplateLookup(
            directories=[self.template_dir],
            output_encoding='utf-8',
            input_encoding='utf-8'
        )
        template = templates.get_template('versions.xml')
        try:
            content = template.render(**{
                'data': value
            })
            return content
        except Exception:
            response.content_type = 'text/html'
            return exceptions.html_error_template().render()
