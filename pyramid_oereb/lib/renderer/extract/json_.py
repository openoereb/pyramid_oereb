# -*- coding: utf-8 -*-
import logging

from json import dumps

from pyramid.request import Request
from pyramid.response import Response
from pyramid.testing import DummyRequest

from pyramid_oereb import Config, route_prefix
from pyramid_oereb.lib.records.documents import DocumentRecord, LegalProvisionRecord,\
    ArticleRecord, LawRecord, HintRecord
from pyramid_oereb.lib.sources.plr import PlrRecord
from pyramid_oereb.lib.url import url_to_base64
from shapely.geometry import mapping

from pyramid_oereb.lib.renderer import Base
from pyramid_oereb.views.webservice import Parameter

log = logging.getLogger(__name__)


class Renderer(Base):
    def __init__(self, info):
        """
        Creates a new JSON renderer instance for extract rendering.

        Args:
            info (pyramid.interfaces.IRendererInfo): Info object.
        """
        super(Renderer, self).__init__(info)

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
        log.debug("__call__() start")
        self._request = self.get_request(system)
        assert isinstance(self._request, (Request, DummyRequest))

        response = self.get_response(system)
        if isinstance(response, Response) and response.content_type == response.default_content_type:
            response.content_type = 'application/json; charset=UTF-8'

        extract_dict = self._render(value[0], value[1])
        result = {
            u'GetExtractByIdResponse': {
                u'extract': extract_dict
            }
        }
        if self._params.flavour == 'embeddable':
            result[u'GetExtractByIdResponse'][u'embeddable'] = self.format_embeddable(value[0].embeddable)
        log.debug("__call__() done.")
        return dumps(result)

    def _render(self, extract, param):
        """
        Serializes the extract record.

        Args:
            extract (pyramid_oereb.lib.records.extract.ExtractRecord): The extract record
            param (pyramid_oereb.views.webservice.Parameter): The parameter instance holding information and
                methods for handling request parameters.

        Returns:
            str: The JSON encoded extract.
        """
        log.debug("_render() start")
        self._params = param

        if not isinstance(self._params, Parameter):
            raise TypeError('Missing parameter definition; Expected {0}, got {1} instead'.format(
                Parameter,
                self._params.__class__
            ))

        if self._params.language is not None:
            self._language = str(self._params.language).lower()
        else:
            self._language = Config.get('default_language')

        extract_dict = {
            'CreationDate': self.date_time(extract.creation_date),
            'isReduced': self._params.flavour in ['reduced', 'embeddable'],
            'ExtractIdentifier': extract.extract_identifier,
            'BaseData': self.get_multilingual_text(extract.base_data),
            'PLRCadastreAuthority': self.format_office(extract.plr_cadastre_authority),
            'RealEstate': self.format_real_estate(extract.real_estate),
            'ConcernedTheme': [self.format_theme(theme) for theme in extract.concerned_theme],
            'NotConcernedTheme': [self.format_theme(theme) for theme in extract.not_concerned_theme],
            'ThemeWithoutData': [self.format_theme(theme) for theme in extract.theme_without_data]
        }

        if self._params.images:
            extract_dict.update({
                'LogoPLRCadastre': extract.logo_plr_cadastre.encode(),
                'FederalLogo': extract.federal_logo.encode(),
                'CantonalLogo': extract.cantonal_logo.encode(),
                'MunicipalityLogo': extract.municipality_logo.encode()
            })
        else:
            extract_dict.update({
                'LogoPLRCadastreRef': self._request.route_url('{0}/image/logo'.format(route_prefix),
                                                              logo='oereb'),
                'FederalLogoRef': self._request.route_url('{0}/image/logo'.format(route_prefix),
                                                          logo='confederation'),
                'CantonalLogoRef': self._request.route_url('{0}/image/logo'.format(route_prefix),
                                                           logo='canton'),
                'MunicipalityLogoRef': self._request.route_url(
                    '{0}/image/municipality'.format(route_prefix),
                    fosnr=extract.real_estate.fosnr
                )
            })

        if extract.certification:
            extract_dict.update({
              'Certification': self.get_multilingual_text(extract.certification),
            })

        if extract.certification_at_web:
            extract_dict.update({
              'CertificationAtWeb': self.get_multilingual_text(extract.certification_at_web),
            })

        if extract.electronic_signature is not None:
            extract_dict['ElectronicSignature'] = extract.electronic_signature
        if extract.qr_code is not None:
            extract_dict['QRCode'] = extract.qr_code
        if extract.general_information is not None:
            extract_dict['GeneralInformation'] = self.get_multilingual_text(extract.general_information)

        if isinstance(extract.exclusions_of_liability, list) and len(extract.exclusions_of_liability) > 0:
            exclusions_of_liability = list()
            for eol in extract.exclusions_of_liability:
                exclusions_of_liability.append({
                    'Title': self.get_multilingual_text(eol.title),
                    'Content': self.get_multilingual_text(eol.content)
                })
            extract_dict['ExclusionOfLiability'] = exclusions_of_liability

        if isinstance(extract.glossaries, list) and len(extract.glossaries) > 0:
            glossaries = list()
            for gls in extract.glossaries:
                gls_title = self.get_multilingual_text(gls.title)
                gls_title_text = gls_title[0]['Text']
                if gls_title_text is not None:
                    glossaries.append({
                        'Title': gls_title,
                        'Content': self.get_multilingual_text(gls.content)
                    })
                else:
                    log.warning("glossary entry in requested language missing for title {}".format(gls.title))

            # Sort glossary by requested language alphabetically
            extract_dict['Glossary'] = self.sort_by_localized_text(
                glossaries,
                lambda element: element['Title'][0]['Text']
            )
        log.debug("_render() done.")
        return extract_dict

    def format_real_estate(self, real_estate):
        """
        Formats a real estate record for rendering according to the federal specification.

        Args:
            real_estate (pyramid_oereb.lib.records.real_estate.RealEstateRecord): The real
                estate record to be formatted.

        Returns:
            dict: The formatted dictionary for rendering.
        """

        assert isinstance(self._params, Parameter)

        real_estate_dict = {
            'Type': real_estate.type,
            'Canton': real_estate.canton,
            'Municipality': real_estate.municipality,
            'FosNr': real_estate.fosnr,
            'LandRegistryArea': real_estate.land_registry_area,
            'PlanForLandRegister': self.format_map(real_estate.plan_for_land_register),
            'PlanForLandRegisterMainPage': self.format_map(real_estate.plan_for_land_register_main_page)
        }

        if self._params.geometry:
            real_estate_dict['Limit'] = self.from_shapely(real_estate.limit)

        if real_estate.number is not None:
            real_estate_dict['Number'] = real_estate.number
        if real_estate.identdn is not None:
            real_estate_dict['IdentDN'] = real_estate.identdn
        if real_estate.egrid is not None:
            real_estate_dict['EGRID'] = real_estate.egrid
        if real_estate.subunit_of_land_register is not None:
            real_estate_dict['SubunitOfLandRegister'] = real_estate.subunit_of_land_register
        if real_estate.metadata_of_geographical_base_data is not None:
            real_estate_dict['MetadataOfGeographicalBaseData'] = \
                real_estate.metadata_of_geographical_base_data

        if isinstance(real_estate.public_law_restrictions, list) \
                and len(real_estate.public_law_restrictions) > 0:
            real_estate_dict['RestrictionOnLandownership'] = \
                self.format_plr(real_estate.public_law_restrictions)

        if isinstance(real_estate.references, list) and len(real_estate.references) > 0:
            reference_list = list()
            for reference in real_estate.references:
                reference_list.append(self.format_document(reference))
            real_estate_dict['Reference'] = reference_list

        if self._params.flavour == 'full':
            real_estate_dict['Highlight'] = self.format_map(real_estate.highlight)

        return real_estate_dict

    def format_plr(self, plrs):
        """
        Formats a public law restriction record for rendering according to the federal specification.

        Args:
            plrs (list of pyramid_oereb.lib.records.plr.PlrRecord): The public law restriction
                records to be formatted.

        Returns:
            list of dict: The formatted dictionaries for rendering.
        """

        assert isinstance(self._params, Parameter)

        plr_list = list()

        for plr in plrs:

            if isinstance(plr, PlrRecord):

                # PLR without legal provision is allowed in reduced extract only!
                if self._params.flavour != 'reduced' and isinstance(plr.documents, list) and \
                        len(plr.documents) == 0:
                    raise ValueError('Restrictions on landownership without legal provision are only allowed '
                                     'in reduced extracts!')
                plr_dict = {
                    'Information': self.get_multilingual_text(plr.information),
                    'Theme': self.format_theme(plr.theme),
                    'Lawstatus': self.format_law_status(plr.law_status),
                    'ResponsibleOffice': self.format_office(plr.responsible_office),
                    'Map': self.format_map(plr.view_service)
                }

                if self._params.images:
                    plr_dict.update({
                        'Symbol': plr.symbol.encode()
                    })
                else:
                    # Link to symbol is only available if type code is set!
                    if plr.type_code:
                        plr_dict.update({
                            'SymbolRef': self.get_symbol_ref(self._request, plr)
                        })

                if plr.area_share is not None:
                    plr_dict['AreaShare'] = plr.area_share
                if plr.length_share is not None:
                    plr_dict['LengthShare'] = plr.length_share
                if plr.nr_of_points is not None:
                    plr_dict['NrOfPoints'] = plr.nr_of_points
                if plr.sub_theme is not None:
                    plr_dict['SubTheme'] = self.get_localized_text(plr.sub_theme).get('Text')
                if plr.other_theme is not None:
                    plr_dict['OtherTheme'] = plr.other_theme
                if plr.type_code is not None:
                    plr_dict['TypeCode'] = plr.type_code
                if plr.type_code_list is not None:
                    plr_dict['TypeCodelist'] = plr.type_code_list
                if plr.part_in_percent is not None:
                    plr_dict['PartInPercent'] = plr.part_in_percent

                if self._params.geometry and isinstance(plr.geometries, list) and len(plr.geometries) > 0:
                    geometry_list = list()
                    for geometry in plr.geometries:
                        geometry_list.append(self.format_geometry(geometry))
                    plr_dict['Geometry'] = geometry_list

                if isinstance(plr.documents, list) and len(plr.documents) > 0:
                    documents_list = list()
                    for document in plr.documents:
                        documents_list.append(self.format_document(document))
                    plr_dict['LegalProvisions'] = documents_list

                plr_list.append(plr_dict)

        return plr_list

    def format_law_status(self, law_status):
        """
        Args:
            law_status (pyramid_oereb.lib.records.law_status.LawStatusRecord): The law status to format into
                a dictionary.
        Returns:
            dict: The transformed law status.
        """
        return {
            'Code': law_status.code,
            'Text': self.get_localized_text(law_status.text)
        }

    def format_document(self, document):
        """
        Formats a document record for rendering according to the federal specification.
        If the render is requested with a *full* flavour, it will render the *textAtWeb*
        into a *Base64TextAtWeb* field (for LegalProvisionRecord documents).

        Args:
            document (pyramid_oereb.lib.records.documents.DocumentBaseRecord): The document
                record to be formatted.

        Returns:
            dict: The formatted dictionary for rendering.
        """

        document_dict = dict()

        if isinstance(document, DocumentRecord) or isinstance(document, LegalProvisionRecord) \
                or isinstance(document, LawRecord) or isinstance(document, HintRecord):

            multilingual_text_at_web = self.get_multilingual_text(document.text_at_web)

            document_dict.update({
                'DocumentType': document.document_type,
                'Lawstatus': self.format_law_status(document.law_status),
                'TextAtWeb': multilingual_text_at_web,
                'Title': self.get_multilingual_text(document.title),
                'ResponsibleOffice': self.format_office(document.responsible_office)
            })
            if self._params.flavour == 'full' and isinstance(document, LegalProvisionRecord):
                base64_text_at_web = url_to_base64(multilingual_text_at_web[0].get('Text'))
                if base64_text_at_web is not None:
                    document_dict['Base64TextAtWeb'] = base64_text_at_web

            if document.official_title is not None:
                document_dict['OfficialTitle'] = self.get_multilingual_text(document.official_title)
            if document.abbreviation is not None:
                document_dict['Abbreviation'] = self.get_multilingual_text(document.abbreviation)
            if document.official_number is not None:
                document_dict['OfficialNumber'] = document.official_number
            if document.canton is not None:
                document_dict['Canton'] = document.canton
            if document.municipality is not None:
                document_dict['Municipality'] = document.municipality

            if isinstance(document.article_numbers, list) and len(document.article_numbers) > 0:
                document_dict['ArticleNumber'] = document.article_numbers

            if isinstance(document.articles, list) and len(document.articles) > 0:
                article_list = list()
                for article in document.articles:
                    article_list.append(self.format_document(article))
                document_dict['Article'] = article_list

            if isinstance(document.references, list) and len(document.references) > 0:
                reference_list = list()
                for reference in document.references:
                    reference_list.append(self.format_document(reference))
                document_dict['Reference'] = reference_list

            # Note: No output for File (binary) because speccifications are
            # currently unclear on this point. See Issue:
            # https://github.com/openoereb/pyramid_oereb/issues/611

        elif isinstance(document, ArticleRecord):
            document_dict.update({
                'Lawstatus': self.format_law_status(document.law_status),
                'Number': document.number
            })

            if document.text_at_web is not None:
                document_dict['TextAtWeb'] = self.get_multilingual_text(document.text_at_web)
            if document.text is not None:
                document_dict['Text'] = self.get_multilingual_text(document.text)

        return document_dict

    def format_geometry(self, geometry):
        """
        Formats a geometry record for rendering according to the federal specification.

        Args:
            geometry (pyramid_oereb.lib.records.geometry.GeometryRecord): The geometry record to
                be formatted.

        Returns:
            dict: The formatted dictionary for rendering.
        """
        geometry_types = Config.get('geometry_types')
        if geometry.geom.type in geometry_types.get('point').get('types'):
            geometry_type = 'Point'
        elif geometry.geom.type in geometry_types.get('line').get('types'):
            geometry_type = 'Line'
        elif geometry.geom.type in geometry_types.get('polygon').get('types'):
            geometry_type = 'Surface'
        else:
            raise TypeError('The geometry type {gtype} is not configured in "geometry_types"'.format(
                gtype=geometry.geom.type
            ))

        geometry_dict = {
            geometry_type: self.from_shapely(geometry.geom),
            'Lawstatus': self.format_law_status(geometry.law_status),
            'ResponsibleOffice': self.format_office(geometry.office)
        }

        if geometry.geo_metadata is not None:
            geometry_dict['MetadataOfGeographicalBaseData'] = geometry.geo_metadata

        return geometry_dict

    def format_office(self, office):
        """
        Formats an office record for rendering according to the federal specification.

        Args:
            office (pyramid_oereb.lib.records.office.OfficeRecord): The office record to be
                formatted.

        Returns:
            dict: The formatted dictionary for rendering.
        """
        office_dict = {
            'Name': self.get_multilingual_text(office.name)
        }
        if office.office_at_web is not None:
            office_dict['OfficeAtWeb'] = office.office_at_web
        if office.uid is not None:
            office_dict['UID'] = office.uid
        if office.line1 is not None:
            office_dict['Line1'] = office.line1
        if office.line2 is not None:
            office_dict['Line2'] = office.line2
        if office.street is not None:
            office_dict['Street'] = office.street
        if office.number is not None:
            office_dict['Number'] = office.number
        if office.postal_code is not None:
            office_dict['PostalCode'] = office.postal_code
        if office.city is not None:
            office_dict['City'] = office.city
        return office_dict

    def format_theme(self, theme):
        """
        Formats a theme record for rendering according to the federal specification.

        Args:
            theme (pyramid_oereb.lib.records.theme.ThemeRecord): The theme record to be
                formatted.

        Returns:
            dict: The formatted dictionary for rendering.
        """
        theme_dict = {
            'Code': theme.code,
            'Text': self.get_localized_text(theme.text)
        }
        return theme_dict

    def format_map(self, map_):
        """
        Formats a view service record for rendering according to the federal specification.

        Args:
            map_ (pyramid_oereb.lib.records.view_service.ViewServiceRecord): The view service
                record to be formatted.

        Returns:
            dict: The formatted dictionary for rendering.
        """
        map_dict = dict()
        if map_.image is not None:
            map_dict['Image'] = map_.image.encode()
        if map_.reference_wms is not None:
            map_dict['ReferenceWMS'] = map_.reference_wms
        if map_.legend_at_web is not None:
            if self._language in map_.legend_at_web:
                map_dict['LegendAtWeb'] = map_.legend_at_web[self._language]
            else:
                log.warning("map_.legend_at_web has no element {}".format(self._language))
        if isinstance(map_.legends, list) and len(map_.legends) > 0:
            other_legend = self.sort_by_localized_text(
                map_.legends,
                lambda element: element.legend_text
            )

            map_dict['OtherLegend'] = [
                self.format_legend_entry(legend_entry) for legend_entry in other_legend]

        map_dict['layerIndex'] = map_.layer_index
        map_dict['layerOpacity'] = map_.layer_opacity
        if map_.min_NS03 is not None:
            map_dict['min_NS03'] = self.format_point(map_.min_NS03, 'EPSG:21781')
        if map_.max_NS03 is not None:
            map_dict['max_NS03'] = self.format_point(map_.max_NS03, 'EPSG:21781')
        if map_.min_NS95 is not None:
            map_dict['min_NS95'] = self.format_point(map_.min_NS95, 'EPSG:2056')
        if map_.max_NS95 is not None:
            map_dict['max_NS95'] = self.format_point(map_.max_NS95, 'EPSG:2056')

        return map_dict

    def format_legend_entry(self, legend_entry):
        """
        Formats a legend entry record for rendering according to the federal specification.

        Args:
            legend_entry (pyramid_oereb.lib.records.view_service.LegendEntryRecord): The legend
                entry record to be formatted.

        Returns:
            dict: The formatted dictionary for rendering.
        """
        legend_entry_dict = {
            'LegendText': self.get_multilingual_text(legend_entry.legend_text),
            'TypeCode': legend_entry.type_code,
            'TypeCodelist': legend_entry.type_code_list,
            'Theme': self.format_theme(legend_entry.theme)
        }

        if self._params.images:
            legend_entry_dict.update({
                'Symbol': legend_entry.symbol.encode()
            })
        else:
            legend_entry_dict.update({
                'SymbolRef': self.get_symbol_ref(self._request, legend_entry)
            })

        if legend_entry.sub_theme is not None:
            legend_entry_dict['SubTheme'] = self.get_localized_text(legend_entry.sub_theme).get('Text')
        if legend_entry.other_theme is not None:
            legend_entry_dict['OtherTheme'] = legend_entry.other_theme
        return legend_entry_dict

    @staticmethod
    def from_shapely(geom):
        """
        Formats shapely geometry for rendering according to the federal specification.

        Args:
            geom (shapely.geometry.base.BaseGeometry): The geometry object to be formatted.

        Returns:
            dict: The formatted geometry.
        """
        geom_dict = {
            'coordinates': mapping(geom)['coordinates'],
            'crs': 'EPSG:{srid}'.format(srid=Config.get('srid'))
            # isosqlmmwkb only used for curved geometries (not supported by shapely)
            # 'isosqlmmwkb': base64.b64encode(geom.wkb)
        }
        return geom_dict

    def format_embeddable(self, embeddable):
        """
        Formats a embeddable record for rendering according to the specification.

        Args:
            embeddable (pyramid_oereb.lib.records.embeddable.EmbeddableRecord): The record to be formatted.

        Returns:
            dict: The formatted record for rendering.
        """

        datasources = []
        for source in embeddable.datasources:
            datasources.append({
                'topic': self.format_theme(source.theme),
                'dataownerName': self.get_localized_text(source.owner.name).get('Text'),
                'transferFromSource': source.date.strftime('%d-%m-%YT%H:%M:%S')
            })

        embeddable_dict = {
            'cadasterState': embeddable.cadaster_state.strftime('%d-%m-%YT%H:%M:%S'),
            'cadasterOrganisationName': self.get_localized_text(
                embeddable.cadaster_organisation.name
            ).get('Text'),
            'dataOwnerNameCadastralSurveying': self.get_localized_text(
                embeddable.data_owner_cadastral_surveying.name
            ).get('Text'),
            'transferFromSourceCadastralSurveying':
                embeddable.transfer_from_source_cadastral_surveying.strftime('%d-%m-%YT%H:%M:%S'),
            'datasource': datasources
        }

        return embeddable_dict

    @staticmethod
    def format_point(point, crs):
        return {
            'coordinates': [point.x, point.y],
            'crs': crs
        }
