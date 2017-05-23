# -*- coding: utf-8 -*-
from mako.lookup import TemplateLookup
from pyramid.path import AssetResolver

from pyramid.response import Response
from pyramid_oereb.lib.renderer import Base
from mako import exceptions


class Extract(Base):

    def __init__(self, info):
        """
        Creates a new XML renderer instance for extract rendering.

        :param info: Info object.
        :type info: pyramid.interfaces.IRendererInfo
        """
        a = AssetResolver('pyramid_oereb')
        resolver = a.resolve('lib/renderer/templates/xml')
        self.template_dir = resolver.abspath()
        super(Extract, self).__init__(info)

    def __call__(self, value, system):
        """
        Returns the XML encoded extract, according to the specification.

        :param value: A tuple containing the generated extract record and the params dictionary.
        :type value: tuple
        :param system: The available system properties.
        :type system: dict
        :return: The XML encoded extract.
        :rtype: str
        """
        response = self.get_response(system)
        if isinstance(response, Response) and response.content_type == response.default_content_type:
            response.content_type = 'application/xml'

        self._config_reader_ = self.get_request(system).pyramid_oereb_config_reader
        self._params_ = value[1]
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
                'default_language': str(self._config_reader_.get('default_language')).lower()
            })
            return content
        except:
            response.content_type = 'text/html'
            return exceptions.html_error_template().render()
