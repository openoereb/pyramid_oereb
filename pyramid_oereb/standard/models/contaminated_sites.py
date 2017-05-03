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
    __table_args__ = {'schema': 'contaminated_sites'}
    __tablename__ = 'availability'
    fosnr = sa.Column(sa.Integer, primary_key=True)
    available = sa.Column(sa.Boolean, nullable=False, default=False)


class Office(Base):
    __table_args__ = {'schema': 'contaminated_sites'}
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
    __table_args__ = {'schema': 'contaminated_sites'}
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
    __table_args__ = {'schema': 'contaminated_sites'}
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
    __table_args__ = {'schema': 'contaminated_sites'}
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
    __table_args__ = {'schema': 'contaminated_sites'}
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
    __table_args__ = {'schema': 'contaminated_sites'}
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
    __table_args__ = {'schema': 'contaminated_sites'}
    __tablename__ = 'view_service'
    id = sa.Column(sa.Integer, primary_key=True)
    link_wms = sa.Column(sa.String, nullable=False)
    legend_web = sa.Column(sa.String, nullable=True)


class LegendEntry(Base):
    __table_args__ = {'schema': 'contaminated_sites'}
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
    __table_args__ = {'schema': 'contaminated_sites'}
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
    __table_args__ = {'schema': 'contaminated_sites'}
    __tablename__ = 'geometry'
    id = sa.Column(sa.Integer, primary_key=True)
    legal_state = sa.Column(sa.String, nullable=False)
    published_from = sa.Column(sa.Date, nullable=False)
    geo_metadata = sa.Column(sa.String, nullable=True)  # TODO: Check translation
    geom = sa.Column(GeoAlchemyGeometry('POLYGON', srid=srid))
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
    __table_args__ = {'schema': 'contaminated_sites'}
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
    __table_args__ = {'schema': 'contaminated_sites'}
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
    __table_args__ = {'schema': 'contaminated_sites'}
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
    __table_args__ = {'schema': 'contaminated_sites'}
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
    __table_args__ = {'schema': 'contaminated_sites'}
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
