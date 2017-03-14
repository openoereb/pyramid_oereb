# -*- coding: utf-8 -*-

import sqlalchemy.ext.declarative
import sqlalchemy as sa

from geoalchemy2.types import Geometry
from sqlalchemy.orm import relationship

NAMING_CONVENTION = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata = sa.MetaData(naming_convention=NAMING_CONVENTION)
Base = sqlalchemy.ext.declarative.declarative_base()
NotAlembicBase = sqlalchemy.ext.declarative.declarative_base()

srid_lv03 = 21781
srid_lv95 = 2056


# section where are the specific plr's are defined
plr_108_schema = 'plr_108'


class Authority(Base):
    __table_args__ = {'schema': plr_108_schema}
    __tablename__ = 'authority'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    authority_web = sa.Column(sa.String, nullable=True)
    uid = sa.Column(sa.String(12), nullable=True)


class ReferenceDefinition(Base):  # TODO: Check translation
    __table_args__ = {'schema': plr_108_schema}
    __tablename__ = 'reference_definition'
    id = sa.Column(sa.Integer, primary_key=True)
    topic = sa.Column(sa.String, nullable=True)
    canton = sa.Column(sa.String(2), nullable=True)
    municipality = sa.Column(sa.Integer, nullable=True)
    authority_id = sa.Column(sa.Integer, sa.ForeignKey(Authority.id), nullable=True)
    authority = relationship(Authority, backref='reference_definitions')


class DocumentBase(Base):
    __table_args__ = {'schema': plr_108_schema}
    __tablename__ = 'document_base'
    id = sa.Column(sa.Integer, primary_key=True)
    text_web = sa.Column(sa.String, nullable=True)
    legal_state = sa.Column(sa.String, nullable=False)
    published_from = sa.Column(sa.Date, nullable=False)
    type = sa.Column(sa.Unicode, nullable=True)
    __mapper_args__ = {
        'polymorphic_identity': 'document_base',
        'polymorphic_on': type,
        'passive_updates': True
    }


class Document(DocumentBase):
    __table_args__ = {'schema': plr_108_schema}
    __tablename__ = 'document'
    title = sa.Column(sa.String, nullable=False)
    official_title = sa.Column(sa.String, nullable=True)
    abbreviation = sa.Column(sa.String, nullable=True)
    official_number = sa.Column(sa.String, nullable=True)
    canton = sa.Column(sa.String(2), nullable=True)
    municipality = sa.Column(sa.Integer, nullable=True)
    document = sa.Column(sa.Binary, nullable=True)
    id = sa.Column(
        sa.Integer, sa.ForeignKey(DocumentBase.id), primary_key=True, onupdate="cascade"
    )
    type = sa.Column(sa.Unicode, nullable=True, server_default="document")
    __mapper_args__ = {
        'polymorphic_identity': 'document'
    }
    authority_id = sa.Column(sa.Integer, sa.ForeignKey(Authority.id), nullable=True)
    authority = relationship(Authority, backref='documents')


class Article(DocumentBase):
    __table_args__ = {'schema': plr_108_schema}
    __tablename__ = 'article'
    number = sa.Column(sa.String, nullable=False)
    text = sa.Column(sa.String, nullable=True)
    id = sa.Column(
        sa.Integer, sa.ForeignKey(DocumentBase.id), primary_key=True, onupdate="cascade"
    )
    type = sa.Column(sa.Unicode, nullable=True, server_default="article")
    __mapper_args__ = {
        'polymorphic_identity': 'article'
    }
    document_id = sa.Column(sa.Integer, sa.ForeignKey(Document.id), nullable=False)
    document = relationship(Document, backref='articles')


class LegalProvision(Document):
    __table_args__ = {'schema': plr_108_schema}
    __tablename__ = 'legal_provision'
    id = sa.Column(
        sa.Integer, sa.ForeignKey(Document.id), primary_key=True, onupdate="cascade"
    )
    type = sa.Column(sa.Unicode, nullable=True, server_default="legal_provision")
    __mapper_args__ = {
        'polymorphic_identity': 'legal_provision'
    }


class ViewService(Base):
    __table_args__ = {'schema': plr_108_schema}
    __tablename__ = 'view_service'
    id = sa.Column(sa.Integer, primary_key=True)
    link_wms = sa.Column(sa.String, nullable=False)
    legend_web = sa.Column(sa.String, nullable=True)


