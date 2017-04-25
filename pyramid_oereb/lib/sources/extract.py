# -*- coding: utf-8 -*-
from geoalchemy2.elements import _SpatialElement
from geoalchemy2.shape import to_shape, from_shape
from pyramid.path import DottedNameResolver

from pyramid_oereb.lib.sources import BaseDatabaseSource, Base
from pyramid_oereb.lib.records.plr import PlrRecord
from pyramid_oereb.lib.records.documents import DocumentRecord, ArticleRecord
from pyramid_oereb.lib.records.exclusion_of_liability import ExclusionOfLiabilityRecord
from pyramid_oereb.lib.records.extract import ExtractRecord
from pyramid_oereb.lib.records.geometry import GeometryRecord
from pyramid_oereb.lib.records.glossary import GlossaryRecord
from pyramid_oereb.lib.records.office import OfficeRecord
from pyramid_oereb.lib.records.reference_definition import ReferenceDefinitionRecord
from pyramid_oereb.lib.records.view_service import ViewServiceRecord, LegendEntryRecord


class ExtractBaseSource(Base):
    _documents_reocord_class_ = DocumentRecord
    _article_record_class_ = ArticleRecord
    _exclusion_of_liability_record_class_ = ExclusionOfLiabilityRecord
    _extract_record_class_ = ExtractRecord
    _geometry_record_class_ = GeometryRecord
    _glossary_record_class_ = GlossaryRecord
    _legend_entry_record_class_ = LegendEntryRecord
    _office_record_class_ = OfficeRecord
    _plr_record_class_ = PlrRecord
    _reference_definition_record_class_ = ReferenceDefinitionRecord
    _view_service_record_class_ = ViewServiceRecord


class ExtractStandardDatabaseSource(BaseDatabaseSource, ExtractBaseSource):

    def __init__(self, **kwargs):
        self._name_ = kwargs.get('name')
        kwargs['model'] = DottedNameResolver().maybe_resolve(
            'pyramid_oereb.models.{name}Geometry'.format(name=self._name_.capitalize())
        )
        super(ExtractStandardDatabaseSource, self).__init__(**kwargs)

    @staticmethod
    def geometry_parsing(geometry_value):
        return to_shape(geometry_value) if isinstance(geometry_value, _SpatialElement) else None

    def from_db_to_legend_entry_record(self, topic, legend_entries_from_db):
        legend_entry_records = []
        for legend_entry_from_db in legend_entries_from_db:
            legend_entry_records.append(self._legend_entry_record_class_(
                legend_entry_from_db.symbol,
                legend_entry_from_db.legend_text,
                legend_entry_from_db.type_code,
                legend_entry_from_db.type_code_list,
                topic
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
                geometry_from_db.geo_metadata,
                self.geometry_parsing(geometry_from_db.geom),
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

    def from_db_to_document_records(self, legal_provisions_from_db, article_number=None):
        document_records = []
        for i, legal_provision in enumerate(legal_provisions_from_db):
            referenced_documents_db = []
            referenced_article_numbers = []
            for join in legal_provision.referenced_documents:
                referenced_documents_db.append(join.referenced_document)
                referenced_article_nr = join.article_number.split('|') if join.article_number else None
                referenced_article_numbers.append(referenced_article_nr)
            referenced_document_records = self.from_db_to_document_records(
                referenced_documents_db,
                referenced_article_numbers
            )
            article_records = self.from_db_to_article_records(legal_provision.articles)
            office_record = self.from_db_to_office_record(legal_provision.responsible_office)
            article_nr = article_number[i] if isinstance(article_number, list) else None
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
                article_nr,
                legal_provision.file,
                article_records,
                referenced_document_records
            ))
        return document_records

    def from_db_to_plr_record(self, public_law_restriction_from_db):
        legend_entry_records = self.from_db_to_legend_entry_record(
            public_law_restriction_from_db.topic,
            public_law_restriction_from_db.view_service.legends
        )
        view_service_record = self.from_db_to_view_service_record(
            public_law_restriction_from_db.view_service,
            legend_entry_records
        )
        documents_from_db = []
        for legal_provision in public_law_restriction_from_db.legal_provisions:
            documents_from_db.append(legal_provision.document)
        document_records = self.from_db_to_document_records(documents_from_db)
        geometry_records = self.from_db_to_geometry_records(public_law_restriction_from_db.geometries)

        basis_plr_records = []
        for join in public_law_restriction_from_db.basis:
            basis_plr_records.append(self.from_db_to_plr_record(join.base))
        refinements_plr_records = []
        for join in public_law_restriction_from_db.refinements:
            refinements_plr_records.append(self.from_db_to_plr_record(join.refinement))
        plr_record = self._plr_record_class_(
            public_law_restriction_from_db.content,
            public_law_restriction_from_db.topic,
            public_law_restriction_from_db.legal_state,
            public_law_restriction_from_db.published_from,
            None,  # TODO: Replace with office record
            public_law_restriction_from_db.subtopic,
            public_law_restriction_from_db.additional_topic,
            public_law_restriction_from_db.type_code,
            public_law_restriction_from_db.type_code_list,
            view_service_record,
            basis_plr_records,
            refinements_plr_records,
            document_records
        )
        # solve circular dependency between plr and geometry
        for geometry_record in geometry_records:
            geometry_record.public_law_restriction = plr_record
        plr_record.geometries = geometry_records
        return plr_record

    def read(self, real_estate):
        """
        The read point which creates a extract, depending on a passed real estate.
        :param real_estate: The real estate in its record representation.
        :type real_estate: pyramid_oereb.lib.records.real_estate.RealEstateRecord
        """
        self.records = list()
        geoalchemy_representation = from_shape(real_estate.limit, srid=2056)
        session = self._adapter_.get_session(self._key_)
        extract = self._extract_record_class_(
            real_estate,
            bin(100),
            bin(100),
            bin(100),
            bin(100)
        )
        geometry_results = session.query(self._model_).filter(self._model_.geom.ST_Intersects(
            geoalchemy_representation
        )).all()

        for geometry_result in geometry_results:
            real_estate.public_law_restrictions.append(
                self.from_db_to_plr_record(geometry_result.public_law_restriction)
            )

        self.records.append(extract)
