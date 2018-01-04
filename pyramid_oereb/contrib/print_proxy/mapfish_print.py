# -*- coding: utf-8 -*-
import subprocess
import sys
import json
import tempfile

import requests
import logging

import time
from shapely.geometry import mapping
from pyramid.httpexceptions import HTTPBadRequest
from pyramid_oereb import Config
from pyramid_oereb.lib.renderer.extract.json_ import Renderer as JsonRenderer
from pyramid_oereb.lib.url import parse_url
if sys.version_info.major == 2:
    import urlparse
else:
    from urllib import parse as urlparse


log = logging.getLogger(__name__)


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
        log.debug("webservice parameter is {}".format(value[1]))

        if value[1].images:
            raise HTTPBadRequest('With image is not allowed in the print')

        self._request = self.get_request(system)

        self.default_lang = Config.get('default_language')
        if 'lang' in self._request.GET:
            self.lang = self._request.GET.get('lang')
        else:
            self.lang = self.default_lang

        # Based on extract record and webservice parameter, render the extract data as JSON
        extract_record = value[0]
        extract_as_dict = self._render(extract_record, value[1])
        feature_geometry = mapping(extract_record.real_estate.limit)

        printable_extract = self.get_printable_extract(extract_as_dict, feature_geometry)

        spec = {
            'layout': Config.get('print', {})['template_name'],
            'outputFormat': 'pdf',
            'lang': self.lang,
            'attributes': printable_extract,
        }

        response = self.get_response(system)

        if self._request.GET.get('getspec', 'no') != 'no':
            response.headers['Content-Type'] = 'application/json; charset=UTF-8'
            return json.dumps(spec, sort_keys=True, indent=4)

        print_result = requests.post(
            urlparse.urljoin(Config.get('print', {})['base_url'] + '/', 'buildreport.pdf'),
            headers=Config.get('print', {})['headers'],
            data=json.dumps(spec)
        )

        if not printable_extract['isReduced'] and print_result.status_code == 200:
            main = tempfile.NamedTemporaryFile(suffix='.pdf')
            main.write(print_result.content)
            main.flush()
            cmd = ['pdftk', main.name]
            temp_files = [main]
            for url in pdf_to_join:
                tmp_file = tempfile.NamedTemporaryFile(suffix='.pdf')
                result = requests.get(url)
                tmp_file.write(result.content)
                tmp_file.flush()
                temp_files.append(tmp_file)
                cmd.append(tmp_file.name)
            out = tempfile.NamedTemporaryFile(suffix='.pdf')
            cmd += ['cat', 'output', out.name]
            sys.stdout.flush()
            time.sleep(0.1)
            subprocess.check_call(cmd)
            content = out.file.read()
        else:
            content = print_result.content

        response.status_code = print_result.status_code
        response.headers = print_result.headers
        if 'Transfer-Encoding' in response.headers:
            del response.headers['Transfer-Encoding']
        if 'Connection' in response.headers:
            del response.headers['Connection']
        return content

    def get_printable_extract(self, extract_dict, feature_geometry):
        """
        Converts an oereb extract into a form suitable for printing by mapfish print.
        """

        log.debug("starting transformation, extract_dict is {}".format(extract_dict))
        log.debug("feature_geometry is {}".format(feature_geometry))

        for attr_name in ['NotConcernedTheme', 'ThemeWithoutData', 'ConcernedTheme']:
            for theme in extract_dict[attr_name]:
                self._localised_text(theme, 'Text')
        self._flatten_object(extract_dict, 'PLRCadastreAuthority')
        self._flatten_object(extract_dict, 'RealEstate')
        del extract_dict['RealEstate_Limit']
        if 'Image' in extract_dict.get('RealEstate_Highlight', {}):
            del extract_dict['RealEstate_Highlight']['Image']

        url, params = parse_url(extract_dict['RealEstate_PlanForLandRegister']['ReferenceWMS'])
        basemap = {
            'type': 'wms',
            'styles': 'default',
            'opacity': 1,
            'baseURL': urlparse.urlunsplit((url.scheme, url.netloc, url.path, None, None)),
            'layers': params['LAYERS'][0].split(','),
            'imageFormat': 'image/png',
            'customParams': {'TRANSPARENT': 'true'},
        }
        extract_dict['baseLayers'] = {'layers': [basemap]}
        extract_dict['legend'] = extract_dict['RealEstate_PlanForLandRegister'].get('LegendAtWeb', '')
        del extract_dict['RealEstate_PlanForLandRegister']  # /definitions/Map

        self._multilingual_m_text(extract_dict, 'GeneralInformation')
        self._multilingual_m_text(extract_dict, 'BaseData')
        for item in extract_dict.get('Glossary', []):
            self._multilingual_text(item, 'Title')
            self._multilingual_text(item, 'Content')
        self._multilingual_text(extract_dict, 'PLRCadastreAuthority_Name')

        pdf_to_join = set()
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
                    'opacity': 1,
                    'styles': 'default',
                    'baseURL': urlparse.urlunsplit((url.scheme, url.netloc, url.path, None, None)),
                    'layers': params['LAYERS'][0].split(','),
                    'imageFormat': 'image/png',
                    'customParams': {'TRANSPARENT': 'true'},
                }, basemap]
            }
            restriction_on_landownership['legend'] = restriction_on_landownership['Map'].get(
                'LegendAtWeb', '')

            # Legend of other visible restriction objects in the topic map
            restriction_on_landownership['OtherLegend'] = restriction_on_landownership['Map'].get(
                'OtherLegend', [])
            for legend_item in restriction_on_landownership['OtherLegend']:
                self._multilingual_text(legend_item, 'LegendText')

            for legend_entry in restriction_on_landownership['OtherLegend']:
                for element in legend_entry.keys():
                    if element not in ['LegendText', 'SymbolRef', 'TypeCode']:
                        del legend_entry[element]

            del restriction_on_landownership['Map']  # /definitions/Map

            for item in restriction_on_landownership.get('Geometry', []):
                self._multilingual_text(item, 'ResponsibleOffice_Name')

            references = {}
            articles = {}
            legal_provisions = {}
            if 'LegalProvisions' in restriction_on_landownership:
                finish = False
                while not finish:
                    finish = True
                    for legal_provision in restriction_on_landownership['LegalProvisions']:
                        if 'Base64TextAtWeb' in legal_provision:
                            del legal_provision['Base64TextAtWeb']
                        if 'Reference' in legal_provision:
                            for reference in legal_provision['Reference']:
                                uid = self._get_element_of_legal_provision_maybe_uid(reference)
                                references[uid] = reference
                            del legal_provision['Reference']
                            finish = False
                        if 'Article' in legal_provision:
                            for article in legal_provision['Article']:
                                uid = self._get_element_of_legal_provision_maybe_uid(article)
                                articles[uid] = article
                            del legal_provision['Article']
                            finish = False
                        uid = self._get_element_of_legal_provision_maybe_uid(legal_provision)
                        legal_provisions[uid] = legal_provision

                del restriction_on_landownership['LegalProvisions']

            restriction_on_landownership['LegalProvisions'] = legal_provisions
            restriction_on_landownership['Reference'] = references
            restriction_on_landownership['Article'] = articles

        # One restriction entry per theme
        theme_restriction = {}
        text_element = [
            'Information', 'Lawstatus_Code', 'Lawstatus_Text', 'ResponsibleOffice_Name',
            'ResponsibleOffice_OfficeAtWeb', 'SymbolRef', 'TypeCode'
        ]
        legend_element = [
            'TypeCode', 'TypeCodelist', 'Area', 'PartInPercent', 'Length', 'SymbolRef', 'Information'
        ]
        for restriction_on_landownership in extract_dict.get('RealEstate_RestrictionOnLandownership', []):
            theme = restriction_on_landownership['Theme_Code']
            geom_type = \
                'Area' if 'Area' in restriction_on_landownership else \
                'Length' if 'Length' in restriction_on_landownership else 'Point'

            if theme not in theme_restriction:
                current = dict(restriction_on_landownership)
                current['Geom_Type'] = geom_type
                theme_restriction[theme] = current

                # Legend
                legend = {}
                for element in legend_element:
                    if element in current:
                        legend[element] = current[element]
                        del current[element]
                    legend['Geom_Type'] = geom_type
                current['Legend'] = [legend]

                # Text
                for element in text_element:
                    if element in current:
                        current[element] = set([current[element]])
                    else:
                        current[element] = set()
                continue
            current = theme_restriction[theme]

            if 'Geom_Type' in current and current['Geom_Type'] != geom_type:
                del current['Geom_Type']

            # Legend
            legend = {}
            for element in legend_element:
                if element in restriction_on_landownership:
                    legend[element] = restriction_on_landownership[element]
                    del restriction_on_landownership[element]
                    legend['Geom_Type'] = geom_type
            current['Legend'].append(legend)

            # Remove in OtherLegend elements that are already in the legend
            current['OtherLegend'] = [other_legend_element
                                      for other_legend_element in current['OtherLegend']
                                      if other_legend_element['SymbolRef'] != legend['SymbolRef']]

            # Number or array
            for element in ['Article', 'LegalProvisions', 'Reference']:
                if current.get(element) is not None and restriction_on_landownership.get(element) is not None:
                    current[element].update(restriction_on_landownership[element])
                elif restriction_on_landownership.get(element) is not None:
                    current[element] = restriction_on_landownership[element]

            # Text
            for element in text_element:
                if element in restriction_on_landownership:
                    current[element].add(restriction_on_landownership[element])

        for restriction_on_landownership in theme_restriction.values():
            for element in text_element:
                restriction_on_landownership[element] = '\n'.join(restriction_on_landownership[element])
            for element in ['Article', 'LegalProvisions', 'Reference']:
                values = list(restriction_on_landownership[element].values())
                self.lpra_flatten(values)
                restriction_on_landownership[element] = values
                if element is 'LegalProvisions':
                    pdf_to_join.update([legal_provision['TextAtWeb'] for legal_provision in values])

        restrictions = list(theme_restriction.values())
        for restriction in restrictions:
            legends = {}
            for legend in restriction['Legend']:
                type_ = legend['TypeCode']
                if type_ in legends:
                    for item in ['Area', 'Length', 'PartInPercent']:
                        if item in legend:
                            if item in legends[type_]:
                                legends[type_][item] += legend[item]
                            else:
                                legends[type_][item] = legend[item]
                else:
                    legends[type_] = legend
            for legend in legends.values():
                for item in ['Area', 'Length']:
                    if item in legend:
                        legend[item] = int(legend[item])
            restriction['Legend'] = list(legends.values())

        extract_dict['RealEstate_RestrictionOnLandownership'] = restrictions
        # End one restriction entry per theme

        for item in extract_dict.get('ExclusionOfLiability', []):
            self._multilingual_text(item, 'Title')
            self._multilingual_text(item, 'Content')

        extract_dict['features'] = {
            'features': {
                'type': 'FeatureCollection',
                'features': [{
                    'type': 'Feature',
                    'geometry': feature_geometry,
                    'properties': {}
                }]
            }
        }
        log.debug("after transformation, extract_dict is {}".format(extract_dict))
        return extract_dict

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

    @staticmethod
    def _get_element_of_legal_provision_maybe_uid(element):
        if element['TextAtWeb'] is not None:
            # If TextAtWeb exists, we want it once it the pdf report.
            return element['TextAtWeb'][0]['Text']
        else:
            # Otherwise, take the Title. It exists for sure, but can be not unique.
            return element['Title'][0]['Text']

    @staticmethod
    def _localised_text(parent, name):
        if name in parent:
            parent[name] = parent[name]['Text']

    def _multilingual_m_text(self, parent, name):
        self._multilingual_text(parent, name)

    def _multilingual_text(self, parent, name):
        if name in parent:
            lang_obj = dict([(e['Language'], e['Text']) for e in parent[name]])
            parent[name] = lang_obj[self._language]
