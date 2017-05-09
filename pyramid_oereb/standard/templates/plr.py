# -*- coding: utf-8 -*-
"""
This is a full representation of the data model defined by the confederations definition. You can use it to
produce a own new topic for the oereb eco system in the specifications shape. To be able to adapt this models
to your own infrastructure you must implement the same attribute names! In fact that inheritance is not easily
 made you need to make your own classes and adapt them to your database.
"""
import sqlalchemy as sa
from pyramid_oereb.standard.models import NAMING_CONVENTION
from pyramid_oereb import srid
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2.types import Geometry as GeoAlchemyGeometry
from sqlalchemy.orm import relationship

metadata = sa.MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base()

if not srid:
    srid = 2056


class Availability(Base):
    """
    A simple bucket for achieving a switch per municipality. Here you can configure via the imported data if
    a public law restriction is available or not. You need to fill it with the data you provided in the app
    schemas municipality table (fosnr).
    :attribute fosnr: The identifier of the municipality in your system (this should be mainly the id_bfs)
    :attribute available: The switch field to configure if this plr is available for the municipality or not.
    This field has direct influence on the applications behaviour. See documentation for more info.
    """
    __table_args__ = {'schema': '${schema_name}'}
    __tablename__ = 'availability'
    fosnr = sa.Column(sa.Integer, primary_key=True)
    available = sa.Column(sa.Boolean, nullable=False, default=False)


class Office(Base):
    """
    The bucket to fill in all the offices you need to reference from public law restriction, document,
    geometry.
    :attribute id: The identifier. This is used in the database only and must not be set manually. If you
    don't like-don't care about.
    :attribute name: The name of the office.
    :attribute office_at_web: A web accessible url to a presentation of this office.
    :attribute uid: The uid (id bfs) of this office.
    :attribute line1: The first address line for this office.
    :attribute line2: The second address line for this office.
    :attribute street: The streets name of the offices address.
    :attribute number: The number on street.
    :attribute postal_code: The ZIP-code.
    :attribute city: The name of the city.
    """
    __table_args__ = {'schema': '${schema_name}'}
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


class ReferenceDefinition(Base):  # TODO: Check translation
    """
    The meta bucket for definitions which are directly related to a public law restriction in a common way or
    to the whole canton or a  whole municipality.  It is used to have a place to store general documents
    which are related to an extract but not directly on a special public law restriction situation.
    :attribute id: The identifier. This is used in the database only and must not be set manually. If you
    don't like-don't care about.
    :attribute topic: The topic which this definition might be related to.
    :attribute canton: The canton this definition is related to.
    :attribute municipality: The municipality this definition is related to.
    :attribute office_id: The foreign key constraint which the definition is related to.
    """
    __table_args__ = {'schema': '${schema_name}'}
    __tablename__ = 'reference_definition'
    id = sa.Column(sa.Integer, primary_key=True)
    topic = sa.Column(sa.String, nullable=True)
    canton = sa.Column(sa.String(2), nullable=True)
    municipality = sa.Column(sa.Integer, nullable=True)
    office_id = sa.Column(sa.Integer, sa.ForeignKey(
        Office.id), nullable=False
    )
    responsible_office = relationship(Office)


class DocumentBase(Base):
    """
    In the specification documents are cascaded in a inheritance way. So this representation is used to
    produce the addressable primary key and to provide the common document attributes.
    :attribute id: The identifier. This is used in the database only and must not be set manually. If you
    don't like-don't care about.
    :attribute text_web: A link which leads to the documents content in the web.
    :attribute legal_state: The status switch if the document is legally approved or not.
    :attribute published_from: The date when the document should be available for publishing on extracts. This
    directly affects the behaviour of extract generation.
    :attribute type: This is a sqlalchemy related attribute to provide database table inheritance.
    """
    __table_args__ = {'schema': '${schema_name}'}
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


class Document(DocumentBase):
    """
    THE DOCUMENT
    This represents the main document in the whole system. It is specialized in some sub classes.
    :attribute id: The identifier. This is used in the database only and must not be set manually. If you
    don't like-don't care about.

    :attribute title: The title or if existing the short title ot his document.
    :attribute office_title: The official title of this document.
    :attribute abbrevation: The shortened version of the documents title.
    :attribute official_number: The official number which uniquely identifies this document.
    :attribute canton: The short version of the canton which this document is about. If this is None this is
        assumed to be a confederations document.
    :attribute municipality: The id bfs of the municipality. If this is None it is assumed the document is
        related to the whole canton or even the confederation.
    :attribute file: The document itself as a binary representation (PDF).
    :attribute office_id: The foreign key to the office which is in charge for this document.
    :attribute responsible_office: The dedicated relation to the office instance from database.
    """
    __table_args__ = {'schema': '${schema_name}'}
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
        sa.ForeignKey(DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Office.id),
        nullable=False
    )
    responsible_office = relationship(Office)


class Article(DocumentBase):
    """
    A subclass of the document representing articles. Article in the sense of a law document. It is often
    described as a special part of the whole law document and reflects a dedicated content of this.
    :attribute id: The identifier. This is used in the database only and must not be set manually. If you
    don't like-don't care about.
    :attribute number: The number which identifies this article in its "mother" document.
    :attribute text: A simple string to describe the article or give some related info.
    :attribute document_id: The foreign key to the document this article is taken from.
    :attribute document: The dedicated relation to the document instance from database.
    """
    __table_args__ = {'schema': '${schema_name}'}
    __tablename__ = 'article'
    __mapper_args__ = {
        'polymorphic_identity': 'article'
    }
    number = sa.Column(sa.String, nullable=False)
    text = sa.Column(sa.String, nullable=True)
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Document.id),
        nullable=False
    )
    document = relationship(
        Document,
        backref='articles',
        foreign_keys=[document_id]
    )


