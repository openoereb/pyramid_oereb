# -*- coding: utf-8 -*-
from json import dumps
from pyramid.response import Response
from pyramid_oereb.lib.renderer import Base


class Extract(Base):
    def __init__(self, info):
        """
        Creates a new JSON renderer instance for extract rendering.

        :param info: Info object.
        :type info: pyramid.interfaces.IRendererInfo
        """
        super(Extract, self).__init__(info)

    def __call__(self, value, system):
        """
        Returns the JSON encoded extract, according to the specification.

        :param value: A tuple containing the generated extract record and the params dictionary.
        :type value: tuple
        :param system: The available system properties.
        :type system: dict
        :return: The JSON encoded extract.
        :rtype: str
        """
        response = self.get_response(system)
        if isinstance(response, Response) and response.content_type == response.default_content_type:
            response.content_type = 'application/json'

        self._config_reader_ = self.get_request(system).pyramid_oereb_config_reader
        self._language_ = str(self._config_reader_.get('default_language')).lower()
        self._params_ = value[1]

        return dumps(self.__render__(value[0]))
