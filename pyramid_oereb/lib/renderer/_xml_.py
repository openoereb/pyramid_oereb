# -*- coding: utf-8 -*-
from StringIO import StringIO
from lxml import etree
import json
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
            response.content_type = 'application/xml'

        self._config_reader_ = self.get_request(system).pyramid_oereb_config_reader
        self._language_ = str(self._config_reader_.get('default_language')).lower()
        self._params_ = value[1]

        return self.create_xml_extract(self.__render__(value[0]))

    def create_xml_extract(self, extract_dict):
        root = etree.Element("GetExtractByIdResponse")
        extract = etree.Element("Extract")
        root.append(extract)
        self.unpack(extract, extract_dict)
        return etree.tostring(root, xml_declaration=True, encoding='utf-8', pretty_print=True)

    def unpack(self, parent, dictionary):
        """
        Simple unwrapping method to create XML elements out of dict structure via lxml library.
        :param parent: The parent lxml element which the snippet should be added to.
        :type parent: lxml.etree.Element
        :param dictionary: The python dictionary snippet which has to be unwrapped.
        :type dictionary: dict
        :return:
        """
        for key, value in dictionary.iteritems():
            if isinstance(value, dict):
                new_parent = etree.Element(key)
                parent.append(new_parent)
                self.unpack(new_parent, value)
            elif isinstance(value, list):
                for element in value:
                    new_parent = etree.Element(key)
                    parent.append(new_parent)
                    self.unpack(new_parent, element)
            else:
                child = etree.Element(key)
                if isinstance(value, bool):
                    # use json dumps to have safe type conversion
                    json_representation = json.dumps({'converted': value})
                    cleaned_representation = json_representation.replace('{', '').replace('}', '')
                    key_value = cleaned_representation.split(':')
                    converted_value = key_value[1]
                    value = converted_value
                child.text = unicode(value)
                parent.append(child)