class LegendEntry(Base):
    __table_args__ = {'schema': plr_108_schema}
    __tablename__ = 'legend_entry'
    id = sa.Column(sa.Integer, primary_key=True)
    symbol = sa.Column(sa.Binary, nullable=False)
    legend_text = sa.Column(sa.String, nullable=False)
    type_code = sa.Column(sa.String(40), nullable=False)
    type_code_list = sa.Column(sa.String, nullable=False)
    topic = sa.Column(sa.String, nullable=False)
    subtopic = sa.Column(sa.String, nullable=True)
    additional_topic = sa.Column(sa.String, nullable=True)
    view_service_id = sa.Column(sa.Integer, sa.ForeignKey(ViewService.id), nullable=False)
    view_service = relationship(ViewService, backref='legends')


# TODO: check how the definition in base model from confederation can be realized
class PublicLawRestriction(Base):
    __table_args__ = {'schema': plr_108_schema}
    __tablename__ = 'public_law_restriction'
    id = sa.Column(sa.Integer, primary_key=True)
    content = sa.Column(sa.String, nullable=False)
    topic = sa.Column(sa.String, nullable=False)
    subtopic = sa.Column(sa.String, nullable=True)
    additional_topic = sa.Column(sa.String, nullable=True)
    type_code = sa.Column(sa.String(40), nullable=True)
    type_code_list = sa.Column(sa.String, nullable=True)
    legal_state = sa.Column(sa.String, nullable=False)
    published_from = sa.Column(sa.Date, nullable=False)
    view_service_id = sa.Column(sa.Integer, sa.ForeignKey(ViewService.id), nullable=True)
    view_service = relationship(ViewService, backref='public_law_restrictions')


class Geometry(Base):
    __table_args__ = {'schema': plr_108_schema}
    __tablename__ = 'geometry'
    id = sa.Column(sa.Integer, primary_key=True)
    legal_state = sa.Column(sa.String, nullable=False)
    published_from = sa.Column(sa.Date, nullable=False)
    geo_metadata = sa.Column(sa.String, nullable=True)  # TODO: Check translation
    geom = sa.Column(Geometry('POLYGON', srid=srid_lv03))
    public_law_restriction = sa.Column(sa.Integer, sa.ForeignKey(PublicLawRestriction.id), nullable=False)
    authority_id = sa.Column(sa.Integer, sa.ForeignKey(Authority.id), nullable=True)
    authority = relationship(Authority, backref='geometries')


class PublicLawRestrictionBase(Base):
    __tablename__ = 'public_law_restriction_base'
    __table_args__ = {'schema': plr_108_schema}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer, sa.ForeignKey(PublicLawRestriction.id), nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer, sa.ForeignKey(PublicLawRestriction.id), nullable=False
    )
    authority_id = sa.Column(sa.Integer, sa.ForeignKey(Authority.id), nullable=True)
    authority = relationship(Authority, backref='public_law_restrictions')


class PublicLawRestrictionRefinement(Base):
    __tablename__ = 'public_law_restriction_refinement'
    __table_args__ = {'schema': plr_108_schema}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer, sa.ForeignKey(PublicLawRestriction.id), nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer, sa.ForeignKey(PublicLawRestriction.id), nullable=False
    )


class PublicLawRestrictionDocument(Base):
    __tablename__ = 'public_law_restriction_document'
    __table_args__ = {'schema': plr_108_schema}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer, sa.ForeignKey(PublicLawRestriction.id), nullable=False
    )
    document_id = sa.Column(sa.Integer, sa.ForeignKey(DocumentBase.id), nullable=False)


# TODO: check translation
class DocumentHint(Base):
    __tablename__ = 'document_hint'
    __table_args__ = {'schema': plr_108_schema}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(sa.Integer, sa.ForeignKey(Document.id), nullable=False)
    hint_document_id = sa.Column(sa.Integer, sa.ForeignKey(Document.id), nullable=False)


class DocumentReferenceDefinition(Base):
    __tablename__ = 'document_reference_definition'
    __table_args__ = {'schema': plr_108_schema}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(sa.Integer, sa.ForeignKey(Document.id), nullable=False)
    reference_definition_id = sa.Column(sa.Integer, sa.ForeignKey(ReferenceDefinition.id), nullable=False)
