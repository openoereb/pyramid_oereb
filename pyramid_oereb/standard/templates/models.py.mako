# -*- coding: utf-8 -*-

import sqlalchemy.ext.declarative
import sqlalchemy as sa

from sqlalchemy import PrimaryKeyConstraint
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


class ${''.join(x for x in app_schema.get('name').title() if not x.isspace()).replace('_', '')}Municipality(Base):
    __table_args__ = {'schema': '${app_schema.get('name')}'}
    __tablename__ = 'municipality'
    fosnr = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    published = sa.Column(sa.Boolean, nullable=False, default=False, server_default=sqlalchemy.text('FALSE'))
    logo = sa.Column(sa.String, nullable=False)
    geom = sa.Column(Geometry('MULTIPOLYGON', srid=${srid}), nullable=True)


class ${''.join(x for x in app_schema.get('name').title() if not x.isspace()).replace('_', '')}RealEstate(Base):
    __table_args__ = {'schema': '${app_schema.get('name')}'}
    __tablename__ = 'real_estate'
    id = sa.Column(sa.Integer, primary_key=True)
    identdn = sa.Column(sa.String, nullable=True)
    number = sa.Column(sa.String, nullable=True)
    egrid = sa.Column(sa.String, nullable=True)
    type = sa.Column(sa.String, nullable=False)
    canton = sa.Column(sa.String, nullable=False)
    municipality = sa.Column(sa.String, nullable=False)
    subunit_of_land_register = sa.Column(sa.String, nullable=True)
    fosnr = sa.Column(sa.Integer, nullable=False)
    metadata_of_geographical_base_data = sa.Column(sa.String, nullable=True)
    land_registry_area = sa.Column(sa.Integer, nullable=False)
    limit = sa.Column(Geometry('MULTIPOLYGON', srid=${srid}))


class ${''.join(x for x in app_schema.get('name').title() if not x.isspace()).replace('_', '')}Address(Base):
    __table_args__ = (
        PrimaryKeyConstraint("street_name", "street_number", "zip_code"),
        {'schema': '${app_schema.get('name')}'}
    )
    __tablename__ = 'address'
    street_name = sa.Column(sa.Unicode, nullable=False)
    street_number = sa.Column(sa.String, nullable=False)
    zip_code = sa.Column(sa.Integer, nullable=False)
    geom = sa.Column(Geometry('POINT', srid=${srid}))


class ${''.join(x for x in app_schema.get('name').title() if not x.isspace()).replace('_', '')}Glossary(Base):
    __table_args__ = {'schema': '${app_schema.get('name')}'}
    __tablename__ = 'glossary'
    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String, nullable=False)
    content = sa.Column(sa.String, nullable=False)


class ${''.join(x for x in app_schema.get('name').title() if not x.isspace()).replace('_', '')}ExclusionOfLiability(Base):
    __table_args__ = {'schema': '${app_schema.get('name')}'}
    __tablename__ = 'exclusion_of_liability'
    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String, nullable=False)
    content = sa.Column(sa.String, nullable=False)
% for schema in plrs:


class ${schema.get("name").capitalize()}Availability(Base):
    __table_args__ = {'schema': '${schema.get("name")}'}
    __tablename__ = 'availability'
    fosnr = sa.Column(sa.Integer, primary_key=True)
    available = sa.Column(sa.Boolean, nullable=False, default=False)


class ${schema.get("name").capitalize()}Office(Base):
    __table_args__ = {'schema': '${schema.get("name")}'}
    __tablename__ = 'office'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    office_at_web = sa.Column(sa.String, nullable=True)
    uid = sa.Column(sa.String(12), nullable=True)
    line1 = sa.Column(sa.String, nullable=True)
    line2 = sa.Column(sa.String, nullable=True)
    street = sa.Column(sa.String, nullable=True)
    number = sa.Column(sa.String, nullable=True)
    postal_code = sa.Column(sa.Integer, nullable=True)
    city = sa.Column(sa.String, nullable=True)


