# -*- coding: utf-8 -*-
from json import dumps

from pyramid.response import Response

from pyramid_oereb import Config
from pyramid_oereb.lib.records.documents import DocumentRecord, LegalProvisionRecord, ArticleRecord
from pyramid_oereb.lib.sources.plr import PlrRecord
from shapely.geometry import mapping

from pyramid_oereb.lib.renderer import Base
from pyramid_oereb.views.webservice import Parameter


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

        self._language_ = str(Config.get('default_language')).lower()
        self._params_ = value[1]

        return self._render(value[0])

    def _render(self, extract):
        """
        Serializes the extract record.

        :param extract: The extract record
        :type extract: pyramid_oereb.lib.records.extract.ExtractRecord
        :return: The JSON encoded extract.
        :rtype: str
        """

        if not isinstance(self._params_, Parameter):
            raise TypeError('Missing parameter definition; Expected {0}, got {1} instead'.format(
                Parameter,
                self._params_.__class__
            ))

        if self._params_.language:
            self._language_ = str(self._params_.language).lower()

        extract_dict = {
            'CreationDate': self.date_time(extract.creation_date),
            'isReduced': self._params_.flavour == 'reduced',
            'LogoPLRCadastre': extract.logo_plr_cadastre.encode(),
            'FederalLogo': extract.federal_logo.encode(),
            'CantonalLogo': extract.cantonal_logo.encode(),
            'MunicipalityLogo': extract.municipality_logo.encode(),
            'ExtractIdentifier': extract.extract_identifier,
            'BaseData': extract.base_data,
            'PLRCadastreAuthority': self.format_office(extract.plr_cadastre_authority),
            'RealEstate': self.format_real_estate(extract.real_estate),
            'ConcernedTheme': [self.format_theme(theme) for theme in extract.concerned_theme],
            'NotConcernedTheme': [self.format_theme(theme) for theme in extract.not_concerned_theme],
            'ThemeWithoutData': [self.format_theme(theme) for theme in extract.theme_without_data]
        }

        if extract.electronic_signature:
            extract_dict['ElectronicSignature'] = extract.electronic_signature
        if extract.qr_code:
            extract_dict['QRCode'] = extract.qr_code
        if extract.general_information:
            extract_dict['GeneralInformation'] = extract.general_information

        if isinstance(extract.exclusions_of_liability, list) and len(extract.exclusions_of_liability) > 0:
            exclusions_of_liability = list()
            for eol in extract.exclusions_of_liability:
                exclusions_of_liability.append({
                    'Title': self.get_localized_text(eol.title),
                    'Content': self.get_localized_text(eol.content)
                })
            extract_dict['ExclusionOfLiability'] = exclusions_of_liability

        if isinstance(extract.glossaries, list) and len(extract.glossaries) > 0:
            glossaries = list()
            for gls in extract.glossaries:
                glossaries.append({
                    'Title': self.get_localized_text(gls.title),
                    'Content': self.get_localized_text(gls.content)
                })
            extract_dict['Glossary'] = glossaries

        response = {
            u'GetExtractByIdResponse': {
                u'extract': extract_dict
            }
        }

        return dumps(response)

    def format_real_estate(self, real_estate):
        """
        Formats a real estate record for rendering according to the federal specification.

        :param real_estate: The real estate record to be formatted.
        :type real_estate: pyramid_oereb.lib.records.real_estate.RealEstateRecord
        :return: The formatted dictionary for rendering.
        :rtype: dict
        """

        assert isinstance(self._params_, Parameter)

        real_estate_dict = {
            'Type': real_estate.type,
            'Canton': real_estate.canton,
            'Municipality': real_estate.municipality,
            'FosNr': real_estate.fosnr,
            'LandRegistryArea': real_estate.land_registry_area,
            'PlanForLandRegister': self.format_map(real_estate.plan_for_land_register)
        }

        if self._params_.geometry:
            real_estate_dict['Limit'] = self.from_shapely(real_estate.limit)

        if real_estate.number:
            real_estate_dict['Number'] = real_estate.number
        if real_estate.identdn:
            real_estate_dict['IdentDN'] = real_estate.identdn
        if real_estate.egrid:
            real_estate_dict['EGRID'] = real_estate.egrid
        if real_estate.subunit_of_land_register:
            real_estate_dict['SubunitOfLandRegister'] = real_estate.subunit_of_land_register
        if real_estate.metadata_of_geographical_base_data:
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

        return real_estate_dict

    def format_plr(self, plrs):
        """
        Formats a public law restriction record for rendering according to the federal specification.

        :param plrs: The public law restriction records to be formatted.
        :type plrs: list of pyramid_oereb.lib.records.plr.PlrRecord
        :return: The formatted dictionaries for rendering.
        :rtype: list of dict
        """

        assert isinstance(self._params_, Parameter)

        plr_list = list()

        for plr in plrs:

            if isinstance(plr, PlrRecord):

                # PLR without legal provision is allowed in reduced extract only!
                if self._params_.flavour != 'reduced' and isinstance(plr.documents, list) and \
                                len(plr.documents) == 0:
                    raise ValueError('Restrictions on landownership without legal provision are only allowed '
                                     'in reduced extracts!')

                plr_dict = {
                    'Information': self.get_localized_text(plr.content),
                    'Theme': self.format_theme(plr.theme),
                    'Lawstatus': plr.legal_state,
                    'Area': plr.area,
                    'Symbol': plr.symbol,
                    'ResponsibleOffice': self.format_office(plr.responsible_office),
                    'Map': self.format_map(plr.view_service)
                }

                if plr.subtopic:
                    plr_dict['SubTheme'] = plr.subtopic
                if plr.additional_topic:
                    plr_dict['OtherTheme'] = plr.additional_topic
                if plr.type_code:
                    plr_dict['TypeCode'] = plr.type_code
                if plr.type_code_list:
                    plr_dict['TypeCodelist'] = plr.type_code_list
                if plr.part_in_percent:
                    plr_dict['PartInPercent'] = plr.part_in_percent

                if self._params_.geometry and isinstance(plr.geometries, list) and len(plr.geometries) > 0:
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

    def format_document(self, document):
        """
        Formats a document record for rendering according to the federal specification.

        :param document: The document record to be formatted.
        :type document: pyramid_oereb.lib.records.documents.DocumentBaseRecord
        :return: The formatted dictionary for rendering.
        :rtype: dict
        """

        document_dict = dict()

        if isinstance(document, DocumentRecord) or isinstance(document, LegalProvisionRecord):

            document_dict.update({
                'Lawstatus': document.legal_state,
                'TextAtWeb': self.get_localized_text(document.text_at_web),
                'Title': self.get_localized_text(document.title),
                'ResponsibleOffice': self.format_office(document.responsible_office)
            })

            if document.official_title:
                document_dict['OfficialTitle'] = self.get_localized_text(document.official_title)
            if document.abbreviation:
                document_dict['Abbrevation'] = self.get_localized_text(document.abbreviation)
            if document.official_number:
                document_dict['OfficialNumber'] = document.official_number
            if document.canton:
                document_dict['Canton'] = document.canton
            if document.municipality:
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

        elif isinstance(document, ArticleRecord):
            document_dict.update({
                'Lawstatus': document.legal_state,
                'Number': document.number
            })

            if document.text_at_web:
                document_dict['TextAtWeb'] = self.get_localized_text(document.text_at_web)
            if document.text:
                document_dict['Text'] = self.get_localized_text(document.text)

        return document_dict

    def format_geometry(self, geometry):
        """
        Formats a geometry record for rendering according to the federal specification.

        :param geometry: The geometry record to be formatted.
        :type geometry: pyramid_oereb.lib.records.geometry.GeometryRecord
        :return: The formatted dictionary for rendering.
        :rtype: dict
        """
        plr_limits = Config.get('plr_limits')
        if geometry.geom.type in plr_limits.get('point_types'):
            geometry_type = 'Point'
        elif geometry.geom.type in plr_limits.get('line_types'):
            geometry_type = 'Line'
        elif geometry.geom.type in plr_limits.get('polygon_types'):
            geometry_type = 'Surface'
        else:
            raise TypeError('The geometry type {gtype} is not configured in "plr_limits"'.format(
                gtype=geometry.geom.type
            ))

        geometry_dict = {
            geometry_type: self.from_shapely(geometry.geom),
            'Lawstatus': geometry.legal_state,
            'ResponsibleOffice': self.format_office(geometry.office)
        }

        if geometry.geo_metadata:
            geometry_dict['MetadataOfGeographicalBaseData'] = geometry.geo_metadata

        return geometry_dict

    def format_office(self, office):
        """
        Formats an office record for rendering according to the federal specification.

        :param office: The office record to be formatted.
        :type office: pyramid_oereb.lib.records.office.OfficeRecord
        :return: The formatted dictionary for rendering.
        :rtype: dict
        """
        office_dict = {
            'Name': self.get_localized_text(office.name)
        }
        if office.office_at_web:
            office_dict['OfficeAtWeb'] = office.office_at_web
        if office.uid:
            office_dict['UID'] = office.uid
        if office.line1:
            office_dict['Line1'] = office.line1
        if office.line2:
            office_dict['Line2'] = office.line2
        if office.street:
            office_dict['Street'] = office.street
        if office.number:
            office_dict['Number'] = office.number
        if office.postal_code:
            office_dict['PostalCode'] = office.postal_code
        if office.city:
            office_dict['City'] = office.city
        return office_dict

    def format_theme(self, theme):
        """
        Formats a theme record for rendering according to the federal specification.

        :param theme: The theme record to be formatted.
        :type theme: pyramid_oereb.lib.records.theme.ThemeRecord
        :return: The formatted dictionary for rendering.
        :rtype: dict
        """
        theme_dict = {
            'Code': theme.code,
            'Text': self.get_localized_text(theme.text)
        }
        return theme_dict

    def format_map(self, map_):
        """
        Formats a view service record for rendering according to the federal specification.

        :param map_: The view service record to be formatted.
        :type map_: pyramid_oereb.lib.records.view_service.ViewServiceRecord
        :return: The formatted dictionary for rendering.
        :rtype: dict
        """
        map_dict = dict()
        if map_.image:
            map_dict['Image'] = map_.image
        if map_.link_wms:
            map_dict['ReferenceWMS'] = map_.link_wms
        if map_.legend_web:
            map_dict['LegendAtWeb'] = map_.legend_web
        if isinstance(map_.legends, list) and len(map_.legends) > 0:
            map_dict['OtherLegend'] = [
                self.format_legend_entry(legend_entry) for legend_entry in map_.legends]
        return map_dict

    def format_legend_entry(self, legend_entry):
        """
        Formats a legend entry record for rendering according to the federal specification.

        :param legend_entry: The legend entry record to be formatted.
        :type legend_entry: pyramid_oereb.lib.records.view_service.LegendEntryRecord
        :return: The formatted dictionary for rendering.
        :rtype: dict
        """
        legend_entry_dict = {
            'Symbol': legend_entry.symbol,
            'LegendText': self.get_localized_text(legend_entry.legend_text),
            'TypeCode': legend_entry.type_code,
            'TypeCodelist': legend_entry.type_code_list,
            'Theme': self.format_theme(legend_entry.theme)
        }
        if legend_entry.sub_theme:
            legend_entry_dict['SubTheme'] = legend_entry.sub_theme
        if legend_entry.additional_theme:
            legend_entry_dict['OtherTheme'] = legend_entry.additional_theme
        return legend_entry_dict

    @staticmethod
    def from_shapely(geom):
        """
        Formats shapely geometry for rendering according to the federal specification.

        :param geom: The geometry object to be formatted.
        :type geom: shapely.geometry.base.BaseGeometry
        :return: The formatted geometry.
        :rtype: dict
        """
        geom_dict = {
            'coordinates': mapping(geom)['coordinates'],
            'crs': 'EPSG:{srid}'.format(srid=Config.get('srid'))
            # isosqlmmwkb only used for curved geometries (not supported by shapely)
            # 'isosqlmmwkb': base64.b64encode(geom.wkb)
        }
        return geom_dict

    @staticmethod
    def get_localized_text(values):
        """
        Returns the set language of a multilingual text element.
        TODO: Fix implementation when multilingual values are available by respecting self.language.

        :param values: The multilingual values encoded as JSON.
        :type values: str or dict
        :return: List of dictionaries containing the multilingual representation.
        :rtype: list of dict
        """
        text = list()
        if isinstance(values, dict):
            for k, v in values.iteritems():
                text.append({
                    'Language': k,
                    'Text': v
                })
        else:
            text.append({
                'Language': Config.get('default_language'),
                'Text': values
            })
        return text
