# -*- coding: utf-8 -*-
from pyramid.response import Response

from pyramid_oereb.lib.renderer import Base


class Json(Base):
    def __call__(self, value, system):
        """
        Returns the JSON encoded extract, according to the specification.
        :param value: The dictionary containing the extract data.
        :type value: dict
        :param system: The available system properties.
        :type system: dict
        :return: The JSON encoded extract.
        :rtype: str
        """
        response = self.get_response(system)
        if isinstance(response, Response) and response.content_type == response.default_content_type:
            response.content_type = 'application/json'

        return self.__render__(value)

    def __render__(self, extract):
        extract = dict()
        return extract
