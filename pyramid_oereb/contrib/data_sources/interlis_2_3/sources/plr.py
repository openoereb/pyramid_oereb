# -*- coding: utf-8 -*-
import logging
import importlib
import binascii

from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import Point, LineString, Polygon, MultiPoint, MultiLineString, MultiPolygon, \
    GeometryCollection
from sqlalchemy import or_

from pyramid_oereb import Config
from pyramid_oereb.core import b64
from pyramid_oereb.core.records.image import ImageRecord
from pyramid_oereb.core.records.plr import EmptyPlrRecord
from pyramid_oereb.core.sources import BaseDatabaseSource
from pyramid_oereb.core.sources.plr import PlrBaseSource
from pyramid_oereb.contrib.data_sources.interlis_2_3.interlis_2_3_utils import from_multilingual_text_to_dict
from pyramid_oereb.contrib.data_sources.interlis_2_3.interlis_2_3_utils import from_multilingual_uri_to_dict
from pyramid_oereb.contrib import eliminate_duplicated_document_records

log = logging.getLogger(__name__)


class StandardThemeConfigParser(object):

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    @property
    def model_factory_path(self):
        return self.kwargs.get('source').get('params').get('model_factory')

    @property
    def schema_name(self):
        return self.kwargs.get('source').get('params').get('schema_name')

    @property
    def geometry_type(self):
        return self.kwargs.get('geometry_type')

    @property
    def srid(self):
        return Config.get_srid()

    @property
    def db_connection(self):
        return self.kwargs.get('source').get('params').get('db_connection')

    def get_model_factory(self):
        module_elements = Config.extract_module_function(
            self.model_factory_path
        )
        return getattr(
            importlib.import_module(module_elements['module_path']),
            module_elements['function_name']
        )

    def get_models(self):
        model_factory = self.get_model_factory()
        return model_factory(
            self.schema_name,
            self.geometry_type,
            self.srid,
            self.db_connection
        )


def parse_multiple_standard_themes(config):
    """
    Args:
        config (pyramid_oereb.standard.config.Config): The config object of the application.

    Returns:
        dict containing the factory_model for every plr code.
    """
    plrs = config._config.get('plrs')
    themes = {}
    for plr in plrs:
        config_parser = StandardThemeConfigParser(**plr)
        themes[plr['code']] = config_parser.get_models()
    return themes