class ${schema.get("name").capitalize()}ReferenceDefinition(Base):  # TODO: Check translation
    __table_args__ = {'schema': '${schema.get("name")}'}
    __tablename__ = 'reference_definition'
    id = sa.Column(sa.Integer, primary_key=True)
    topic = sa.Column(sa.String, nullable=True)
    canton = sa.Column(sa.String(2), nullable=True)
    municipality = sa.Column(sa.Integer, nullable=True)
    office_id = sa.Column(sa.Integer, sa.ForeignKey(
        ${schema.get("name").capitalize()}Office.id), nullable=False
    )
    responsible_office = relationship(${schema.get("name").capitalize()}Office)


class ${schema.get("name").capitalize()}DocumentBase(Base):
    __table_args__ = {'schema': '${schema.get("name")}'}
    __tablename__ = 'document_base'
    id = sa.Column(sa.Integer, primary_key=True)
    text_web = sa.Column(sa.String, nullable=True)
    legal_state = sa.Column(sa.String, nullable=False)
    published_from = sa.Column(sa.Date, nullable=False)
    type = sa.Column(sa.Unicode, nullable=False)
    __mapper_args__ = {
        'polymorphic_identity': 'document_base',
        'polymorphic_on': type,
        'passive_updates': True
    }


class ${schema.get("name").capitalize()}Document(${schema.get("name").capitalize()}DocumentBase):
    __table_args__ = {'schema': '${schema.get("name")}'}
    __tablename__ = 'document'
    __mapper_args__ = {
        'polymorphic_identity': 'document'
    }
    title = sa.Column(sa.String, nullable=False)
    official_title = sa.Column(sa.String, nullable=True)
    abbreviation = sa.Column(sa.String, nullable=True)
    official_number = sa.Column(sa.String, nullable=True)
    canton = sa.Column(sa.String(2), nullable=True)
    municipality = sa.Column(sa.Integer, nullable=True)
    file = sa.Column(sa.Binary, nullable=True)
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(${schema.get("name").capitalize()}DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(${schema.get("name").capitalize()}Office.id),
        nullable=False
    )
    responsible_office = relationship(${schema.get("name").capitalize()}Office)


class ${schema.get("name").capitalize()}Article(${schema.get("name").capitalize()}DocumentBase):
    __table_args__ = {'schema': '${schema.get("name")}'}
    __tablename__ = 'article'
    __mapper_args__ = {
        'polymorphic_identity': 'article'
    }
    number = sa.Column(sa.String, nullable=False)
    text = sa.Column(sa.String, nullable=True)
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(${schema.get("name").capitalize()}DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(${schema.get("name").capitalize()}Document.id),
        nullable=False
    )
    document = relationship(
        ${schema.get("name").capitalize()}Document,
        backref='articles',
        foreign_keys=[document_id]
    )


class ${schema.get("name").capitalize()}LegalProvision(${schema.get("name").capitalize()}Document):
    __table_args__ = {'schema': '${schema.get("name")}'}
    __tablename__ = 'legal_provision'
    __mapper_args__ = {
        'polymorphic_identity': 'legal_provision'
    }
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(${schema.get("name").capitalize()}Document.id),
        primary_key=True,
        onupdate="cascade"
    )


class ${schema.get("name").capitalize()}ViewService(Base):
    __table_args__ = {'schema': '${schema.get("name")}'}
    __tablename__ = 'view_service'
    id = sa.Column(sa.Integer, primary_key=True)
    link_wms = sa.Column(sa.String, nullable=False)
    legend_web = sa.Column(sa.String, nullable=True)


class ${schema.get("name").capitalize()}LegendEntry(Base):
    __table_args__ = {'schema': '${schema.get("name")}'}
    __tablename__ = 'legend_entry'
    id = sa.Column(sa.Integer, primary_key=True)
    file = sa.Column(sa.Binary, nullable=False)
    legend_text = sa.Column(sa.String, nullable=False)
    type_code = sa.Column(sa.String(40), nullable=False)
    type_code_list = sa.Column(sa.String, nullable=False)
    topic = sa.Column(sa.String, nullable=False)
    subtopic = sa.Column(sa.String, nullable=True)
    additional_topic = sa.Column(sa.String, nullable=True)
    view_service_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(${schema.get("name").capitalize()}ViewService.id),
        nullable=False
    )
    view_service = relationship(${schema.get("name").capitalize()}ViewService, backref='legends')


