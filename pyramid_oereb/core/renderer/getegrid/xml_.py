# -*- coding: utf-8 -*-
from mako.lookup import TemplateLookup
from pyramid.path import AssetResolver

from pyramid.response import Response

from pyramid_oereb.core.renderer import Base
from pyramid_oereb.core.views.webservice import Parameter
from mako import exceptions


class Renderer(Base):

    def __init__(self, info):
        """
        Creates a new XML renderer instance for versions rendering.

        Args:
            info (pyramid.interfaces.IRendererInfo): Info object.
        """
        a = AssetResolver('pyramid_oereb')
        resolver = a.resolve('core/renderer/getegrid/templates/xml')
        geom_resolver = a.resolve('core/renderer/extract/templates/xml')
        self.template_dirs = [resolver.abspath(), geom_resolver.abspath()]
        self._gml_id = 0
        super(Renderer, self).__init__(info)

    def __call__(self, value, system):
        """
        Returns the XML encoded versions response according to the specification.

        Args:
            value (tuple): A tuple containing the real estates and the params
                dictionary.
            system (dict): The available system properties.

        Returns:
            str: The XML encoded versions response.
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

        templates = TemplateLookup(
            directories=self.template_dirs,
            output_encoding='utf-8',
            input_encoding='utf-8'
        )
        template = templates.get_template('getegrid.xml')
        try:
            content = template.render(**{
                'data': value[0],
                'params': self._params_,
                'sort_by_localized_text': self.sort_by_localized_text,
                'localized': self.get_localized_text,
                'multilingual': self.get_multilingual_text,
                'get_localized_image': self.get_localized_image,
                'request': self._request
            })
            return content
        except Exception:
            response.content_type = 'text/html'
            return exceptions.html_error_template().render()