class DatabaseSource(BaseDatabaseSource, PlrBaseSource):
    def __init__(self, **kwargs):
        """
        Keyword Arguments:
            name (str): The name. You are free to choose one.
            code (str): The official code. Regarding to the federal specifications.
            geometry_type (str): The geometry type. Possible are: POINT, POLYGON, LINESTRING,
                GEOMETRYCOLLECTION
            thresholds (dict): The configuration of limits and units used for processing.
            text (dict of str): The speaking title. It must be a dictionary containing language (as
                configured) as key and text as value.
            language (str): The language this public law restriction is originally shipped with.
            federal (bool): Switch if it is a federal topic. This will be taken into account in processing
                steps.
            source (dict): The configuration dictionary of the public law restriction
            hooks (dict of str): The hook methods: get_symbol, get_symbol_ref. They have to be provided as
                dotted string for further use with dotted name resolver of pyramid package.
            law_status (dict of str): The configuration dictionary of the law status. It consists of
                the code and text which must be a dictionary containing language (as configured)
                as key and text as value.
        """
        config_parser = StandardThemeConfigParser(**kwargs)
        self.models = config_parser.get_models()
        bds_kwargs = {
            'model': self.models.Geometry,
            'db_connection': kwargs.get('source').get('params').get('db_connection')
        }

        BaseDatabaseSource.__init__(self, **bds_kwargs)
        PlrBaseSource.__init__(self, **kwargs)

        self.legend_entry_model = self.models.LegendEntry
        self.datasource = []

    def from_db_to_legend_entry_record(self, legend_entry_from_db):
        theme = Config.get_theme_by_code_sub_code(legend_entry_from_db.theme, legend_entry_from_db.sub_theme)
        legend_entry_record = self._legend_entry_record_class(
            ImageRecord(
                b64.decode(
                    binascii.b2a_base64(legend_entry_from_db.symbol).decode('ascii')
                )
            ),
            from_multilingual_text_to_dict(
                de=legend_entry_from_db.legend_text_de,
                fr=legend_entry_from_db.legend_text_fr,
                it=legend_entry_from_db.legend_text_it,
                rm=legend_entry_from_db.legend_text_rm,
                en=legend_entry_from_db.legend_text_en
            ),
            legend_entry_from_db.type_code,
            legend_entry_from_db.type_code_list,
            theme,
            view_service_id=legend_entry_from_db.view_service_id,
            identifier=legend_entry_from_db.t_id
        )
        return legend_entry_record

    def from_db_to_legend_entry_records(self, legend_entries_from_db, sub_theme=None):
        legend_entry_records = []
        if sub_theme is not None:
            for legend_entry_from_db in legend_entries_from_db:
                if legend_entry_from_db.sub_theme == sub_theme:
                    self.from_db_to_legend_entry_record(legend_entry_from_db)
        else:
            for legend_entry_from_db in legend_entries_from_db:
                legend_entry_records.append(
                    self.from_db_to_legend_entry_record(legend_entry_from_db)
                )

        return legend_entry_records

    def from_db_to_view_service_record(self, view_service_from_db, legend_entry_records, theme):
        multilingual_uri = from_multilingual_uri_to_dict(view_service_from_db.multilingual_uri)
        layer_index, layer_opacity = Config.get_index_and_opacity_of_view_service(multilingual_uri)
        view_service_record = self._view_service_record_class(
            multilingual_uri,
            layer_index,
            layer_opacity,
            Config.get('default_language'),
            Config.get('srid'),
            Config.get('proxies'),
            legends=legend_entry_records
        )
        return view_service_record

    def unwrap_multi_geometry_(self, law_status, published_from, published_until,
                               multi_geom, geo_metadata):
        unwrapped = []
        for geom in multi_geom.geoms:
            unwrapped.append(
                self._geometry_record_class(
                    law_status,
                    published_from,
                    published_until,
                    geom,
                    geo_metadata
                )
            )
        return unwrapped

    def unwrap_geometry_collection_(self, law_status, published_from, published_until,
                                    collection, geo_metadata):
        unwrapped = []
        if len(collection.geoms) > 1:
            raise AttributeError(u'There was more than one element in the GeometryCollection. '
                                 u'This is not supported!')
        for geom in collection.geoms:
            unwrapped.extend(
                self.create_geometry_records_(
                    law_status,
                    published_from,
                    published_until,
                    geom,
                    geo_metadata
                )
            )
        return unwrapped

    def create_geometry_records_(self, law_status, published_from, published_until,
                                 geom, geo_metadata):
        geometry_records = []

        # Process single geometries
        if isinstance(geom, (Point, LineString, Polygon)):
            geometry_records.append(
                self._geometry_record_class(
                    law_status,
                    published_from,
                    published_until,
                    geom,
                    geo_metadata
                )
            )

        # Process multi geometries
        elif isinstance(geom, (MultiPoint, MultiLineString, MultiPolygon)):
            geometry_records.extend(self.unwrap_multi_geometry_(
                law_status,
                published_from,
                published_until,
                geom,
                geo_metadata
            ))

        # Process geometry collections
        elif isinstance(geom, GeometryCollection):
            geometry_records.extend(self.unwrap_geometry_collection_(
                law_status,
                published_from,
                published_until,
                geom,
                geo_metadata
            ))

        else:
            log.warning('Received geometry with unsupported type: {0}. Skipped geometry.'.format(
                geom.type
            ))

        return geometry_records

    def from_db_to_geometry_records(self, geometries_from_db):
        geometry_records = []
        for geometry_from_db in geometries_from_db:
            # Create law status record
            law_status = Config.get_law_status_by_data_code(
                    self._plr_info.get('code'),
                    geometry_from_db.law_status
                )

            if geometry_from_db.point is not None:
                geom = geometry_from_db.point
            elif geometry_from_db.line is not None:
                geom = geometry_from_db.line
            elif geometry_from_db.surface is not None:
                geom = geometry_from_db.surface

            # Create geometry records
            geometry_records.extend(self.create_geometry_records_(
                law_status,
                geometry_from_db.published_from,
                geometry_from_db.published_until,
                to_shape(geom),
                geometry_from_db.geo_metadata
            ))

        return geometry_records

    def from_db_to_office_record(self, offices_from_db):
        office_record = self._office_record_class(
            from_multilingual_text_to_dict(
                de=offices_from_db.name_de,
                fr=offices_from_db.name_fr,
                it=offices_from_db.name_it,
                rm=offices_from_db.name_rm,
                en=offices_from_db.name_en,
            ),
            offices_from_db.uid,
            from_multilingual_uri_to_dict(offices_from_db.multilingual_uri),
            offices_from_db.line1,
            offices_from_db.line2,
            offices_from_db.street,
            offices_from_db.number,
            offices_from_db.postal_code,
            offices_from_db.city
        )

        return office_record

    def from_db_to_document_records(self, documents_from_db):
        document_records = []
        for document in documents_from_db:
            office_record = self.from_db_to_office_record(document.responsible_office)
            law_status = Config.get_law_status_by_data_code(
                self._plr_info.get('code'),
                document.law_status
            )
            document_records.append(self._documents_record_class(
                document_type=Config.get_document_type_by_data_code(
                    self._plr_info.get('code'),
                    document.document_type
                ),
                index=document.index,
                law_status=law_status,
                title=from_multilingual_text_to_dict(
                        de=document.title_de,
                        fr=document.title_fr,
                        it=document.title_it,
                        rm=document.title_rm,
                        en=document.title_en),
                responsible_office=office_record,
                published_from=document.published_from,
                published_until=document.published_until,
                text_at_web=from_multilingual_uri_to_dict(document.multilingual_uri),
                abbreviation=from_multilingual_text_to_dict(
                        de=document.abbreviation_de,
                        fr=document.abbreviation_fr,
                        it=document.abbreviation_it,
                        rm=document.abbreviation_rm,
                        en=document.abbreviation_en),
                official_number=from_multilingual_text_to_dict(
                        de=document.official_number_de,
                        fr=document.official_number_fr,
                        it=document.official_number_it,
                        rm=document.official_number_rm,
                        en=document.official_number_en),
                only_in_municipality=document.only_in_municipality,
                article_numbers=None,
                file=None
            ))
        return document_records

    def from_db_to_plr_record(self, params, public_law_restriction_from_db, legend_entries_from_db):
        thresholds = self._plr_info.get('thresholds')
        min_length = thresholds.get('length').get('limit')
        length_unit = thresholds.get('length').get('unit')
        min_area = thresholds.get('area').get('limit')
        area_unit = thresholds.get('area').get('unit')
        legend_entry_record = self.from_db_to_legend_entry_record(
            public_law_restriction_from_db.legend_entry
        )
        legend_entry_records = self.from_db_to_legend_entry_records(
            legend_entries_from_db,
            legend_entry_record.theme.sub_code
        )
        symbol = ImageRecord(
            b64.decode(
                binascii.b2a_base64(public_law_restriction_from_db.legend_entry.symbol).decode('ascii')
            )
        )
        view_service_record = self.from_db_to_view_service_record(
            public_law_restriction_from_db.view_service,
            legend_entry_records,
            self._plr_info.get('code')
        )
        theme = Config.get_theme_by_code_sub_code(
            public_law_restriction_from_db.legend_entry.theme,
            public_law_restriction_from_db.legend_entry.sub_theme)
        document_records = eliminate_duplicated_document_records(
            theme.document_records,
            self.get_document_records(params, public_law_restriction_from_db)
        )
        geometry_records = self.from_db_to_geometry_records(public_law_restriction_from_db.geometries)
        law_status = Config.get_law_status_by_data_code(
            self._plr_info.get('code'),
            public_law_restriction_from_db.law_status
        )
        sub_theme_legend_entry_record = \
            legend_entry_record.theme if legend_entry_record.theme.sub_code else None
        plr_record = self._plr_record_class(
            Config.get_theme_by_code_sub_code(legend_entry_record.theme.code),
            legend_entry_record,
            law_status,
            public_law_restriction_from_db.published_from,
            public_law_restriction_from_db.published_until,
            self.from_db_to_office_record(public_law_restriction_from_db.responsible_office),
            symbol,
            view_service_record,
            geometry_records,
            sub_theme=sub_theme_legend_entry_record,
            type_code=public_law_restriction_from_db.legend_entry.type_code,
            type_code_list=public_law_restriction_from_db.legend_entry.type_code_list,
            documents=document_records,
            min_area=min_area,
            min_length=min_length,
            area_unit=area_unit,
            length_unit=length_unit,
            view_service_id=public_law_restriction_from_db.view_service.t_id
        )

        return plr_record

    def get_document_records(self, params, public_law_restriction_from_db):
        documents_from_db = []
        if not hasattr(public_law_restriction_from_db, 'legal_provisions'):
            raise AttributeError('The public_law_restriction implementation of type {} has no '
                                 'legal_provisions attribute. Check the model implementation.'
                                 .format(type(public_law_restriction_from_db)))
        for legal_provision in public_law_restriction_from_db.legal_provisions:
            documents_from_db.append(legal_provision.document)
        document_records = self.from_db_to_document_records(documents_from_db)
        return document_records

    def collect_related_geometries_by_real_estate(self, session, real_estate):
        """
        Extracts all geometries in the topic which have spatial relation with the passed real estate

        Args:
            session (sqlalchemy.orm.Session): The requested clean session instance ready for use
            real_estate (pyramid_oereb.lib.records.real_estate.RealEstateRecord): The real
                estate in its record representation.

        Returns:
            list: The result of the related geometries unique by the public law restriction id
        """

        return session.query(self._model_).filter(
                 or_(
                  self._model_.point.ST_Intersects(from_shape(real_estate.limit, srid=Config.get('srid'))),
                  self._model_.line.ST_Intersects(from_shape(real_estate.limit, srid=Config.get('srid'))),
                  self._model_.surface.ST_Intersects(from_shape(real_estate.limit, srid=Config.get('srid')))
                 )).distinct(self._model_.public_law_restriction_id).all()

    def collect_legend_entries_by_bbox(self, session, bbox):
        """
        Extracts all legend entries in the topic which have spatial relation with the passed bounding box of
        visible extent.

        Args:
            session (sqlalchemy.orm.Session): The requested clean session instance ready for use
            bbox (shapely.geometry.base.BaseGeometry): The bbox to search the records.

        Returns:
            list: The result of the related geometries unique by the public law restriction id
        """
        distinct_legend_entry_ids = []
        geometries = session.query(self._model_).filter(
                      or_(
                       self._model_.point.ST_Intersects(from_shape(bbox, srid=Config.get('srid'))),
                       self._model_.line.ST_Intersects(from_shape(bbox, srid=Config.get('srid'))),
                       self._model_.surface.ST_Intersects(from_shape(bbox, srid=Config.get('srid')))
                      )).distinct(self._model_.public_law_restriction_id).all()

        for geometry in geometries:
            if geometry.public_law_restriction.legend_entry_id not in distinct_legend_entry_ids:
                distinct_legend_entry_ids.append(geometry.public_law_restriction.legend_entry_id)

        return session.query(self.legend_entry_model).filter(
            self.legend_entry_model.t_id.in_((distinct_legend_entry_ids))).all()

    def read(self, params, real_estate, bbox):
        """
        The read point which creates a extract, depending on a passed real estate.

        Args:
            params (pyramid_oereb.views.webservice.Parameter): The parameters of the extract request.
            real_estate (pyramid_oereb.lib.records.real_estate.RealEstateRecord): The real
                estate in its record representation.
            bbox (shapely.geometry.base.BaseGeometry): The bbox to search the records.
        """

        # Check if the plr is marked as available
        if Config.availability_by_theme_code_municipality_fosnr(self._plr_info['code'], real_estate.fosnr):
            session = self._adapter_.get_session(self._key_)
            try:
                if session.query(self._model_).count() == 0:
                    # We can stop here already because there are no items in the database
                    self.records = [EmptyPlrRecord(
                            Config.get_theme_by_code_sub_code(self._plr_info['code'])
                        )]
                else:
                    # We need to investigate more in detail

                    # Try to find geometries which have spatial relation with real estate
                    geometry_results = self.collect_related_geometries_by_real_estate(
                        session, real_estate
                    )
                    if len(geometry_results) == 0:
                        # We checked if there are spatially related elements in database. But there is none.
                        # So we can stop here.
                        self.records = [EmptyPlrRecord(
                            Config.get_theme_by_code_sub_code(self._plr_info['code'])
                        )]
                    else:
                        # We found spatially related elements. This means we need to extract the actual plr
                        # information related to the found geometries.
                        self.records = []
                        legend_entries_from_db = self.collect_legend_entries_by_bbox(session, bbox)
                        for geometry_result in geometry_results:
                            self.records.append(
                                self.from_db_to_plr_record(
                                    params,
                                    geometry_result.public_law_restriction,
                                    legend_entries_from_db
                                )
                            )

            finally:
                session.close()

        # Add empty record if topic is not available
        else:
            self.records = [EmptyPlrRecord(
                Config.get_theme_by_code_sub_code(self._plr_info['code']),
                has_data=False
            )]
