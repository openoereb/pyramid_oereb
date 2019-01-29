# -*- coding: utf-8 -*-
import subprocess
import sys
import json
import tempfile

import requests
import logging

import time

from datetime import datetime
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
            self._multilingual_text(item, 'Abbreviation')

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
        log.debug("Parameter webservice is {}".format(value[1]))

        if value[1].images:
            raise HTTPBadRequest('With image is not allowed in the print')

        self._request = self.get_request(system)
        # If language present in request, use that. Otherwise, keep language from base class
        if 'lang' in self._request.GET:
            self._language = self._request.GET.get('lang')

        # Based on extract record and webservice parameter, render the extract data as JSON
        extract_record = value[0]
        extract_as_dict = self._render(extract_record, value[1])
        feature_geometry = mapping(extract_record.real_estate.limit)
        pdf_to_join = set()

        self.convert_to_printable_extract(extract_as_dict, feature_geometry, pdf_to_join)

        print_config = Config.get('print', {})

        extract_as_dict['Display_RealEstate_SubunitOfLandRegister'] = print_config.get(
            'display_real_estate_subunit_of_land_register', True
        )

        spec = {
            'layout': Config.get('print', {})['template_name'],
            'outputFormat': 'pdf',
            'lang': self._language,
            'attributes': extract_as_dict,
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

        if not extract_as_dict['isReduced'] and print_result.status_code == 200:
            main = tempfile.NamedTemporaryFile(suffix='.pdf')
            main.write(print_result.content)
            main.flush()
            cmd = ['pdftk', main.name]
            temp_files = [main]
            for url in pdf_to_join:
                result = requests.get(url)
                content_type = result.headers.get('content-type')
                log.debug("document url: " + url + " => content_type: " + content_type)
                if content_type != 'application/pdf':
                    msg = "Skipped document inclusion (url: '{}') because content_type: '{}'"
                    log.warn(msg.format(url, content_type))
                    continue
                tmp_file = tempfile.NamedTemporaryFile(suffix='.pdf')
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

    def convert_to_printable_extract(self, extract_dict, feature_geometry, pdf_to_join):
        """
        Converts an oereb extract into a form suitable for printing by mapfish print.

        Args:
            extract_dict: the oereb extract, will get converted by this function into a form
                            convenient for mapfish-print
            feature_geometry: the geometry for this extract, will get added to the extract information
            pdf_to_join: a set of additional information for the pdf, will get filled by this function
        """

        log.debug("Starting transformation, extract_dict is {}".format(extract_dict))
        log.debug("Parameter feature_geometry is {}".format(feature_geometry))

        creation_date = datetime.strptime(extract_dict['CreationDate'], '%Y-%m-%dT%H:%M:%S')
        extract_dict['Footer'] = '   '.join([
            creation_date.strftime('%d.%m.%Y'),
            creation_date.strftime('%H:%M:%S'),
            extract_dict['ExtractIdentifier']
        ])
        extract_dict['CreationDate'] = creation_date.strftime('%d.%m.%Y')

        for attr_name in ['NotConcernedTheme', 'ThemeWithoutData', 'ConcernedTheme']:
            for theme in extract_dict[attr_name]:
                self._localised_text(theme, 'Text')
        self._flatten_object(extract_dict, 'PLRCadastreAuthority')
        self._flatten_object(extract_dict, 'RealEstate')
        if 'Image' in extract_dict.get('RealEstate_Highlight', {}):
            del extract_dict['RealEstate_Highlight']['Image']

        main_page_url, main_page_params = \
            parse_url(extract_dict['RealEstate_PlanForLandRegisterMainPage']['ReferenceWMS'])
        base_url = urlparse.urlunsplit((main_page_url.scheme,
                                        main_page_url.netloc,
                                        main_page_url.path,
                                        None,
                                        None))
        main_page_basemap = {
            'type': 'wms',
            'styles': 'default',
            'opacity': extract_dict['RealEstate_PlanForLandRegisterMainPage'].get('layerOpacity', 0.6),
            'baseURL': base_url,
            'layers': main_page_params['LAYERS'][0].split(','),
            'imageFormat': 'image/png',
            'customParams': {'TRANSPARENT': 'true'},
        }
        extract_dict['baseLayers'] = {'layers': [main_page_basemap]}
        url, params = parse_url(extract_dict['RealEstate_PlanForLandRegister']['ReferenceWMS'])
        basemap = {
            'type': 'wms',
            'styles': 'default',
            'opacity': extract_dict['RealEstate_PlanForLandRegister'].get('layerOpacity', 0.6),
            'baseURL': urlparse.urlunsplit((url.scheme, url.netloc, url.path, None, None)),
            'layers': params['LAYERS'][0].split(','),
            'imageFormat': 'image/png',
            'customParams': {'TRANSPARENT': 'true'},
        }
        del extract_dict['RealEstate_PlanForLandRegister']  # /definitions/Map

        self._multilingual_m_text(extract_dict, 'GeneralInformation')
        self._multilingual_m_text(extract_dict, 'BaseData')
        self._multilingual_m_text(extract_dict, 'Certification')

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
                    'opacity': restriction_on_landownership['Map'].get('layerOpacity', 0.6),
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
                for element in list(legend_entry.keys()):
                    if element not in ['LegendText', 'SymbolRef', 'TypeCode']:
                        del legend_entry[element]

            del restriction_on_landownership['Map']  # /definitions/Map

            for item in restriction_on_landownership.get('Geometry', []):
                self._multilingual_text(item, 'ResponsibleOffice_Name')

            legal_provisions = {}
            laws = {}
            hints = {}

            if 'LegalProvisions' in restriction_on_landownership:
                finish = False
                while not finish:
                    finish = True
                    for legal_provision in restriction_on_landownership['LegalProvisions']:
                        if 'Base64TextAtWeb' in legal_provision:
                            del legal_provision['Base64TextAtWeb']
                        if 'Reference' in legal_provision:
                            for reference in legal_provision['Reference']:
                                self._categorize_documents(reference, legal_provisions, laws, hints)
                            del legal_provision['Reference']
                            finish = False
                        if 'Article' in legal_provision:
                            for article in legal_provision['Article']:
                                self._categorize_documents(article, legal_provisions, laws, hints)
                            del legal_provision['Article']
                            finish = False

                        self._categorize_documents(legal_provision, legal_provisions, laws, hints)

                del restriction_on_landownership['LegalProvisions']

            restriction_on_landownership['LegalProvisions'] = legal_provisions
            restriction_on_landownership['Laws'] = laws
            restriction_on_landownership['Hints'] = hints

        # One restriction entry per theme
        theme_restriction = {}
        text_element = [
            'Information', 'Lawstatus_Code', 'Lawstatus_Text', 'ResponsibleOffice_Name',
            'ResponsibleOffice_OfficeAtWeb', 'SymbolRef', 'TypeCode'
        ]
        legend_element = [
            'TypeCode', 'TypeCodelist', 'AreaShare', 'PartInPercent', 'LengthShare',
            'SymbolRef', 'Information'
        ]
        split_sub_themes = Config.get('print', {}).get('split_sub_themes', False)
        for restriction_on_landownership in extract_dict.get('RealEstate_RestrictionOnLandownership', []):
            theme = restriction_on_landownership['Theme_Code']

            if split_sub_themes:
                if 'SubTheme' in restriction_on_landownership:
                    theme = theme + '_' + restriction_on_landownership['SubTheme']
                    restriction_on_landownership['Split_SubTheme'] = True

            geom_type = \
                'AreaShare' if 'AreaShare' in restriction_on_landownership else \
                'LengthShare' if 'LengthShare' in restriction_on_landownership else 'NrOfPoints'

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
            for element in ['Laws', 'LegalProvisions', 'Hints']:
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
            for element in ['Laws', 'LegalProvisions', 'Hints']:
                values = list(restriction_on_landownership[element].values())
                self.lpra_flatten(values)
                restriction_on_landownership[element] = values
                if element == 'LegalProvisions':
                    pdf_to_join.update([legal_provision['TextAtWeb'] for legal_provision in values])

        restrictions = list(theme_restriction.values())
        for restriction in restrictions:
            legends = {}
            for legend in restriction['Legend']:
                type_ = legend['TypeCode']
                if type_ in legends:
                    for item in ['AreaShare', 'LengthShare', 'PartInPercent']:
                        if item in legend:
                            if item in legends[type_]:
                                legends[type_][item] += legend[item]
                            else:
                                legends[type_][item] = legend[item]
                else:
                    legends[type_] = legend
            for legend in legends.values():
                for item in ['AreaShare', 'LengthShare']:
                    if item in legend:
                        legend[item] = legend[item]
            # After transformation, get the new legend entries, sorted by TypeCode
            transformed_legend = \
                list([transformed_entry for (key, transformed_entry) in sorted(legends.items())])
            restriction['Legend'] = transformed_legend

        sorted_restrictions = []
        if split_sub_themes:
            # sort sub themes if sub theme splitting is enabled
            sorted_restrictions = self._sort_sub_themes(restrictions)
        else:
            # default sorting
            for theme in Config.get_themes():
                for restriction in restrictions:
                    if theme.code == restriction.get('Theme_Code'):
                        sorted_restrictions.append(restriction)

        extract_dict['RealEstate_RestrictionOnLandownership'] = sorted_restrictions
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

        # Reformat land registry area
        extract_dict['RealEstate_LandRegistryArea'] = u'{0} m²'.format(
            extract_dict['RealEstate_LandRegistryArea']
        )

        # Reformat AreaShare, LengthShare and part in percent values
        for restriction in extract_dict['RealEstate_RestrictionOnLandownership']:
            for legend in restriction['Legend']:
                if 'LengthShare' in legend:
                    legend['LengthShare'] = '{0} m'.format(legend['LengthShare'])
                if 'AreaShare' in legend:
                    legend['AreaShare'] = u'{0} m²'.format(legend['AreaShare'])
                if 'PartInPercent' in legend:
                    legend['PartInPercent'] = '{0}%'.format(legend['PartInPercent'])

        log.debug("After transformation, extract_dict is {}".format(extract_dict))
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
    def _categorize_documents(document, legal_provisions, laws, hints):
        """
        Categorize document by their documentType (LegalProvision, Law or Hint)

        Args:
            dcoument (dict): The document type as dictionary.
            legal_provisions (dict): The legal_provisions dictionary to fill.
            laws (dict): The laws dictionary to fill.
            hints (dict): The Hints dictionary to fill.
        """
        uid = Renderer._get_element_of_legal_provision_maybe_uid(document)
        documentType = document.get('DocumentType')
        if documentType is None:
            error_msg = "mandatory attribute document_type is missing in document " \
                        ": {}".format(document)
            log.error(error_msg)
            raise AttributeError(error_msg)

        if documentType == 'LegalProvision':
            legal_provisions[uid] = document
        elif documentType == 'Law':
            laws[uid] = document
        else:
            hints[uid] = document

    @staticmethod
    def _get_element_of_legal_provision_maybe_uid(element):
        """
        Make a unique key string out of title and TextAtWeb. This is necessary to satisfy the KBS's theme.
        There it can happen, that we get different titles with the same URL. This way we keep even them.

        Args:
            element (dict): The document type as dictionary.

        Returns:
            str: The constructed unique key made of Title and TextAtWeb
        """
        unique_key = []
        if element['TextAtWeb'] is not None:
            # If TextAtWeb exists, we want it for uniqueness too.
            unique_key.append(element['TextAtWeb'][0]['Text'])
        unique_key.append(element['Title'][0]['Text'])
        return '_'.join(unique_key)

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

    def _sort_sub_themes(self, restrictions):
        # split restrictions by theme codes
        split_by_theme_code = self._split_restrictions_by_theme_code(restrictions)

        # sort sub themes of the same theme
        for theme_code in split_by_theme_code:
            sub_themes = []
            non_sub_themes = []
            for restriction in split_by_theme_code[theme_code]:
                if restriction.get('Split_SubTheme', False):
                    sub_themes.append(restriction)
                else:
                    non_sub_themes.append(restriction)
            # only sort if there are multiple sub themes
            if len(sub_themes) > 1:
                sorter, params = self._get_sorter(theme_code)
                sub_themes = sorter.sort(sub_themes, params)
            split_by_theme_code[theme_code] = non_sub_themes + sub_themes

        # sort + flatten the splitted themes again
        sorted_restrictions = []
        for theme in Config.get_themes():
            if theme.code in split_by_theme_code:
                sorted_restrictions += split_by_theme_code[theme.code]

        return sorted_restrictions

    @staticmethod
    def _split_restrictions_by_theme_code(restrictions):
        """
        Args:
            restrictions (list): array of restrictions

        Returns:
            (dict) restrictions split up by theme code
        """
        split_by_theme_code = {}
        for restriction in restrictions:
            theme_code = restriction.get('Theme_Code')
            if theme_code in split_by_theme_code:
                split_by_theme_code[theme_code].append(restriction)
            else:
                split_by_theme_code[theme_code] = [restriction]
        return split_by_theme_code

    @staticmethod
    def _load_sorter(module, class_name):
        """
        Dynamically loads a (sorter) class from a module.

        Args:
            module (str): Module name to load
            class_name (str): Class name to load

        Returns:
            (object) Requested (sorter) class
        """
        sorter_module = __import__(module, fromlist=[class_name])
        sorter = getattr(sorter_module, class_name)
        return sorter

    @staticmethod
    def _get_sorter(theme_code):
        """
        Returns the sub theme sorter for the given theme_code.

        Args:
            theme_code (str): theme_code

        Returns:
            sorter: Sub theme sorter object
            params (dict): parameters for the sorter (from theme configuration)
        """
        sorter_config = Config.get_sub_theme_sorter_config(theme_code)
        sorter = Renderer._load_sorter(sorter_config['module'], sorter_config['class_name'])
        params = sorter_config.get('params', {})
        return sorter, params
