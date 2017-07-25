# -*- coding: utf-8 -*-

import sys
import json
import requests

import logging

from shapely.geometry import mapping
from pyramid.httpexceptions import HTTPBadRequest

from pyramid_oereb import Config
from pyramid_oereb.lib.renderer.extract.json_ import Renderer
if sys.version_info.major == 2:
    import urlparse
else:
    from urllib import parse as urlparse


log = logging.getLogger('pyramid_oereb')


class PrintRenderer(Renderer):

    def __call__(self, value, system):
        """
        Returns the JSON encoded extract, according to the specification.

        Args:
            value (tuple): A tuple containing the generated extract record and the params
                dictionary.
            system (dict): The available system properties.

        Returns:
            str: The JSON encoded extract.
        """

        if value[1].images:
            return HTTPBadRequest("With image is not allowed in the print")

        self._request = self.get_request(system)

        self.default_lang = Config.get('default_language')
        if 'lang' in self._request.GET:
            self.lang = self._request.GET.get('lang')
        else:
            self.lang = self.default_lang

        extract_dict = self._render(value[0], value[1])
        for attr_name in ['NotConcernedTheme', 'ThemeWithoutData', 'ConcernedTheme']:
            for theme in extract_dict[attr_name]:
                self._localised_text(theme, 'Text')
        self._flatten_object(extract_dict, 'PLRCadastreAuthority')
        self._flatten_object(extract_dict, 'RealEstate')
        self._multilingual_m_text(extract_dict, 'GeneralInformation')
        self._multilingual_m_text(extract_dict, 'BaseData')
        for item in extract_dict.get('Glossary', []):
            self._multilingual_text(item, 'Title')
            self._multilingual_text(item, 'Content')
        self._multilingual_text(extract_dict, 'PLRCadastreAuthority_Name')
        for restriction_on_landownership in extract_dict.get('RealEstate_RestrictionOnLandownership', []):
            self._flatten_object(restriction_on_landownership, 'Lawstatus')
            self._flatten_object(restriction_on_landownership, 'Theme')
            self._flatten_object(restriction_on_landownership, 'ResponsibleOffice')
            self._flatten_array_object(restriction_on_landownership, 'Geometry', 'ResponsibleOffice')
            self._localised_text(restriction_on_landownership, 'Theme_Text')
            self._localised_text(restriction_on_landownership, 'Lawstatus_Text')
            self._multilingual_m_text(restriction_on_landownership, 'Information')
            self._multilingual_text(restriction_on_landownership, 'ResponsibleOffice_Name')
            for item in restriction_on_landownership.get('Geometry', []):
                self._multilingual_text(item, 'ResponsibleOffice_Name')

            legal_provisions = []
            legal_provisions += restriction_on_landownership.get('LegalProvisions', [])
            finish = False
            while finish:
                finish = True
                for legal_provision in legal_provisions:
                    if 'Reference' in legal_provision:
                        legal_provisions += legal_provision['Reference']
                        del legal_provision['Reference']
                        finish = False
                    if 'Article' in legal_provision:
                        legal_provisions += legal_provision['Article']
                        del legal_provision['Article']
                        finish = False
            restriction_on_landownership['LegalProvisions'] = legal_provisions
            for item in restriction_on_landownership.get('LegalProvisions', []):
                self._flatten_object(item, 'Lawstatus')
                self._localised_text(item, 'Lawstatus_Text')
                self._flatten_object(item, 'ResponsibleOffice')
                self._multilingual_text(item, 'ResponsibleOffice_Name')
                self._multilingual_text(item, 'TextAtWeb')

            for item in restriction_on_landownership.get('LegalProvisions', []):
                self._multilingual_m_text(item, 'Text')
                self._multilingual_text(item, 'Title')
                self._multilingual_text(item, 'OfficialTitle')
                self._multilingual_text(item, 'Abbrevation')

        for item in extract_dict.get('ExclusionOfLiability', []):
            self._multilingual_text(item, 'Title')
            self._multilingual_text(item, 'Content')

        extract_dict["features"] = {
            "features": {
                "type": "FeatureCollection",
                "features": [{
                    "type": "Feature",
                    "geometry": mapping(value[0].real_estate.limit),
                    "properties": {}
                }]
            }
        }
        spec = {
            "layout": "A4 portrait",
            "outputFormat": "pdf",
            "attributes": extract_dict,
        }

        response = self.get_response(system)

        if self._request.GET.get('getspec', 'no') != 'no':
            response.headers['Content-Type'] = 'application/json; charset=UTF-8'
            return json.dumps(spec, sort_keys=True, indent=4)

        print_result = requests.post(
            urlparse.urljoin(Config.get('print', {})['base_url'] + "/", 'buildreport.pdf'),
            headers={
                "Content-Type": "application/json; charset=UTF-8"
            },
            data=json.dumps(spec)
        )
        response.status_code = print_result.status_code
        response.headers = print_result.headers
        if 'Transfer-Encoding' in response.headers:
            del response.headers['Transfer-Encoding']
        if 'Connection' in response.headers:
            del response.headers['Connection']
        return print_result.content

    def _flatten_array_object(self, parent, array_name, object_name):
        if array_name in parent:
            for item in parent[array_name]:
                self._flatten_object(item, object_name)

    @staticmethod
    def _flatten_object(parent, name):
        if name in parent:
            for key, value in parent[name].items():
                parent['{}_{}'.format(name, key)] = value
            del parent[name]

    def _localised_text(self, parent, name):
        if name in parent:
            parent[name] = parent[name]['Text']

    def _multilingual_m_text(self, parent, name):
        self._multilingual_text(parent, name)

    def _multilingual_text(self, parent, name):
        if name in parent:
            # lang_obj = dict([(e['Language'], e['Text']) for e in parent[name]])
            # lang = self.lang if self.lang in lang_obj else self.default_lang
            # parent[name] = lang_obj[lang]
            parent[name] = parent[name][0]['Text']
