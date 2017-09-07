# -*- coding: utf-8 -*-
import sys
import json
import requests
import logging

from shapely.geometry import mapping
from pyramid.httpexceptions import HTTPBadRequest
from pyramid_oereb import Config
from pyramid_oereb.lib.renderer.extract.json_ import Renderer as JsonRenderer
from pyramid_oereb.lib.url import parse_url
if sys.version_info.major == 2:
    import urlparse
else:
    from urllib import parse as urlparse


log = logging.getLogger('pyramid_oereb')


class Renderer(JsonRenderer):

    def lpra_flatten(self, items):
        for item in items:
            self._flatten_object(item, 'Lawstatus')
            self._localised_text(item, 'Lawstatus_Text')
            self._flatten_object(item, 'ResponsibleOffice')
            self._multilingual_text(item, 'ResponsibleOffice_Name')
            self._multilingual_text(item, 'TextAtWeb')

            self._multilingual_m_text(item, 'Text')
            self._multilingual_text(item, 'Title')
            self._multilingual_text(item, 'OfficialTitle')
            self._multilingual_text(item, 'Abbrevation')

    def __call__(self, value, system):
        """
        Implements a subclass of pyramid_oereb.lib.renderer.extract.json_.Renderer to create a print result
        out of a json. The json extract is reformatted to fit the structure of mapfish print.

        Args:
            value (tuple): A tuple containing the generated extract record and the params
                dictionary.
            system (dict): The available system properties.

        Returns:
            buffer: The pdf content as received from configured mapfish print instance url.
        """

        if value[1].images:
            raise HTTPBadRequest("With image is not allowed in the print")

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

        url, params = parse_url(extract_dict['RealEstate_PlanForLandRegister']['ReferenceWMS'])
        extract_dict['baseLayers'] = {
            'layers': [{
                'type': 'wms',
                'baseURL': urlparse.urlunsplit((url.scheme, url.netloc, url.path, None, None)),
                'layers': params['LAYERS'][0].split(','),
                'imageFormat': 'image/png',
            }]
        }
        extract_dict['legend'] = extract_dict['RealEstate_PlanForLandRegister'].get('LegendAtWeb', '')
        del extract_dict['RealEstate_PlanForLandRegister']  # /definitions/Map

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

            url, params = parse_url(restriction_on_landownership['Map']['ReferenceWMS'])
            restriction_on_landownership['baseLayers'] = {
                'layers': [{
                    'type': 'wms',
                    'baseURL': urlparse.urlunsplit((url.scheme, url.netloc, url.path, None, None)),
                    'layers': params['LAYERS'][0].split(','),
                    'imageFormat': 'image/png',
                }]
            }
            restriction_on_landownership['legend'] = restriction_on_landownership['Map'].get(
                'LegendAtWeb', '')
            del restriction_on_landownership['Map']  # /definitions/Map

            for item in restriction_on_landownership.get('Geometry', []):
                self._multilingual_text(item, 'ResponsibleOffice_Name')

            legal_provisions = []
            reference = []
            article = []
            if 'LegalProvisions' in restriction_on_landownership:
                finish = False
                while not finish:
                    finish = True
                    for legal_provision in restriction_on_landownership['LegalProvisions']:
                        if 'Reference' in legal_provision:
                            reference += legal_provision['Reference']
                            del legal_provision['Reference']
                            finish = False
                        if 'Article' in legal_provision:
                            article += legal_provision['Article']
                            del legal_provision['Article']
                            finish = False

                legal_provisions += restriction_on_landownership['LegalProvisions']
                del restriction_on_landownership['LegalProvisions']

            self.lpra_flatten(legal_provisions)
            self.lpra_flatten(reference)
            self.lpra_flatten(article)
            restriction_on_landownership['LegalProvisions'] = legal_provisions
            restriction_on_landownership['Reference'] = reference
            restriction_on_landownership['Article'] = article

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
            "layout": Config.get('print', {})['template_name'],
            "outputFormat": "pdf",
            "lang": self.lang,
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