class LegalProvision(Document):
    """
    A subclass of the document representing legal provisions. It is a specialized class of document.
    :attribute id: The identifier. This is used in the database only and must not be set manually. If you
    don't like-don't care about.
    """
    __table_args__ = {'schema': '${schema_name}'}
    __tablename__ = 'legal_provision'
    __mapper_args__ = {
        'polymorphic_identity': 'legal_provision'
    }
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Document.id),
        primary_key=True,
        onupdate="cascade"
    )


class ViewService(Base):
    """
    A view service aka WMS which can deliver a cartographic representation via web.
    :attribute id: The identifier. This is used in the database only and must not be set manually. If you
    don't like-don't care about.
    :attribute link_wms: The actual url which leads to the desired cartographic representation.
    :attribute legend_web: A link leading to a wms describing document (png).
    """
    __table_args__ = {'schema': '${schema_name}'}
    __tablename__ = 'view_service'
    id = sa.Column(sa.Integer, primary_key=True)
    link_wms = sa.Column(sa.String, nullable=False)
    legend_web = sa.Column(sa.String, nullable=True)


class LegendEntry(Base):
    """
    A view service aka WMS which can deliver a cartographic representation via web.
    :attribute id: The identifier. This is used in the database only and must not be set manually. If you
    don't like-don't care about.
    :attribute file: An image with represents the legend entry. This can be png or svg.
    :attribute legend_text: Text to describe this legend entry.
    :attribute type_code: Type code of the public law restriction which is represented by this legend entry.
    :attribute type_code_list: List of all public law restrictions which are described through this legend
    entry.
    :attribute topic: Statement to describe to which public law restriction this legend entry belongs.
    :attribute subtopic: Description for sub topics this legend entry might belonging to.
    :attribute additional_topic: A link to additional topics. It must be like the following patterns:
    * ch.{canton}.{topic}
    * fl.{topic}
    * ch.{bfsnr}.{topic}
    This with {canton} as the official two letters short version (e.g.'BE') {topic} as the name of the topic
    and {bfsnr} as the municipality id of the federal office of statistics.
    """
    __table_args__ = {'schema': '${schema_name}'}
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
        sa.ForeignKey(ViewService.id),
        nullable=False
    )
    view_service = relationship(ViewService, backref='legends')


# TODO: check how the definition in base model from confederation can be realized
class PublicLawRestriction(Base):
    """
    The bucket where you can fill in all your public law restrictions.
    :attribute id: The identifier. This is used in the database only and must not be set manually. If you
    don't like-don't care about.
    :attribute content:
    """
    __table_args__ = {'schema': '${schema_name}'}
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
        sa.ForeignKey(ViewService.id),
        nullable=True
    )
    view_service = relationship(
        ViewService,
        backref='public_law_restrictions'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Office.id),
        nullable=False
    )
    responsible_office = relationship(Office)


class Geometry(Base):
    __table_args__ = {'schema': '${schema_name}'}
    __tablename__ = 'geometry'
    id = sa.Column(sa.Integer, primary_key=True)
    legal_state = sa.Column(sa.String, nullable=False)
    published_from = sa.Column(sa.Date, nullable=False)
    geo_metadata = sa.Column(sa.String, nullable=True)  # TODO: Check translation
    geom = sa.Column(GeoAlchemyGeometry('${geometry_type}', srid=srid))
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction = relationship(
        PublicLawRestriction,
        backref='geometries'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Office.id),
        nullable=False
    )
    responsible_office = relationship(Office)


class PublicLawRestrictionBase(Base):
    __tablename__ = 'public_law_restriction_base'
    __table_args__ = {'schema': '${schema_name}'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        PublicLawRestriction,
        backref='basis',
        foreign_keys=[public_law_restriction_id]
    )
    base = relationship(
        PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class PublicLawRestrictionRefinement(Base):
    __tablename__ = 'public_law_restriction_refinement'
    __table_args__ = {'schema': '${schema_name}'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        PublicLawRestriction,
        backref='refinements',
        foreign_keys=[public_law_restriction_id]
    )
    refinement = relationship(
        PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class PublicLawRestrictionDocument(Base):
    __tablename__ = 'public_law_restriction_document'
    __table_args__ = {'schema': '${schema_name}'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(PublicLawRestriction.id),
        nullable=False
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(DocumentBase.id),
        nullable=False
    )
    plr = relationship(
        PublicLawRestriction,
        backref='legal_provisions'
    )
    document = relationship(
        DocumentBase
    )
    article_numbers = sa.Column(sa.String, nullable=True)


# TODO: check translation
class DocumentReference(Base):
    __tablename__ = 'document_reference'
    __table_args__ = {'schema': '${schema_name}'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Document.id),
        nullable=False
    )
    reference_document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Document.id),
        nullable=False
    )
    document = relationship(
        Document,
        backref='referenced_documents',
        foreign_keys=[document_id]
    )
    referenced_document = relationship(
        Document,
        foreign_keys=[reference_document_id]
    )
    article_numbers = sa.Column(sa.String, nullable=True)


class DocumentReferenceDefinition(Base):
    __tablename__ = 'document_reference_definition'
    __table_args__ = {'schema': '${schema_name}'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Document.id),
        nullable=False
    )
    reference_definition_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(ReferenceDefinition.id),
        nullable=False
    )
