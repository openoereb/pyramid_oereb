# -*- coding: utf-8 -*-
import logging
import base64
import datetime

from geoalchemy2.elements import _SpatialElement
from geoalchemy2.shape import to_shape, from_shape
from pyramid.path import DottedNameResolver
from sqlalchemy import or_
from sqlalchemy import text

from pyramid_oereb.lib.config import Config
from pyramid_oereb.lib.records.availability import AvailabilityRecord
from pyramid_oereb.lib.records.embeddable import TransferFromSourceRecord
from pyramid_oereb.lib.records.theme import EmbeddableThemeRecord
from pyramid_oereb.lib.records.image import ImageRecord
from pyramid_oereb.lib.sources import BaseDatabaseSource, Base
from pyramid_oereb.lib.records.plr import EmptyPlrRecord, PlrRecord
from pyramid_oereb.lib.records.documents import DocumentRecord, ArticleRecord
from pyramid_oereb.lib.records.exclusion_of_liability import ExclusionOfLiabilityRecord
from pyramid_oereb.lib.records.geometry import GeometryRecord
from pyramid_oereb.lib.records.glossary import GlossaryRecord
from pyramid_oereb.lib.records.office import OfficeRecord
from pyramid_oereb.lib.records.reference_definition import ReferenceDefinitionRecord
from pyramid_oereb.lib.records.view_service import ViewServiceRecord, LegendEntryRecord

log = logging.getLogger('pyramid_oereb')


class PlrBaseSource(Base):
    _documents_reocord_class_ = DocumentRecord
    _article_record_class_ = ArticleRecord
    _exclusion_of_liability_record_class_ = ExclusionOfLiabilityRecord
    _geometry_record_class_ = GeometryRecord
    _glossary_record_class_ = GlossaryRecord
    _legend_entry_record_class_ = LegendEntryRecord
    _office_record_class_ = OfficeRecord
    _plr_record_class_ = PlrRecord
    _reference_definition_record_class_ = ReferenceDefinitionRecord
    _view_service_record_class_ = ViewServiceRecord


