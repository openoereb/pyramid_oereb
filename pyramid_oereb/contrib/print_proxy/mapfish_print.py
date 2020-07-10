# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import io
import json
import logging
import requests
from shapely.geometry import mapping
import subprocess
import sys
import tempfile
import time
from urllib import parse as urlparse

from pyramid.httpexceptions import HTTPBadRequest
from pyramid_oereb import Config
from pyramid_oereb.lib.renderer.extract.json_ import Renderer as JsonRenderer
from pyramid_oereb.lib.url import parse_url
from pyramid.httpexceptions import HTTPInternalServerError
from PyPDF2 import PdfFileReader
from PyPDF2.utils import PdfReadError
from .toc_pages import TocPages


log = logging.getLogger(__name__)

LEGEND_ELEMENT_SORT_ORDER = [
    'AreaShare',
    'LengthShare',
    'NrOfPoints'
]


class Renderer(JsonRenderer):

    def lpra_flatten(self, items):
        for item in items:
            self._flatten_object(item, 'Lawstatus')
            self._localised_text(item, 'Lawstatus_Text')
            self._flatten_object(item, 'ResponsibleOffice')
            self._multilingual_text(item, 'ResponsibleOffice_Name')
            self._multilingual_text_at_web(item)

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

        # Create a lower case GET dict to be able to accept all cases of upper and lower case writing
        self._lowercase_GET_dict = dict((k.lower(), v.lower()) for k, v in self._request.GET.iteritems())

        # If a language is specified in the request, use it. Otherwise, use the language from base class
        self._fallback_language = Config.get('default_language')
        if 'lang' in self._lowercase_GET_dict:
            self._language = self._lowercase_GET_dict.get('lang')

        # Based on extract record and webservice parameter, render the extract data as JSON
        extract_record = value[0]
        extract_as_dict = self._render(extract_record, value[1])
        feature_geometry = mapping(extract_record.real_estate.limit)
        pdf_to_join = set()

        if Config.get('print', {}).get('compute_toc_pages', False):
            extract_as_dict['nbTocPages'] = TocPages(extract_as_dict).getNbPages()
        else:
            extract_as_dict['nbTocPages'] = 1

        self.convert_to_printable_extract(extract_as_dict, feature_geometry, pdf_to_join)

        print_config = Config.get('print', {})

        extract_as_dict['Display_RealEstate_SubunitOfLandRegister'] = print_config.get(
            'display_real_estate_subunit_of_land_register', True
        )

        extract_as_dict['Display_Certification'] = print_config.get(
            'display_certification', True
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
        pdf_url = urlparse.urljoin(Config.get('print', {})['base_url'] + '/', 'buildreport.pdf')
        pdf_headers = Config.get('print', {})['headers']
        print_result = requests.post(
            pdf_url,
            headers=pdf_headers,
            data=json.dumps(spec)
        )
        try:
            if Config.get('print', {}).get('compute_toc_pages', False):
                with io.BytesIO() as pdf:
                    pdf.write(print_result.content)
                    pdf_reader = PdfFileReader(pdf)
                    x = []
                    for i in range(len(pdf_reader.getOutlines())):
                        x.append(pdf_reader.getOutlines()[i]['/Page']['/StructParents'])
                    try:
                        true_nb_of_toc = min(x)-1
                    except ValueError:
                        true_nb_of_toc = 1

                    if true_nb_of_toc != extract_as_dict['nbTocPages']:
                        log.warning('nbTocPages in result pdf: {} are not equal to the one predicted : {}, request new pdf'.format(true_nb_of_toc,extract_as_dict['nbTocPages'])) # noqa
                        extract_as_dict['nbTocPages'] = true_nb_of_toc
                        print_result = requests.post(
                            pdf_url,
                            headers=pdf_headers,
                            data=json.dumps(spec)
                        )
        except PdfReadError as e:
            err_msg = 'a problem occurred while generating the pdf file'
            log.error(err_msg + ': ' + str(e))
            raise HTTPInternalServerError(err_msg)

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
                    log.warning(msg.format(url, content_type))
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

        # Save printed file to the specified path.
        pdf_archive_path = print_config.get('pdf_archive_path', None)
        if pdf_archive_path is not None:
            self.archive_pdf_file(pdf_archive_path, content, extract_as_dict)

        response.status_code = print_result.status_code
        response.headers = print_result.headers
        if 'Transfer-Encoding' in response.headers:
            del response.headers['Transfer-Encoding']
        if 'Connection' in response.headers:
            del response.headers['Connection']
        return content

    @staticmethod
    def archive_pdf_file(pdf_archive_path, binary_content, extract_as_dict):
        pdf_archive_path = pdf_archive_path if pdf_archive_path[-1:] == '/' else pdf_archive_path + '/'
        log.debug('Start to archive pdf file at path: ' + pdf_archive_path)

        time_info = (datetime.utcnow() + timedelta(hours=2)).strftime('%Y%m%d%H%M%S')  # UTC+2
        egrid = extract_as_dict.get('RealEstate_EGRID', 'no_egrid')
        path_and_filename = pdf_archive_path + time_info + '_' + egrid + '.pdf'

        archive = open(path_and_filename, 'ab')
        archive.write(binary_content)
        log.debug('Pdf file archived at: ' + path_and_filename)
        return path_and_filename

    @staticmethod
    def get_wms_url_params():
        """
        Returns the list of additionally configured wms_url_params.

        Returns:
            (dict): The configured wms_url_params.
        """
        result = {}
        wms_url_params = Config.get('print', {}).get('wms_url_params', False)
        if wms_url_params:
            log.debug("get_wms_url_params() read configuration {}".format(wms_url_params))
            if isinstance(wms_url_params, dict):
                result = wms_url_params
            else:
                log.warning("get_wms_url_params() ignoring unaccepted configuration value {}"
                            .format(wms_url_params))
        else:
            log.info("no wms_url_params configuration detected; using default value")
            result = {'TRANSPARENT': 'true'}
        return result

    def convert_to_printable_extract(self, extract_dict, feature_geometry, pdf_to_join):
        """
        Converts an oereb extract into a form suitable for printing by mapfish print.

        Args:
            extract_dict: the oereb extract, will get converted by this function into a form
                            convenient for mapfish-print
            feature_geometry: the geometry for this extract, will get added to the extract information
            pdf_to_join: a set of additional information for the pdf. Will get filled by this function.
                         Used in the full extract only
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
        wms_url_params = self.get_wms_url_params()

        main_page_basemap = {
            'type': 'wms',
            'styles': 'default',
            'opacity': extract_dict['RealEstate_PlanForLandRegisterMainPage'].get('layerOpacity', 0.6),
            'baseURL': base_url,
            'layers': main_page_params['LAYERS'][0].split(','),
            'imageFormat': 'image/png',
            'customParams': wms_url_params,
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
            'customParams': wms_url_params,
        }
        del extract_dict['RealEstate_PlanForLandRegister']  # /definitions/Map

        self._multilingual_m_text(extract_dict, 'GeneralInformation')
        self._multilingual_m_text(extract_dict, 'BaseData')
        self._multilingual_m_text(extract_dict, 'Certification')
        self._multilingual_m_text(extract_dict, 'CertificationAtWeb')

        for item in extract_dict.get('Glossary', []):
            self._multilingual_text(item, 'Title')
            self._multilingual_text(item, 'Content')
        self._multilingual_text(extract_dict, 'PLRCadastreAuthority_Name')

        for restriction_on_landownership in extract_dict.get('RealEstate_RestrictionOnLandownership', []):
            self._flatten_object(restriction_on_landownership, 'Lawstatus')
            self._flatten_object(restriction_on_landownership, 'Theme')
            self._flatten_array_object(restriction_on_landownership, 'Geometry', 'ResponsibleOffice')
            self._localised_text(restriction_on_landownership, 'Theme_Text')
            self._localised_text(restriction_on_landownership, 'Lawstatus_Text')
            self._multilingual_m_text(restriction_on_landownership, 'Information')

            self._multilingual_text(restriction_on_landownership['ResponsibleOffice'], 'Name')
            restriction_on_landownership['ResponsibleOffice'] = \
                [restriction_on_landownership['ResponsibleOffice']]

            url, params = parse_url(restriction_on_landownership['Map']['ReferenceWMS'])

            restriction_on_landownership['baseLayers'] = {
                'layers': [{
                    'type': params.pop('SERVICE', ['wms'])[0].lower(),
                    'opacity': restriction_on_landownership['Map'].get('layerOpacity', 0.6),
                    'styles': params.pop('STYLES', ['default'])[0],
                    'baseURL': urlparse.urlunsplit((url.scheme, url.netloc, url.path, None, None)),
                    'layers': params.pop('LAYERS', '')[0].split(','),
                    'imageFormat': params.pop('FORMAT', ['image/png'])[0],
                    'customParams': self.get_custom_wms_params(params),
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
            'Information', 'Lawstatus_Code', 'Lawstatus_Text', 'SymbolRef', 'TypeCode'
        ]
        legend_element = [
            'TypeCode', 'TypeCodelist', 'AreaShare', 'PartInPercent', 'LengthShare', 'NrOfPoints',
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

            # add additional ResponsibleOffice to theme if it not already exists there
            new_responsible_office = restriction_on_landownership['ResponsibleOffice'][0]
            existing_office_names = list(map(lambda o: o['Name'], current['ResponsibleOffice']))
            if new_responsible_office['Name'] not in existing_office_names:
                current['ResponsibleOffice'].append(new_responsible_office)

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
                    # This adds the first URL of TextAtWeb to the pdf_to_join set. At this point of the code
                    # there should only be one URL as the grouping takes place only after this if statement.
                    pdf_to_join.update([legal_provision['TextAtWeb'][0]['URL'] for legal_provision in values])

                # Group legal provisions and hints which have the same title.
                if (
                       (Config.get('print', {}).get('group_legal_provisions', False)) and
                       (element == 'LegalProvisions' or element == 'Hints')
                   ):
                    restriction_on_landownership[element] = \
                        self.group_legal_provisions(restriction_on_landownership[element])

            # sort legal provisioning, hints and laws
            restriction_on_landownership['LegalProvisions'] = self.sort_dict_list(
                restriction_on_landownership['LegalProvisions'],
                self.sort_legal_provision
            )
            restriction_on_landownership['Laws'] = self.sort_dict_list(
                restriction_on_landownership['Laws'],
                self.sort_laws
            )
            restriction_on_landownership['Hints'] = self.sort_dict_list(
                restriction_on_landownership['Hints'],
                self.sort_hints
            )

        restrictions = list(theme_restriction.values())
        for restriction in restrictions:
            legends = {}
            for legend in restriction['Legend']:
                type_ = legend['TypeCode']
                if type_ in legends:
                    for item in ['AreaShare', 'LengthShare', 'PartInPercent', 'NrOfPoints']:
                        if item in legend:
                            if item in legends[type_]:
                                legends[type_][item] += legend[item]
                            else:
                                legends[type_][item] = legend[item]
                else:
                    legends[type_] = legend
            # After transformation, get the new legend entries, sorted by TypeCode
            transformed_legend = \
                list([transformed_entry for (key, transformed_entry) in legends.items()])
            restriction['Legend'] = self.sort_dict_list(transformed_legend, self.sort_legend_elem)

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

        # Reformat AreaShare, LengthShare, NrOfPoints and part in percent values
        for restriction in extract_dict['RealEstate_RestrictionOnLandownership']:
            for legend in restriction['Legend']:
                if 'LengthShare' in legend:
                    legend['LengthShare'] = '{0} m'.format(legend['LengthShare'])
                if 'AreaShare' in legend:
                    legend['AreaShare'] = u'{0} m²'.format(legend['AreaShare'])
                if 'PartInPercent' in legend:
                    legend['PartInPercent'] = '{0}%'.format(round(legend['PartInPercent'], 2))
                if 'NrOfPoints' in legend:
                    legend['NrOfPoints'] = '{0}'.format(legend['NrOfPoints'])

        log.debug("After transformation, extract_dict is {}".format(extract_dict))
        return extract_dict

    @staticmethod
    def group_legal_provisions(legal_provisions):
        merged_provision = []
        for element in legal_provisions:
            # get element with same title if existing
            existing_element = \
                next((item for item in merged_provision if item['Title'] == element['Title']), None)
            if not existing_element:
                merged_provision.append(element)
                continue

            # join the the existing list with the new one
            existing_element['TextAtWeb'].extend(element['TextAtWeb'])
        return merged_provision if len(merged_provision) > 0 else legal_provisions

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

    def _multilingual_text_at_web(self, parent):
        name = 'TextAtWeb'
        if name in parent:
            lang_obj = dict([(e['Language'], e['Text']) for e in parent[name]])
            if self._language in lang_obj.keys():
                parent[name] = [{'URL': lang_obj[self._language]}]
            else:
                parent[name] = [{'URL': lang_obj[self._fallback_language]}]

    def _multilingual_text(self, parent, name):
        if name in parent:
            lang_obj = dict([(e['Language'], e['Text']) for e in parent[name]])
            if self._language in lang_obj.keys():
                parent[name] = lang_obj[self._language]
            else:
                parent[name] = lang_obj[self._fallback_language]

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

        # sort + flatten the split themes again
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

    @staticmethod
    def sort_dict_list(legend_list, sort_keys):
        """
        Sorts list of dictionaries by one or more sort keys.
        This function makes it possible to run test on the sorted list and assure the
        correctness of the soring.

        Args:
            legend_list (list(dict): list of legend dictionaries
            sort_keys (tuple/any): tuple of keys according to which the list of dictionaries will be
            sorted (at least one is needed)
        Returns:
            sorted list of legend dictionaries
        """
        return sorted(legend_list, key=sort_keys)

    @staticmethod
    def sort_legal_provision(elem):
        """
        Provides the sort key for the supplied legal provision element as a tuple consisting of:
         * title
         * Official number

        Args:
            elem (dict): one element of the legal provision list
        Returns:
            sort key (tuple)
        """

        sort_title = elem['Title'] if 'Title' in elem else ''
        sort_number = elem['OfficialNumber'] if 'OfficialNumber' in elem else None
        return sort_title, sort_number

    @staticmethod
    def sort_hints(elem):
        """
        Provides the sort key for the supplied hint element as a tuple consisting of:
         * Title

        Args:
            elem (dict): one element of the hints list
        Returns:
            sort key (tuple)
        """
        return elem['Title'] if 'Title' in elem else ''

    @staticmethod
    def sort_laws(elem):
        """
        Provides the sort key for the supplied law element as a tuple consisting of:
         * OfficialNumber (if this attribute is empty the element will be placed at the end of the list)
         * Title

        Args:
            elem (dict): one element of the legal laws list

        Returns:
            sort key (tuple)
        """
        sort_empty_number_last = 0 if 'OfficialNumber' in elem else 1
        sort_number = elem['OfficialNumber'] if 'OfficialNumber' in elem else ""
        sort_title = elem['Title'] if 'Title' in elem else ""
        return sort_empty_number_last, sort_number, sort_title

    @staticmethod
    def sort_legend_elem(elem):
        """
        Provides the sort key for the supplied legend element as a tuple consisting of:
         * rank of the geometry type as defined in LEGEND_ELEMENT_SORT_ORDER
         * value of the geometry if available (AreaShare and LengthShare)

        Args:
            elem (dict): legend entry

        Returns:
            sort key (tuple)
        """
        geom_type = elem['Geom_Type']

        if geom_type in LEGEND_ELEMENT_SORT_ORDER:
            # Get predefined order
            category = LEGEND_ELEMENT_SORT_ORDER.index(geom_type)
        else:
            # Put elements not found predefined order last
            category = len(LEGEND_ELEMENT_SORT_ORDER)

        # Use value as secondary criteria if available (defaults to 0 if not available).
        # Negative value for ascending sort order.
        value = -elem.get(geom_type, 0)

        return category, value

    def get_custom_wms_params(self, params):
        """
        From a given dictionary filter out all the parameters that are specified in the config
        and return these.
        Only values which exist in the given params are added.
        If there is nothing configured or the config is not a list
        the configured wms_url_params are used as fallback.

        Args:
            params (dict): Parameters available in the URL

        Returns:
            custom_params (dict): dictionary of filtered params
        """
        wms_url_params = Config.get('print', {}).get('wms_url_keep_params', False)
        if not isinstance(wms_url_params, list):
            # If no config exists or config is not as expected fall back to use standard wms_url_params
            return self.get_wms_url_params()

        custom_params = {
            wms_keys: self.string_check(wms_values)
            for wms_keys, wms_values in params.items()
            if wms_keys in wms_url_params
        }
        return custom_params

    @staticmethod
    def string_check(value):
        """
        Check if the value given is a string.
        If it is not, assume it is a list and join the values using comma separator.

        Args:
            value (str or list): value to be treated.

        Returns:
            (str): converted value
        """
        return value if isinstance(value, str) else ','.join(value)