# TODO: check how the definition in base model from confederation can be realized
class ${schema.get("name").capitalize()}PublicLawRestriction(Base):
    __table_args__ = {'schema': '${schema.get("name")}'}
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
    view_service_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(${schema.get("name").capitalize()}ViewService.id),
        nullable=True
    )
    view_service = relationship(
        ${schema.get("name").capitalize()}ViewService,
        backref='public_law_restrictions'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(${schema.get("name").capitalize()}Office.id),
        nullable=False
    )
    responsible_office = relationship(${schema.get("name").capitalize()}Office)


class ${schema.get("name").capitalize()}Geometry(Base):
    __table_args__ = {'schema': '${schema.get("name")}'}
    __tablename__ = 'geometry'
    id = sa.Column(sa.Integer, primary_key=True)
    legal_state = sa.Column(sa.String, nullable=False)
    published_from = sa.Column(sa.Date, nullable=False)
    geo_metadata = sa.Column(sa.String, nullable=True)  # TODO: Check translation
    geom = sa.Column(Geometry('${schema.get("geometry_type")}', srid=${srid}))
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(${schema.get("name").capitalize()}PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction = relationship(
        ${schema.get("name").capitalize()}PublicLawRestriction,
        backref='geometries'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(${schema.get("name").capitalize()}Office.id),
        nullable=False
    )
    responsible_office = relationship(${schema.get("name").capitalize()}Office)


class ${schema.get("name").capitalize()}PublicLawRestrictionBase(Base):
    __tablename__ = 'public_law_restriction_base'
    __table_args__ = {'schema': '${schema.get("name")}'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(${schema.get("name").capitalize()}PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(${schema.get("name").capitalize()}PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        ${schema.get("name").capitalize()}PublicLawRestriction,
        backref='basis',
        foreign_keys=[public_law_restriction_id]
    )
    base = relationship(
        ${schema.get("name").capitalize()}PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class ${schema.get("name").capitalize()}PublicLawRestrictionRefinement(Base):
    __tablename__ = 'public_law_restriction_refinement'
    __table_args__ = {'schema': '${schema.get("name")}'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(${schema.get("name").capitalize()}PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(${schema.get("name").capitalize()}PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        ${schema.get("name").capitalize()}PublicLawRestriction,
        backref='refinements',
        foreign_keys=[public_law_restriction_id]
    )
    refinement = relationship(
        ${schema.get("name").capitalize()}PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class ${schema.get("name").capitalize()}PublicLawRestrictionDocument(Base):
    __tablename__ = 'public_law_restriction_document'
    __table_args__ = {'schema': '${schema.get("name")}'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(${schema.get("name").capitalize()}PublicLawRestriction.id),
        nullable=False
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(${schema.get("name").capitalize()}DocumentBase.id),
        nullable=False
    )
    plr = relationship(
        ${schema.get("name").capitalize()}PublicLawRestriction,
        backref='legal_provisions'
    )
    document = relationship(
        ${schema.get("name").capitalize()}DocumentBase
    )
    article_numbers = sa.Column(sa.String, nullable=True)


# TODO: check translation
class ${schema.get("name").capitalize()}DocumentReference(Base):
    __tablename__ = 'document_reference'
    __table_args__ = {'schema': '${schema.get("name")}'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(${schema.get("name").capitalize()}Document.id),
        nullable=False
    )
    reference_document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(${schema.get("name").capitalize()}Document.id),
        nullable=False
    )
    document = relationship(
        ${schema.get("name").capitalize()}Document,
        backref='referenced_documents',
        foreign_keys=[document_id]
    )
    referenced_document = relationship(
        ${schema.get("name").capitalize()}Document,
        foreign_keys=[reference_document_id]
    )
    article_numbers = sa.Column(sa.String, nullable=True)


class ${schema.get("name").capitalize()}DocumentReferenceDefinition(Base):
    __tablename__ = 'document_reference_definition'
    __table_args__ = {'schema': '${schema.get("name")}'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(${schema.get("name").capitalize()}Document.id),
        nullable=False
    )
    reference_definition_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(${schema.get("name").capitalize()}ReferenceDefinition.id),
        nullable=False
    )
% endfor