class PlrStandardDatabaseSource(BaseDatabaseSource, PlrBaseSource):
    def __init__(self, **kwargs):
        self._plr_info_ = kwargs
        models_path = self._plr_info_.get('source').get('params').get('models')
        bds_kwargs = {
            'model': DottedNameResolver().maybe_resolve(
                '{models_path}.Geometry'.format(models_path=models_path)
            ),
            'db_connection': kwargs.get('source').get('params').get('db_connection')
        }
        self.legend_entry_model = DottedNameResolver().maybe_resolve(
            '{models_path}.LegendEntry'.format(models_path=models_path)
        )
        availability_model = DottedNameResolver().maybe_resolve(
            '{models_path}.Availability'.format(models_path=models_path)
        )
        transfer_from_source_model = DottedNameResolver().maybe_resolve(
            '{models_path}.DataIntegration'.format(models_path=models_path)
        )
        super(PlrStandardDatabaseSource, self).__init__(**bds_kwargs)

        session = self._adapter_.get_session(self._key_)
        availabilities_from_db = session.query(availability_model).all()
        self.availabilities = []
        for availability in availabilities_from_db:
            self.availabilities.append(
                AvailabilityRecord(availability.fosnr, available=availability.available)
            )
        self.transfer_from_source = session.query(transfer_from_source_model).all()
        # TODO: Fix this. Its not possible to have no actuality set. It's only for test case
        theme_sources = []
        for source in self.transfer_from_source:
            theme_sources.append(TransferFromSourceRecord(
                self.transfer_from_source.date,
                self.transfer_from_source.office(source.office)
            ))
        if len(theme_sources) == 0:
            log.warning(u'The theme sources for the topic {0} are empty. This is not allowed. Going through '
                        u'anyway'.format(self._plr_info_.get('code')))
            theme_sources = [TransferFromSourceRecord(
                datetime.datetime.now(),
                Config.get_plr_cadastre_authority()
            )]
        self.theme_record = EmbeddableThemeRecord(
            self._plr_info_.get('code'),
            self._plr_info_.get('text'),
            theme_sources
        )
        session.close()

    @property
    def info(self):
        """
        Return the info dictionary.

        Returns:
            dict: The info dictionary.
        """
        return self._plr_info_

    @staticmethod
    def geometry_parsing(geometry_value):
        geometry_types = Config.get('geometry_types')
        collection_types = geometry_types.get('collection').get('types')
        if isinstance(geometry_value, _SpatialElement):
            shapely_representation = to_shape(geometry_value)
            if shapely_representation.type in collection_types:
                # We need to check if the collection is empty
                if len(shapely_representation.geoms) > 0:
                    if len(shapely_representation.geoms) == 1:
                        # Its not empty, and due to specifications we are only interested in one (the first)
                        # geometry
                        shapely_representation = shapely_representation.geoms[0]
                    else:
                        raise AttributeError(u'There was more than one element in the GeometryCollection. '
                                             u'This is not supported!')
                else:
                    # There was nothing in it. So we assume it was meant to be None.
                    shapely_representation = None
            return shapely_representation
        else:
            return None

    def from_db_to_legend_entry_record(self, theme, legend_entries_from_db):
        legend_entry_records = []
        for legend_entry_from_db in legend_entries_from_db:
            legend_entry_records.append(self._legend_entry_record_class_(
                ImageRecord(base64.b64decode(legend_entry_from_db.symbol)),
                legend_entry_from_db.legend_text,
                legend_entry_from_db.type_code,
                legend_entry_from_db.type_code_list,
                theme
            ))
        return legend_entry_records

    def from_db_to_view_service_record(self, view_service_from_db, legend_entry_records):
        view_service_record = self._view_service_record_class_(
            view_service_from_db.link_wms,
            view_service_from_db.legend_web,
            legends=legend_entry_records
        )
        return view_service_record

    def from_db_to_geometry_records(self, geometries_from_db):
        geometry_records = []
        for geometry_from_db in geometries_from_db:
            geometry_records.append(self._geometry_record_class_(
                geometry_from_db.legal_state,
                geometry_from_db.published_from,
                self.geometry_parsing(geometry_from_db.geom),
                geometry_from_db.geo_metadata,
                office=self.from_db_to_office_record(geometry_from_db.responsible_office)
            ))
        return geometry_records

    def from_db_to_office_record(self, offices_from_db):
        office_record = self._office_record_class_(
            offices_from_db.name,
            offices_from_db.uid,
            offices_from_db.office_at_web,
            offices_from_db.line1,
            offices_from_db.line2,
            offices_from_db.street,
            offices_from_db.number,
            offices_from_db.postal_code,
            offices_from_db.city
        )
        return office_record

    def from_db_to_article_records(self, articles_from_db):
        article_records = []
        for article_from_db in articles_from_db:
            article_records.append(self._article_record_class_(
                article_from_db.legal_state,
                article_from_db.published_from,
                article_from_db.number,
                article_from_db.text_at_web,
                article_from_db.text
            ))
        return article_records

    def from_db_to_document_records(self, legal_provisions_from_db, article_numbers=None):
        document_records = []
        for i, legal_provision in enumerate(legal_provisions_from_db):
            referenced_documents_db = []
            referenced_article_numbers = []
            for join in legal_provision.referenced_documents:
                referenced_documents_db.append(join.referenced_document)
                referenced_article_nrs = join.article_numbers.split('|') if join.article_numbers else None
                referenced_article_numbers.append(referenced_article_nrs)
            referenced_document_records = self.from_db_to_document_records(
                referenced_documents_db,
                referenced_article_numbers
            )
            article_records = self.from_db_to_article_records(legal_provision.articles)
            office_record = self.from_db_to_office_record(legal_provision.responsible_office)
            article_nrs = article_numbers[i] if isinstance(article_numbers, list) else None
            document_records.append(self._documents_reocord_class_(
                legal_provision.legal_state,
                legal_provision.published_from,
                legal_provision.title,
                office_record,
                legal_provision.text_web,
                legal_provision.abbreviation,
                legal_provision.official_number,
                legal_provision.official_title,
                legal_provision.canton,
                legal_provision.municipality,
                article_nrs,
                legal_provision.file,
                article_records,
                referenced_document_records
            ))
        return document_records

    def from_db_to_plr_record(self, public_law_restriction_from_db):
        thresholds = self._plr_info_.get('thresholds')
        min_length = thresholds.get('length').get('limit')
        length_unit = thresholds.get('length').get('unit')
        length_precision = thresholds.get('length').get('precision')
        min_area = thresholds.get('area').get('limit')
        area_unit = thresholds.get('area').get('unit')
        area_precision = thresholds.get('area').get('precision')
        percentage_precision = thresholds.get('percentage').get('precision')
        legend_entry_records = self.from_db_to_legend_entry_record(
            self.theme_record,
            public_law_restriction_from_db.view_service.legends
        )
        symbol = None
        for legend_entry_record in legend_entry_records:
            if public_law_restriction_from_db.type_code == legend_entry_record:
                symbol_base64 = legend_entry_record.file
                symbol = ImageRecord(base64.b64decode(symbol_base64))
        if symbol is None:
            # TODO: raise real error here when data is correct, emit warning for now
            msg = u'No symbol was found for plr in topic {topic} with id {id}'.format(
                topic=self._plr_info_.get('code'),
                id=public_law_restriction_from_db.id
            )
            log.warning(msg)
            symbol = ImageRecord(bin(1))
            # raise AttributeError(msg)
        view_service_record = self.from_db_to_view_service_record(
            public_law_restriction_from_db.view_service,
            legend_entry_records
        )
        documents_from_db = []
        article_numbers = []
        for i, legal_provision in enumerate(public_law_restriction_from_db.legal_provisions):
            documents_from_db.append(legal_provision.document)
            article_nrs = legal_provision.article_numbers.split('|') if legal_provision.article_numbers \
                else None
            article_numbers.append(article_nrs)
        document_records = self.from_db_to_document_records(documents_from_db, article_numbers)
        geometry_records = self.from_db_to_geometry_records(public_law_restriction_from_db.geometries)

        basis_plr_records = []
        for join in public_law_restriction_from_db.basis:
            basis_plr_records.append(self.from_db_to_plr_record(join.base))
        refinements_plr_records = []
        for join in public_law_restriction_from_db.refinements:
            refinements_plr_records.append(self.from_db_to_plr_record(join.refinement))
        plr_record = self._plr_record_class_(
            self.theme_record,
            public_law_restriction_from_db.content,
            public_law_restriction_from_db.legal_state,
            public_law_restriction_from_db.published_from,
            self.from_db_to_office_record(public_law_restriction_from_db.responsible_office),
            symbol,
            subtopic=public_law_restriction_from_db.subtopic,
            additional_topic=public_law_restriction_from_db.additional_topic,
            type_code=public_law_restriction_from_db.type_code,
            type_code_list=public_law_restriction_from_db.type_code_list,
            view_service=view_service_record,
            basis=basis_plr_records,
            refinements=refinements_plr_records,
            documents=document_records,
            min_area=min_area,
            min_length=min_length,
            area_unit=area_unit,
            length_unit=length_unit,
            area_precision=area_precision,
            length_precision=length_precision,
            percentage_precision=percentage_precision
        )
        # solve circular dependency between plr and geometry
        for geometry_record in geometry_records:
            geometry_record.public_law_restriction = plr_record
        plr_record.geometries = geometry_records
        return plr_record

    @staticmethod
    def extract_geometry_collection_db(db_path, real_estate_geometry):
        """
        Decides the geometry collection cases of geometric filter operations when the database contains multi
        geometries but the passed geometry does not.
        The multi geometry will be extracted to it's sub parts for operation.

        Args:
            db_path (str): The point separated string of schema_name.table_name.column_name from
                which we can construct a correct SQL statement.
            real_estate_geometry (shapely.geometry.base.BaseGeometry): The shapely geometry
                representation which is used for comparison.

        Returns:
            sqlalchemy.sql.elements.BooleanClauseList: The clause element.

        Raises:
            HTTPBadRequest
        """
        srid = Config.get('srid')
        sql_text_point = 'ST_Intersects(ST_CollectionExtract({0}, 1), ST_GeomFromText(\'{1}\', {2}))'.format(
            db_path,
            real_estate_geometry.wkt,
            srid
        )
        sql_text_line = 'ST_Intersects(ST_CollectionExtract({0}, 2), ST_GeomFromText(\'{1}\', {2}))'.format(
            db_path,
            real_estate_geometry.wkt,
            srid
        )
        sql_text_polygon = 'ST_Intersects(ST_Envelope({0}), ' \
                           'ST_GeomFromText(\'{1}\', {2}))'.format(
                                db_path,
                                real_estate_geometry.wkt,
                                srid
                            )
        clause_blocks = [
            text(sql_text_point),
            text(sql_text_line),
            text(sql_text_polygon)
        ]
        return or_(*clause_blocks)

    def handle_collection(self, geometry_results, session, collection_types, bbox):

        # Check for Geometry type, cause we can't handle geometry collections the same as specific geometries
        if self._plr_info_.get('geometry_type') in [x.upper() for x in collection_types]:

            # The PLR is defined as a collection type. We need to do a special handling
            db_bbox_intersection_results = session.query(self._model_).filter(
                self.extract_geometry_collection_db(
                    '{schema}.{table}.geom'.format(
                        schema=self._model_.__table__.schema,
                        table=self._model_.__table__.name
                    ),
                    bbox
                )
            )

            def handle_result(result):
                real_geometry_intersection_result = bbox.intersects(to_shape(result.geom))
                if real_geometry_intersection_result:
                    geometry_results.append(
                        result
                    )
            for result in db_bbox_intersection_results:
                handle_result(result)
        else:

            # The PLR is not problematic at all cause we do not have a collection type here
            geometry_results.extend(session.query(self._model_).filter(self._model_.geom.ST_Intersects(
                from_shape(bbox, srid=Config.get('srid'))
            )).all())

    def read(self, real_estate, bbox):
        """
        The read point which creates a extract, depending on a passed real estate.

        Args:
            real_estate (pyramid_oereb.lib.records.real_estate.RealEstateRecord): The real
                estate in its record representation.
            bbox (shapely.geometry.base.BaseGeometry): The bbox to search the records.

        Returns:
            TODO: TODO
        """
        geometry_types = Config.get('geometry_types')
        collection_types = geometry_types.get('collection').get('types')

        public_law_restrictions = []

        # Check if the plr is marked as available
        for availability in self.availabilities:
            if real_estate.fosnr == availability.fosnr and not availability.available:
                # The plr is marked as not available! This stops every further processing for this PLR and
                # adds a simple empty record for the PLR's on this real estate
                public_law_restrictions.append(EmptyPlrRecord(self.theme_record, has_data=False))
                return public_law_restrictions
        session = self._adapter_.get_session(self._key_)

        if session.query(self._model_).count() == 0:
            # We can stop here already because there are no items in the database
            public_law_restrictions.append(EmptyPlrRecord(self.theme_record, has_data=False))
            return public_law_restrictions

        geometry_results = []
        self.handle_collection(geometry_results, session, collection_types, bbox)

        if len(geometry_results) == 0:
            public_law_restrictions.append(EmptyPlrRecord(self.theme_record))
            return public_law_restrictions
        for geometry_result in geometry_results:
            public_law_restrictions.append(
                self.from_db_to_plr_record(geometry_result.public_law_restriction)
            )
        session.close()
        return public_law_restrictions
