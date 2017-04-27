
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


class PyramidOerebMainMunicipality(Base):
    __table_args__ = {'schema': 'pyramid_oereb_main'}
    __tablename__ = 'municipality'
    fosnr = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    published = sa.Column(sa.Boolean, nullable=False, default=False, server_default=sqlalchemy.text('FALSE'))
    logo = sa.Column(sa.String, nullable=False)
    geom = sa.Column(Geometry('MULTIPOLYGON', srid=2056), nullable=True)


class PyramidOerebMainRealEstate(Base):
    __table_args__ = {'schema': 'pyramid_oereb_main'}
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
    limit = sa.Column(Geometry('MULTIPOLYGON', srid=2056))


class PyramidOerebMainAddress(Base):
    __table_args__ = (
        PrimaryKeyConstraint("street_name", "street_number", "zip_code"),
        {'schema': 'pyramid_oereb_main'}
    )
    __tablename__ = 'address'
    street_name = sa.Column(sa.Unicode, nullable=False)
    street_number = sa.Column(sa.String, nullable=False)
    zip_code = sa.Column(sa.Integer, nullable=False)
    geom = sa.Column(Geometry('POINT', srid=2056))


class PyramidOerebMainGlossary(Base):
    __table_args__ = {'schema': 'pyramid_oereb_main'}
    __tablename__ = 'glossary'
    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String, nullable=False)
    content = sa.Column(sa.String, nullable=False)


class PyramidOerebMainExclusionOfLiability(Base):
    __table_args__ = {'schema': 'pyramid_oereb_main'}
    __tablename__ = 'exclusion_of_liability'
    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String, nullable=False)
    content = sa.Column(sa.String, nullable=False)


class Plr73Availability(Base):
    __table_args__ = {'schema': 'plr73'}
    __tablename__ = 'availability'
    fosnr = sa.Column(sa.Integer, primary_key=True)
    available = sa.Column(sa.Boolean, nullable=False, default=False)


class Plr73Office(Base):
    __table_args__ = {'schema': 'plr73'}
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


class Plr73ReferenceDefinition(Base):  # TODO: Check translation
    __table_args__ = {'schema': 'plr73'}
    __tablename__ = 'reference_definition'
    id = sa.Column(sa.Integer, primary_key=True)
    topic = sa.Column(sa.String, nullable=True)
    canton = sa.Column(sa.String(2), nullable=True)
    municipality = sa.Column(sa.Integer, nullable=True)
    office_id = sa.Column(sa.Integer, sa.ForeignKey(
        Plr73Office.id), nullable=False
    )
    responsible_office = relationship(Plr73Office)


class Plr73DocumentBase(Base):
    __table_args__ = {'schema': 'plr73'}
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


class Plr73Document(Plr73DocumentBase):
    __table_args__ = {'schema': 'plr73'}
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
        sa.ForeignKey(Plr73DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr73Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr73Office)


class Plr73Article(Plr73DocumentBase):
    __table_args__ = {'schema': 'plr73'}
    __tablename__ = 'article'
    __mapper_args__ = {
        'polymorphic_identity': 'article'
    }
    number = sa.Column(sa.String, nullable=False)
    text = sa.Column(sa.String, nullable=True)
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr73DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr73Document.id),
        nullable=False
    )
    document = relationship(
        Plr73Document,
        backref='articles',
        foreign_keys=[document_id]
    )


class Plr73LegalProvision(Plr73Document):
    __table_args__ = {'schema': 'plr73'}
    __tablename__ = 'legal_provision'
    __mapper_args__ = {
        'polymorphic_identity': 'legal_provision'
    }
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr73Document.id),
        primary_key=True,
        onupdate="cascade"
    )


class Plr73ViewService(Base):
    __table_args__ = {'schema': 'plr73'}
    __tablename__ = 'view_service'
    id = sa.Column(sa.Integer, primary_key=True)
    link_wms = sa.Column(sa.String, nullable=False)
    legend_web = sa.Column(sa.String, nullable=True)


class Plr73LegendEntry(Base):
    __table_args__ = {'schema': 'plr73'}
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
        sa.ForeignKey(Plr73ViewService.id),
        nullable=False
    )
    view_service = relationship(Plr73ViewService, backref='legends')


# TODO: check how the definition in base model from confederation can be realized
class Plr73PublicLawRestriction(Base):
    __table_args__ = {'schema': 'plr73'}
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
        sa.ForeignKey(Plr73ViewService.id),
        nullable=True
    )
    view_service = relationship(
        Plr73ViewService,
        backref='public_law_restrictions'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr73Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr73Office)


class Plr73Geometry(Base):
    __table_args__ = {'schema': 'plr73'}
    __tablename__ = 'geometry'
    id = sa.Column(sa.Integer, primary_key=True)
    legal_state = sa.Column(sa.String, nullable=False)
    published_from = sa.Column(sa.Date, nullable=False)
    geo_metadata = sa.Column(sa.String, nullable=True)  # TODO: Check translation
    geom = sa.Column(Geometry('LINESTRING', srid=2056))
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr73PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction = relationship(
        Plr73PublicLawRestriction,
        backref='geometries'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr73Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr73Office)


class Plr73PublicLawRestrictionBase(Base):
    __tablename__ = 'public_law_restriction_base'
    __table_args__ = {'schema': 'plr73'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr73PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr73PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr73PublicLawRestriction,
        backref='basis',
        foreign_keys=[public_law_restriction_id]
    )
    base = relationship(
        Plr73PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr73PublicLawRestrictionRefinement(Base):
    __tablename__ = 'public_law_restriction_refinement'
    __table_args__ = {'schema': 'plr73'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr73PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr73PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr73PublicLawRestriction,
        backref='refinements',
        foreign_keys=[public_law_restriction_id]
    )
    refinement = relationship(
        Plr73PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr73PublicLawRestrictionDocument(Base):
    __tablename__ = 'public_law_restriction_document'
    __table_args__ = {'schema': 'plr73'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr73PublicLawRestriction.id),
        nullable=False
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr73DocumentBase.id),
        nullable=False
    )
    plr = relationship(
        Plr73PublicLawRestriction,
        backref='legal_provisions'
    )
    document = relationship(
        Plr73DocumentBase
    )
    article_numbers = sa.Column(sa.String, nullable=True)


# TODO: check translation
class Plr73DocumentReference(Base):
    __tablename__ = 'document_reference'
    __table_args__ = {'schema': 'plr73'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr73Document.id),
        nullable=False
    )
    reference_document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr73Document.id),
        nullable=False
    )
    document = relationship(
        Plr73Document,
        backref='referenced_documents',
        foreign_keys=[document_id]
    )
    referenced_document = relationship(
        Plr73Document,
        foreign_keys=[reference_document_id]
    )
    article_numbers = sa.Column(sa.String, nullable=True)


class Plr73DocumentReferenceDefinition(Base):
    __tablename__ = 'document_reference_definition'
    __table_args__ = {'schema': 'plr73'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr73Document.id),
        nullable=False
    )
    reference_definition_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr73ReferenceDefinition.id),
        nullable=False
    )


class Plr87Availability(Base):
    __table_args__ = {'schema': 'plr87'}
    __tablename__ = 'availability'
    fosnr = sa.Column(sa.Integer, primary_key=True)
    available = sa.Column(sa.Boolean, nullable=False, default=False)


class Plr87Office(Base):
    __table_args__ = {'schema': 'plr87'}
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


class Plr87ReferenceDefinition(Base):  # TODO: Check translation
    __table_args__ = {'schema': 'plr87'}
    __tablename__ = 'reference_definition'
    id = sa.Column(sa.Integer, primary_key=True)
    topic = sa.Column(sa.String, nullable=True)
    canton = sa.Column(sa.String(2), nullable=True)
    municipality = sa.Column(sa.Integer, nullable=True)
    office_id = sa.Column(sa.Integer, sa.ForeignKey(
        Plr87Office.id), nullable=False
    )
    responsible_office = relationship(Plr87Office)


class Plr87DocumentBase(Base):
    __table_args__ = {'schema': 'plr87'}
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


class Plr87Document(Plr87DocumentBase):
    __table_args__ = {'schema': 'plr87'}
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
        sa.ForeignKey(Plr87DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr87Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr87Office)


class Plr87Article(Plr87DocumentBase):
    __table_args__ = {'schema': 'plr87'}
    __tablename__ = 'article'
    __mapper_args__ = {
        'polymorphic_identity': 'article'
    }
    number = sa.Column(sa.String, nullable=False)
    text = sa.Column(sa.String, nullable=True)
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr87DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr87Document.id),
        nullable=False
    )
    document = relationship(
        Plr87Document,
        backref='articles',
        foreign_keys=[document_id]
    )


class Plr87LegalProvision(Plr87Document):
    __table_args__ = {'schema': 'plr87'}
    __tablename__ = 'legal_provision'
    __mapper_args__ = {
        'polymorphic_identity': 'legal_provision'
    }
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr87Document.id),
        primary_key=True,
        onupdate="cascade"
    )


class Plr87ViewService(Base):
    __table_args__ = {'schema': 'plr87'}
    __tablename__ = 'view_service'
    id = sa.Column(sa.Integer, primary_key=True)
    link_wms = sa.Column(sa.String, nullable=False)
    legend_web = sa.Column(sa.String, nullable=True)


class Plr87LegendEntry(Base):
    __table_args__ = {'schema': 'plr87'}
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
        sa.ForeignKey(Plr87ViewService.id),
        nullable=False
    )
    view_service = relationship(Plr87ViewService, backref='legends')


# TODO: check how the definition in base model from confederation can be realized
class Plr87PublicLawRestriction(Base):
    __table_args__ = {'schema': 'plr87'}
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
        sa.ForeignKey(Plr87ViewService.id),
        nullable=True
    )
    view_service = relationship(
        Plr87ViewService,
        backref='public_law_restrictions'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr87Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr87Office)


class Plr87Geometry(Base):
    __table_args__ = {'schema': 'plr87'}
    __tablename__ = 'geometry'
    id = sa.Column(sa.Integer, primary_key=True)
    legal_state = sa.Column(sa.String, nullable=False)
    published_from = sa.Column(sa.Date, nullable=False)
    geo_metadata = sa.Column(sa.String, nullable=True)  # TODO: Check translation
    geom = sa.Column(Geometry('LINESTRING', srid=2056))
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr87PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction = relationship(
        Plr87PublicLawRestriction,
        backref='geometries'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr87Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr87Office)


class Plr87PublicLawRestrictionBase(Base):
    __tablename__ = 'public_law_restriction_base'
    __table_args__ = {'schema': 'plr87'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr87PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr87PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr87PublicLawRestriction,
        backref='basis',
        foreign_keys=[public_law_restriction_id]
    )
    base = relationship(
        Plr87PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr87PublicLawRestrictionRefinement(Base):
    __tablename__ = 'public_law_restriction_refinement'
    __table_args__ = {'schema': 'plr87'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr87PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr87PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr87PublicLawRestriction,
        backref='refinements',
        foreign_keys=[public_law_restriction_id]
    )
    refinement = relationship(
        Plr87PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr87PublicLawRestrictionDocument(Base):
    __tablename__ = 'public_law_restriction_document'
    __table_args__ = {'schema': 'plr87'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr87PublicLawRestriction.id),
        nullable=False
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr87DocumentBase.id),
        nullable=False
    )
    plr = relationship(
        Plr87PublicLawRestriction,
        backref='legal_provisions'
    )
    document = relationship(
        Plr87DocumentBase
    )
    article_numbers = sa.Column(sa.String, nullable=True)


# TODO: check translation
class Plr87DocumentReference(Base):
    __tablename__ = 'document_reference'
    __table_args__ = {'schema': 'plr87'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr87Document.id),
        nullable=False
    )
    reference_document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr87Document.id),
        nullable=False
    )
    document = relationship(
        Plr87Document,
        backref='referenced_documents',
        foreign_keys=[document_id]
    )
    referenced_document = relationship(
        Plr87Document,
        foreign_keys=[reference_document_id]
    )
    article_numbers = sa.Column(sa.String, nullable=True)


class Plr87DocumentReferenceDefinition(Base):
    __tablename__ = 'document_reference_definition'
    __table_args__ = {'schema': 'plr87'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr87Document.id),
        nullable=False
    )
    reference_definition_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr87ReferenceDefinition.id),
        nullable=False
    )


class Plr88Availability(Base):
    __table_args__ = {'schema': 'plr88'}
    __tablename__ = 'availability'
    fosnr = sa.Column(sa.Integer, primary_key=True)
    available = sa.Column(sa.Boolean, nullable=False, default=False)


class Plr88Office(Base):
    __table_args__ = {'schema': 'plr88'}
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


class Plr88ReferenceDefinition(Base):  # TODO: Check translation
    __table_args__ = {'schema': 'plr88'}
    __tablename__ = 'reference_definition'
    id = sa.Column(sa.Integer, primary_key=True)
    topic = sa.Column(sa.String, nullable=True)
    canton = sa.Column(sa.String(2), nullable=True)
    municipality = sa.Column(sa.Integer, nullable=True)
    office_id = sa.Column(sa.Integer, sa.ForeignKey(
        Plr88Office.id), nullable=False
    )
    responsible_office = relationship(Plr88Office)


class Plr88DocumentBase(Base):
    __table_args__ = {'schema': 'plr88'}
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


class Plr88Document(Plr88DocumentBase):
    __table_args__ = {'schema': 'plr88'}
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
        sa.ForeignKey(Plr88DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr88Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr88Office)


class Plr88Article(Plr88DocumentBase):
    __table_args__ = {'schema': 'plr88'}
    __tablename__ = 'article'
    __mapper_args__ = {
        'polymorphic_identity': 'article'
    }
    number = sa.Column(sa.String, nullable=False)
    text = sa.Column(sa.String, nullable=True)
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr88DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr88Document.id),
        nullable=False
    )
    document = relationship(
        Plr88Document,
        backref='articles',
        foreign_keys=[document_id]
    )


class Plr88LegalProvision(Plr88Document):
    __table_args__ = {'schema': 'plr88'}
    __tablename__ = 'legal_provision'
    __mapper_args__ = {
        'polymorphic_identity': 'legal_provision'
    }
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr88Document.id),
        primary_key=True,
        onupdate="cascade"
    )


class Plr88ViewService(Base):
    __table_args__ = {'schema': 'plr88'}
    __tablename__ = 'view_service'
    id = sa.Column(sa.Integer, primary_key=True)
    link_wms = sa.Column(sa.String, nullable=False)
    legend_web = sa.Column(sa.String, nullable=True)


class Plr88LegendEntry(Base):
    __table_args__ = {'schema': 'plr88'}
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
        sa.ForeignKey(Plr88ViewService.id),
        nullable=False
    )
    view_service = relationship(Plr88ViewService, backref='legends')


# TODO: check how the definition in base model from confederation can be realized
class Plr88PublicLawRestriction(Base):
    __table_args__ = {'schema': 'plr88'}
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
        sa.ForeignKey(Plr88ViewService.id),
        nullable=True
    )
    view_service = relationship(
        Plr88ViewService,
        backref='public_law_restrictions'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr88Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr88Office)


class Plr88Geometry(Base):
    __table_args__ = {'schema': 'plr88'}
    __tablename__ = 'geometry'
    id = sa.Column(sa.Integer, primary_key=True)
    legal_state = sa.Column(sa.String, nullable=False)
    published_from = sa.Column(sa.Date, nullable=False)
    geo_metadata = sa.Column(sa.String, nullable=True)  # TODO: Check translation
    geom = sa.Column(Geometry('LINESTRING', srid=2056))
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr88PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction = relationship(
        Plr88PublicLawRestriction,
        backref='geometries'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr88Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr88Office)


class Plr88PublicLawRestrictionBase(Base):
    __tablename__ = 'public_law_restriction_base'
    __table_args__ = {'schema': 'plr88'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr88PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr88PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr88PublicLawRestriction,
        backref='basis',
        foreign_keys=[public_law_restriction_id]
    )
    base = relationship(
        Plr88PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr88PublicLawRestrictionRefinement(Base):
    __tablename__ = 'public_law_restriction_refinement'
    __table_args__ = {'schema': 'plr88'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr88PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr88PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr88PublicLawRestriction,
        backref='refinements',
        foreign_keys=[public_law_restriction_id]
    )
    refinement = relationship(
        Plr88PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr88PublicLawRestrictionDocument(Base):
    __tablename__ = 'public_law_restriction_document'
    __table_args__ = {'schema': 'plr88'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr88PublicLawRestriction.id),
        nullable=False
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr88DocumentBase.id),
        nullable=False
    )
    plr = relationship(
        Plr88PublicLawRestriction,
        backref='legal_provisions'
    )
    document = relationship(
        Plr88DocumentBase
    )
    article_numbers = sa.Column(sa.String, nullable=True)


# TODO: check translation
class Plr88DocumentReference(Base):
    __tablename__ = 'document_reference'
    __table_args__ = {'schema': 'plr88'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr88Document.id),
        nullable=False
    )
    reference_document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr88Document.id),
        nullable=False
    )
    document = relationship(
        Plr88Document,
        backref='referenced_documents',
        foreign_keys=[document_id]
    )
    referenced_document = relationship(
        Plr88Document,
        foreign_keys=[reference_document_id]
    )
    article_numbers = sa.Column(sa.String, nullable=True)


class Plr88DocumentReferenceDefinition(Base):
    __tablename__ = 'document_reference_definition'
    __table_args__ = {'schema': 'plr88'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr88Document.id),
        nullable=False
    )
    reference_definition_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr88ReferenceDefinition.id),
        nullable=False
    )


class Plr97Availability(Base):
    __table_args__ = {'schema': 'plr97'}
    __tablename__ = 'availability'
    fosnr = sa.Column(sa.Integer, primary_key=True)
    available = sa.Column(sa.Boolean, nullable=False, default=False)


class Plr97Office(Base):
    __table_args__ = {'schema': 'plr97'}
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


class Plr97ReferenceDefinition(Base):  # TODO: Check translation
    __table_args__ = {'schema': 'plr97'}
    __tablename__ = 'reference_definition'
    id = sa.Column(sa.Integer, primary_key=True)
    topic = sa.Column(sa.String, nullable=True)
    canton = sa.Column(sa.String(2), nullable=True)
    municipality = sa.Column(sa.Integer, nullable=True)
    office_id = sa.Column(sa.Integer, sa.ForeignKey(
        Plr97Office.id), nullable=False
    )
    responsible_office = relationship(Plr97Office)


class Plr97DocumentBase(Base):
    __table_args__ = {'schema': 'plr97'}
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


class Plr97Document(Plr97DocumentBase):
    __table_args__ = {'schema': 'plr97'}
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
        sa.ForeignKey(Plr97DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr97Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr97Office)


class Plr97Article(Plr97DocumentBase):
    __table_args__ = {'schema': 'plr97'}
    __tablename__ = 'article'
    __mapper_args__ = {
        'polymorphic_identity': 'article'
    }
    number = sa.Column(sa.String, nullable=False)
    text = sa.Column(sa.String, nullable=True)
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr97DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr97Document.id),
        nullable=False
    )
    document = relationship(
        Plr97Document,
        backref='articles',
        foreign_keys=[document_id]
    )


class Plr97LegalProvision(Plr97Document):
    __table_args__ = {'schema': 'plr97'}
    __tablename__ = 'legal_provision'
    __mapper_args__ = {
        'polymorphic_identity': 'legal_provision'
    }
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr97Document.id),
        primary_key=True,
        onupdate="cascade"
    )


class Plr97ViewService(Base):
    __table_args__ = {'schema': 'plr97'}
    __tablename__ = 'view_service'
    id = sa.Column(sa.Integer, primary_key=True)
    link_wms = sa.Column(sa.String, nullable=False)
    legend_web = sa.Column(sa.String, nullable=True)


class Plr97LegendEntry(Base):
    __table_args__ = {'schema': 'plr97'}
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
        sa.ForeignKey(Plr97ViewService.id),
        nullable=False
    )
    view_service = relationship(Plr97ViewService, backref='legends')


# TODO: check how the definition in base model from confederation can be realized
class Plr97PublicLawRestriction(Base):
    __table_args__ = {'schema': 'plr97'}
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
        sa.ForeignKey(Plr97ViewService.id),
        nullable=True
    )
    view_service = relationship(
        Plr97ViewService,
        backref='public_law_restrictions'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr97Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr97Office)


class Plr97Geometry(Base):
    __table_args__ = {'schema': 'plr97'}
    __tablename__ = 'geometry'
    id = sa.Column(sa.Integer, primary_key=True)
    legal_state = sa.Column(sa.String, nullable=False)
    published_from = sa.Column(sa.Date, nullable=False)
    geo_metadata = sa.Column(sa.String, nullable=True)  # TODO: Check translation
    geom = sa.Column(Geometry('LINESTRING', srid=2056))
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr97PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction = relationship(
        Plr97PublicLawRestriction,
        backref='geometries'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr97Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr97Office)


class Plr97PublicLawRestrictionBase(Base):
    __tablename__ = 'public_law_restriction_base'
    __table_args__ = {'schema': 'plr97'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr97PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr97PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr97PublicLawRestriction,
        backref='basis',
        foreign_keys=[public_law_restriction_id]
    )
    base = relationship(
        Plr97PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr97PublicLawRestrictionRefinement(Base):
    __tablename__ = 'public_law_restriction_refinement'
    __table_args__ = {'schema': 'plr97'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr97PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr97PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr97PublicLawRestriction,
        backref='refinements',
        foreign_keys=[public_law_restriction_id]
    )
    refinement = relationship(
        Plr97PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr97PublicLawRestrictionDocument(Base):
    __tablename__ = 'public_law_restriction_document'
    __table_args__ = {'schema': 'plr97'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr97PublicLawRestriction.id),
        nullable=False
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr97DocumentBase.id),
        nullable=False
    )
    plr = relationship(
        Plr97PublicLawRestriction,
        backref='legal_provisions'
    )
    document = relationship(
        Plr97DocumentBase
    )
    article_numbers = sa.Column(sa.String, nullable=True)


# TODO: check translation
class Plr97DocumentReference(Base):
    __tablename__ = 'document_reference'
    __table_args__ = {'schema': 'plr97'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr97Document.id),
        nullable=False
    )
    reference_document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr97Document.id),
        nullable=False
    )
    document = relationship(
        Plr97Document,
        backref='referenced_documents',
        foreign_keys=[document_id]
    )
    referenced_document = relationship(
        Plr97Document,
        foreign_keys=[reference_document_id]
    )
    article_numbers = sa.Column(sa.String, nullable=True)


class Plr97DocumentReferenceDefinition(Base):
    __tablename__ = 'document_reference_definition'
    __table_args__ = {'schema': 'plr97'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr97Document.id),
        nullable=False
    )
    reference_definition_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr97ReferenceDefinition.id),
        nullable=False
    )


class Plr96Availability(Base):
    __table_args__ = {'schema': 'plr96'}
    __tablename__ = 'availability'
    fosnr = sa.Column(sa.Integer, primary_key=True)
    available = sa.Column(sa.Boolean, nullable=False, default=False)


class Plr96Office(Base):
    __table_args__ = {'schema': 'plr96'}
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


class Plr96ReferenceDefinition(Base):  # TODO: Check translation
    __table_args__ = {'schema': 'plr96'}
    __tablename__ = 'reference_definition'
    id = sa.Column(sa.Integer, primary_key=True)
    topic = sa.Column(sa.String, nullable=True)
    canton = sa.Column(sa.String(2), nullable=True)
    municipality = sa.Column(sa.Integer, nullable=True)
    office_id = sa.Column(sa.Integer, sa.ForeignKey(
        Plr96Office.id), nullable=False
    )
    responsible_office = relationship(Plr96Office)


class Plr96DocumentBase(Base):
    __table_args__ = {'schema': 'plr96'}
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


class Plr96Document(Plr96DocumentBase):
    __table_args__ = {'schema': 'plr96'}
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
        sa.ForeignKey(Plr96DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr96Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr96Office)


class Plr96Article(Plr96DocumentBase):
    __table_args__ = {'schema': 'plr96'}
    __tablename__ = 'article'
    __mapper_args__ = {
        'polymorphic_identity': 'article'
    }
    number = sa.Column(sa.String, nullable=False)
    text = sa.Column(sa.String, nullable=True)
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr96DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr96Document.id),
        nullable=False
    )
    document = relationship(
        Plr96Document,
        backref='articles',
        foreign_keys=[document_id]
    )


class Plr96LegalProvision(Plr96Document):
    __table_args__ = {'schema': 'plr96'}
    __tablename__ = 'legal_provision'
    __mapper_args__ = {
        'polymorphic_identity': 'legal_provision'
    }
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr96Document.id),
        primary_key=True,
        onupdate="cascade"
    )


class Plr96ViewService(Base):
    __table_args__ = {'schema': 'plr96'}
    __tablename__ = 'view_service'
    id = sa.Column(sa.Integer, primary_key=True)
    link_wms = sa.Column(sa.String, nullable=False)
    legend_web = sa.Column(sa.String, nullable=True)


class Plr96LegendEntry(Base):
    __table_args__ = {'schema': 'plr96'}
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
        sa.ForeignKey(Plr96ViewService.id),
        nullable=False
    )
    view_service = relationship(Plr96ViewService, backref='legends')


# TODO: check how the definition in base model from confederation can be realized
class Plr96PublicLawRestriction(Base):
    __table_args__ = {'schema': 'plr96'}
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
        sa.ForeignKey(Plr96ViewService.id),
        nullable=True
    )
    view_service = relationship(
        Plr96ViewService,
        backref='public_law_restrictions'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr96Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr96Office)


class Plr96Geometry(Base):
    __table_args__ = {'schema': 'plr96'}
    __tablename__ = 'geometry'
    id = sa.Column(sa.Integer, primary_key=True)
    legal_state = sa.Column(sa.String, nullable=False)
    published_from = sa.Column(sa.Date, nullable=False)
    geo_metadata = sa.Column(sa.String, nullable=True)  # TODO: Check translation
    geom = sa.Column(Geometry('POLYGON', srid=2056))
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr96PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction = relationship(
        Plr96PublicLawRestriction,
        backref='geometries'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr96Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr96Office)


class Plr96PublicLawRestrictionBase(Base):
    __tablename__ = 'public_law_restriction_base'
    __table_args__ = {'schema': 'plr96'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr96PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr96PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr96PublicLawRestriction,
        backref='basis',
        foreign_keys=[public_law_restriction_id]
    )
    base = relationship(
        Plr96PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr96PublicLawRestrictionRefinement(Base):
    __tablename__ = 'public_law_restriction_refinement'
    __table_args__ = {'schema': 'plr96'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr96PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr96PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr96PublicLawRestriction,
        backref='refinements',
        foreign_keys=[public_law_restriction_id]
    )
    refinement = relationship(
        Plr96PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr96PublicLawRestrictionDocument(Base):
    __tablename__ = 'public_law_restriction_document'
    __table_args__ = {'schema': 'plr96'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr96PublicLawRestriction.id),
        nullable=False
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr96DocumentBase.id),
        nullable=False
    )
    plr = relationship(
        Plr96PublicLawRestriction,
        backref='legal_provisions'
    )
    document = relationship(
        Plr96DocumentBase
    )
    article_numbers = sa.Column(sa.String, nullable=True)


# TODO: check translation
class Plr96DocumentReference(Base):
    __tablename__ = 'document_reference'
    __table_args__ = {'schema': 'plr96'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr96Document.id),
        nullable=False
    )
    reference_document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr96Document.id),
        nullable=False
    )
    document = relationship(
        Plr96Document,
        backref='referenced_documents',
        foreign_keys=[document_id]
    )
    referenced_document = relationship(
        Plr96Document,
        foreign_keys=[reference_document_id]
    )
    article_numbers = sa.Column(sa.String, nullable=True)


class Plr96DocumentReferenceDefinition(Base):
    __tablename__ = 'document_reference_definition'
    __table_args__ = {'schema': 'plr96'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr96Document.id),
        nullable=False
    )
    reference_definition_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr96ReferenceDefinition.id),
        nullable=False
    )


class Plr103Availability(Base):
    __table_args__ = {'schema': 'plr103'}
    __tablename__ = 'availability'
    fosnr = sa.Column(sa.Integer, primary_key=True)
    available = sa.Column(sa.Boolean, nullable=False, default=False)


class Plr103Office(Base):
    __table_args__ = {'schema': 'plr103'}
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


class Plr103ReferenceDefinition(Base):  # TODO: Check translation
    __table_args__ = {'schema': 'plr103'}
    __tablename__ = 'reference_definition'
    id = sa.Column(sa.Integer, primary_key=True)
    topic = sa.Column(sa.String, nullable=True)
    canton = sa.Column(sa.String(2), nullable=True)
    municipality = sa.Column(sa.Integer, nullable=True)
    office_id = sa.Column(sa.Integer, sa.ForeignKey(
        Plr103Office.id), nullable=False
    )
    responsible_office = relationship(Plr103Office)


class Plr103DocumentBase(Base):
    __table_args__ = {'schema': 'plr103'}
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


class Plr103Document(Plr103DocumentBase):
    __table_args__ = {'schema': 'plr103'}
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
        sa.ForeignKey(Plr103DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr103Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr103Office)


class Plr103Article(Plr103DocumentBase):
    __table_args__ = {'schema': 'plr103'}
    __tablename__ = 'article'
    __mapper_args__ = {
        'polymorphic_identity': 'article'
    }
    number = sa.Column(sa.String, nullable=False)
    text = sa.Column(sa.String, nullable=True)
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr103DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr103Document.id),
        nullable=False
    )
    document = relationship(
        Plr103Document,
        backref='articles',
        foreign_keys=[document_id]
    )


class Plr103LegalProvision(Plr103Document):
    __table_args__ = {'schema': 'plr103'}
    __tablename__ = 'legal_provision'
    __mapper_args__ = {
        'polymorphic_identity': 'legal_provision'
    }
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr103Document.id),
        primary_key=True,
        onupdate="cascade"
    )


class Plr103ViewService(Base):
    __table_args__ = {'schema': 'plr103'}
    __tablename__ = 'view_service'
    id = sa.Column(sa.Integer, primary_key=True)
    link_wms = sa.Column(sa.String, nullable=False)
    legend_web = sa.Column(sa.String, nullable=True)


class Plr103LegendEntry(Base):
    __table_args__ = {'schema': 'plr103'}
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
        sa.ForeignKey(Plr103ViewService.id),
        nullable=False
    )
    view_service = relationship(Plr103ViewService, backref='legends')


# TODO: check how the definition in base model from confederation can be realized
class Plr103PublicLawRestriction(Base):
    __table_args__ = {'schema': 'plr103'}
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
        sa.ForeignKey(Plr103ViewService.id),
        nullable=True
    )
    view_service = relationship(
        Plr103ViewService,
        backref='public_law_restrictions'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr103Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr103Office)


class Plr103Geometry(Base):
    __table_args__ = {'schema': 'plr103'}
    __tablename__ = 'geometry'
    id = sa.Column(sa.Integer, primary_key=True)
    legal_state = sa.Column(sa.String, nullable=False)
    published_from = sa.Column(sa.Date, nullable=False)
    geo_metadata = sa.Column(sa.String, nullable=True)  # TODO: Check translation
    geom = sa.Column(Geometry('POLYGON', srid=2056))
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr103PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction = relationship(
        Plr103PublicLawRestriction,
        backref='geometries'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr103Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr103Office)


class Plr103PublicLawRestrictionBase(Base):
    __tablename__ = 'public_law_restriction_base'
    __table_args__ = {'schema': 'plr103'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr103PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr103PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr103PublicLawRestriction,
        backref='basis',
        foreign_keys=[public_law_restriction_id]
    )
    base = relationship(
        Plr103PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr103PublicLawRestrictionRefinement(Base):
    __tablename__ = 'public_law_restriction_refinement'
    __table_args__ = {'schema': 'plr103'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr103PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr103PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr103PublicLawRestriction,
        backref='refinements',
        foreign_keys=[public_law_restriction_id]
    )
    refinement = relationship(
        Plr103PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr103PublicLawRestrictionDocument(Base):
    __tablename__ = 'public_law_restriction_document'
    __table_args__ = {'schema': 'plr103'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr103PublicLawRestriction.id),
        nullable=False
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr103DocumentBase.id),
        nullable=False
    )
    plr = relationship(
        Plr103PublicLawRestriction,
        backref='legal_provisions'
    )
    document = relationship(
        Plr103DocumentBase
    )
    article_numbers = sa.Column(sa.String, nullable=True)


# TODO: check translation
class Plr103DocumentReference(Base):
    __tablename__ = 'document_reference'
    __table_args__ = {'schema': 'plr103'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr103Document.id),
        nullable=False
    )
    reference_document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr103Document.id),
        nullable=False
    )
    document = relationship(
        Plr103Document,
        backref='referenced_documents',
        foreign_keys=[document_id]
    )
    referenced_document = relationship(
        Plr103Document,
        foreign_keys=[reference_document_id]
    )
    article_numbers = sa.Column(sa.String, nullable=True)


class Plr103DocumentReferenceDefinition(Base):
    __tablename__ = 'document_reference_definition'
    __table_args__ = {'schema': 'plr103'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr103Document.id),
        nullable=False
    )
    reference_definition_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr103ReferenceDefinition.id),
        nullable=False
    )


class Plr104Availability(Base):
    __table_args__ = {'schema': 'plr104'}
    __tablename__ = 'availability'
    fosnr = sa.Column(sa.Integer, primary_key=True)
    available = sa.Column(sa.Boolean, nullable=False, default=False)


class Plr104Office(Base):
    __table_args__ = {'schema': 'plr104'}
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


class Plr104ReferenceDefinition(Base):  # TODO: Check translation
    __table_args__ = {'schema': 'plr104'}
    __tablename__ = 'reference_definition'
    id = sa.Column(sa.Integer, primary_key=True)
    topic = sa.Column(sa.String, nullable=True)
    canton = sa.Column(sa.String(2), nullable=True)
    municipality = sa.Column(sa.Integer, nullable=True)
    office_id = sa.Column(sa.Integer, sa.ForeignKey(
        Plr104Office.id), nullable=False
    )
    responsible_office = relationship(Plr104Office)


class Plr104DocumentBase(Base):
    __table_args__ = {'schema': 'plr104'}
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


class Plr104Document(Plr104DocumentBase):
    __table_args__ = {'schema': 'plr104'}
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
        sa.ForeignKey(Plr104DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr104Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr104Office)


class Plr104Article(Plr104DocumentBase):
    __table_args__ = {'schema': 'plr104'}
    __tablename__ = 'article'
    __mapper_args__ = {
        'polymorphic_identity': 'article'
    }
    number = sa.Column(sa.String, nullable=False)
    text = sa.Column(sa.String, nullable=True)
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr104DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr104Document.id),
        nullable=False
    )
    document = relationship(
        Plr104Document,
        backref='articles',
        foreign_keys=[document_id]
    )


class Plr104LegalProvision(Plr104Document):
    __table_args__ = {'schema': 'plr104'}
    __tablename__ = 'legal_provision'
    __mapper_args__ = {
        'polymorphic_identity': 'legal_provision'
    }
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr104Document.id),
        primary_key=True,
        onupdate="cascade"
    )


class Plr104ViewService(Base):
    __table_args__ = {'schema': 'plr104'}
    __tablename__ = 'view_service'
    id = sa.Column(sa.Integer, primary_key=True)
    link_wms = sa.Column(sa.String, nullable=False)
    legend_web = sa.Column(sa.String, nullable=True)


class Plr104LegendEntry(Base):
    __table_args__ = {'schema': 'plr104'}
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
        sa.ForeignKey(Plr104ViewService.id),
        nullable=False
    )
    view_service = relationship(Plr104ViewService, backref='legends')


# TODO: check how the definition in base model from confederation can be realized
class Plr104PublicLawRestriction(Base):
    __table_args__ = {'schema': 'plr104'}
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
        sa.ForeignKey(Plr104ViewService.id),
        nullable=True
    )
    view_service = relationship(
        Plr104ViewService,
        backref='public_law_restrictions'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr104Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr104Office)


class Plr104Geometry(Base):
    __table_args__ = {'schema': 'plr104'}
    __tablename__ = 'geometry'
    id = sa.Column(sa.Integer, primary_key=True)
    legal_state = sa.Column(sa.String, nullable=False)
    published_from = sa.Column(sa.Date, nullable=False)
    geo_metadata = sa.Column(sa.String, nullable=True)  # TODO: Check translation
    geom = sa.Column(Geometry('POLYGON', srid=2056))
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr104PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction = relationship(
        Plr104PublicLawRestriction,
        backref='geometries'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr104Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr104Office)


class Plr104PublicLawRestrictionBase(Base):
    __tablename__ = 'public_law_restriction_base'
    __table_args__ = {'schema': 'plr104'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr104PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr104PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr104PublicLawRestriction,
        backref='basis',
        foreign_keys=[public_law_restriction_id]
    )
    base = relationship(
        Plr104PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr104PublicLawRestrictionRefinement(Base):
    __tablename__ = 'public_law_restriction_refinement'
    __table_args__ = {'schema': 'plr104'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr104PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr104PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr104PublicLawRestriction,
        backref='refinements',
        foreign_keys=[public_law_restriction_id]
    )
    refinement = relationship(
        Plr104PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr104PublicLawRestrictionDocument(Base):
    __tablename__ = 'public_law_restriction_document'
    __table_args__ = {'schema': 'plr104'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr104PublicLawRestriction.id),
        nullable=False
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr104DocumentBase.id),
        nullable=False
    )
    plr = relationship(
        Plr104PublicLawRestriction,
        backref='legal_provisions'
    )
    document = relationship(
        Plr104DocumentBase
    )
    article_numbers = sa.Column(sa.String, nullable=True)


# TODO: check translation
class Plr104DocumentReference(Base):
    __tablename__ = 'document_reference'
    __table_args__ = {'schema': 'plr104'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr104Document.id),
        nullable=False
    )
    reference_document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr104Document.id),
        nullable=False
    )
    document = relationship(
        Plr104Document,
        backref='referenced_documents',
        foreign_keys=[document_id]
    )
    referenced_document = relationship(
        Plr104Document,
        foreign_keys=[reference_document_id]
    )
    article_numbers = sa.Column(sa.String, nullable=True)


class Plr104DocumentReferenceDefinition(Base):
    __tablename__ = 'document_reference_definition'
    __table_args__ = {'schema': 'plr104'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr104Document.id),
        nullable=False
    )
    reference_definition_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr104ReferenceDefinition.id),
        nullable=False
    )


class Plr108Availability(Base):
    __table_args__ = {'schema': 'plr108'}
    __tablename__ = 'availability'
    fosnr = sa.Column(sa.Integer, primary_key=True)
    available = sa.Column(sa.Boolean, nullable=False, default=False)


class Plr108Office(Base):
    __table_args__ = {'schema': 'plr108'}
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


class Plr108ReferenceDefinition(Base):  # TODO: Check translation
    __table_args__ = {'schema': 'plr108'}
    __tablename__ = 'reference_definition'
    id = sa.Column(sa.Integer, primary_key=True)
    topic = sa.Column(sa.String, nullable=True)
    canton = sa.Column(sa.String(2), nullable=True)
    municipality = sa.Column(sa.Integer, nullable=True)
    office_id = sa.Column(sa.Integer, sa.ForeignKey(
        Plr108Office.id), nullable=False
    )
    responsible_office = relationship(Plr108Office)


class Plr108DocumentBase(Base):
    __table_args__ = {'schema': 'plr108'}
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


class Plr108Document(Plr108DocumentBase):
    __table_args__ = {'schema': 'plr108'}
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
        sa.ForeignKey(Plr108DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr108Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr108Office)


class Plr108Article(Plr108DocumentBase):
    __table_args__ = {'schema': 'plr108'}
    __tablename__ = 'article'
    __mapper_args__ = {
        'polymorphic_identity': 'article'
    }
    number = sa.Column(sa.String, nullable=False)
    text = sa.Column(sa.String, nullable=True)
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr108DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr108Document.id),
        nullable=False
    )
    document = relationship(
        Plr108Document,
        backref='articles',
        foreign_keys=[document_id]
    )


class Plr108LegalProvision(Plr108Document):
    __table_args__ = {'schema': 'plr108'}
    __tablename__ = 'legal_provision'
    __mapper_args__ = {
        'polymorphic_identity': 'legal_provision'
    }
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr108Document.id),
        primary_key=True,
        onupdate="cascade"
    )


class Plr108ViewService(Base):
    __table_args__ = {'schema': 'plr108'}
    __tablename__ = 'view_service'
    id = sa.Column(sa.Integer, primary_key=True)
    link_wms = sa.Column(sa.String, nullable=False)
    legend_web = sa.Column(sa.String, nullable=True)


class Plr108LegendEntry(Base):
    __table_args__ = {'schema': 'plr108'}
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
        sa.ForeignKey(Plr108ViewService.id),
        nullable=False
    )
    view_service = relationship(Plr108ViewService, backref='legends')


# TODO: check how the definition in base model from confederation can be realized
class Plr108PublicLawRestriction(Base):
    __table_args__ = {'schema': 'plr108'}
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
        sa.ForeignKey(Plr108ViewService.id),
        nullable=True
    )
    view_service = relationship(
        Plr108ViewService,
        backref='public_law_restrictions'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr108Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr108Office)


class Plr108Geometry(Base):
    __table_args__ = {'schema': 'plr108'}
    __tablename__ = 'geometry'
    id = sa.Column(sa.Integer, primary_key=True)
    legal_state = sa.Column(sa.String, nullable=False)
    published_from = sa.Column(sa.Date, nullable=False)
    geo_metadata = sa.Column(sa.String, nullable=True)  # TODO: Check translation
    geom = sa.Column(Geometry('POLYGON', srid=2056))
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr108PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction = relationship(
        Plr108PublicLawRestriction,
        backref='geometries'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr108Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr108Office)


class Plr108PublicLawRestrictionBase(Base):
    __tablename__ = 'public_law_restriction_base'
    __table_args__ = {'schema': 'plr108'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr108PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr108PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr108PublicLawRestriction,
        backref='basis',
        foreign_keys=[public_law_restriction_id]
    )
    base = relationship(
        Plr108PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr108PublicLawRestrictionRefinement(Base):
    __tablename__ = 'public_law_restriction_refinement'
    __table_args__ = {'schema': 'plr108'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr108PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr108PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr108PublicLawRestriction,
        backref='refinements',
        foreign_keys=[public_law_restriction_id]
    )
    refinement = relationship(
        Plr108PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr108PublicLawRestrictionDocument(Base):
    __tablename__ = 'public_law_restriction_document'
    __table_args__ = {'schema': 'plr108'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr108PublicLawRestriction.id),
        nullable=False
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr108DocumentBase.id),
        nullable=False
    )
    plr = relationship(
        Plr108PublicLawRestriction,
        backref='legal_provisions'
    )
    document = relationship(
        Plr108DocumentBase
    )
    article_numbers = sa.Column(sa.String, nullable=True)


# TODO: check translation
class Plr108DocumentReference(Base):
    __tablename__ = 'document_reference'
    __table_args__ = {'schema': 'plr108'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr108Document.id),
        nullable=False
    )
    reference_document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr108Document.id),
        nullable=False
    )
    document = relationship(
        Plr108Document,
        backref='referenced_documents',
        foreign_keys=[document_id]
    )
    referenced_document = relationship(
        Plr108Document,
        foreign_keys=[reference_document_id]
    )
    article_numbers = sa.Column(sa.String, nullable=True)


class Plr108DocumentReferenceDefinition(Base):
    __tablename__ = 'document_reference_definition'
    __table_args__ = {'schema': 'plr108'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr108Document.id),
        nullable=False
    )
    reference_definition_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr108ReferenceDefinition.id),
        nullable=False
    )


class Plr116Availability(Base):
    __table_args__ = {'schema': 'plr116'}
    __tablename__ = 'availability'
    fosnr = sa.Column(sa.Integer, primary_key=True)
    available = sa.Column(sa.Boolean, nullable=False, default=False)


class Plr116Office(Base):
    __table_args__ = {'schema': 'plr116'}
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


class Plr116ReferenceDefinition(Base):  # TODO: Check translation
    __table_args__ = {'schema': 'plr116'}
    __tablename__ = 'reference_definition'
    id = sa.Column(sa.Integer, primary_key=True)
    topic = sa.Column(sa.String, nullable=True)
    canton = sa.Column(sa.String(2), nullable=True)
    municipality = sa.Column(sa.Integer, nullable=True)
    office_id = sa.Column(sa.Integer, sa.ForeignKey(
        Plr116Office.id), nullable=False
    )
    responsible_office = relationship(Plr116Office)


class Plr116DocumentBase(Base):
    __table_args__ = {'schema': 'plr116'}
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


class Plr116Document(Plr116DocumentBase):
    __table_args__ = {'schema': 'plr116'}
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
        sa.ForeignKey(Plr116DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr116Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr116Office)


class Plr116Article(Plr116DocumentBase):
    __table_args__ = {'schema': 'plr116'}
    __tablename__ = 'article'
    __mapper_args__ = {
        'polymorphic_identity': 'article'
    }
    number = sa.Column(sa.String, nullable=False)
    text = sa.Column(sa.String, nullable=True)
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr116DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr116Document.id),
        nullable=False
    )
    document = relationship(
        Plr116Document,
        backref='articles',
        foreign_keys=[document_id]
    )


class Plr116LegalProvision(Plr116Document):
    __table_args__ = {'schema': 'plr116'}
    __tablename__ = 'legal_provision'
    __mapper_args__ = {
        'polymorphic_identity': 'legal_provision'
    }
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr116Document.id),
        primary_key=True,
        onupdate="cascade"
    )


class Plr116ViewService(Base):
    __table_args__ = {'schema': 'plr116'}
    __tablename__ = 'view_service'
    id = sa.Column(sa.Integer, primary_key=True)
    link_wms = sa.Column(sa.String, nullable=False)
    legend_web = sa.Column(sa.String, nullable=True)


class Plr116LegendEntry(Base):
    __table_args__ = {'schema': 'plr116'}
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
        sa.ForeignKey(Plr116ViewService.id),
        nullable=False
    )
    view_service = relationship(Plr116ViewService, backref='legends')


# TODO: check how the definition in base model from confederation can be realized
class Plr116PublicLawRestriction(Base):
    __table_args__ = {'schema': 'plr116'}
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
        sa.ForeignKey(Plr116ViewService.id),
        nullable=True
    )
    view_service = relationship(
        Plr116ViewService,
        backref='public_law_restrictions'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr116Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr116Office)


class Plr116Geometry(Base):
    __table_args__ = {'schema': 'plr116'}
    __tablename__ = 'geometry'
    id = sa.Column(sa.Integer, primary_key=True)
    legal_state = sa.Column(sa.String, nullable=False)
    published_from = sa.Column(sa.Date, nullable=False)
    geo_metadata = sa.Column(sa.String, nullable=True)  # TODO: Check translation
    geom = sa.Column(Geometry('POLYGON', srid=2056))
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr116PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction = relationship(
        Plr116PublicLawRestriction,
        backref='geometries'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr116Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr116Office)


class Plr116PublicLawRestrictionBase(Base):
    __tablename__ = 'public_law_restriction_base'
    __table_args__ = {'schema': 'plr116'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr116PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr116PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr116PublicLawRestriction,
        backref='basis',
        foreign_keys=[public_law_restriction_id]
    )
    base = relationship(
        Plr116PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr116PublicLawRestrictionRefinement(Base):
    __tablename__ = 'public_law_restriction_refinement'
    __table_args__ = {'schema': 'plr116'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr116PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr116PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr116PublicLawRestriction,
        backref='refinements',
        foreign_keys=[public_law_restriction_id]
    )
    refinement = relationship(
        Plr116PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr116PublicLawRestrictionDocument(Base):
    __tablename__ = 'public_law_restriction_document'
    __table_args__ = {'schema': 'plr116'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr116PublicLawRestriction.id),
        nullable=False
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr116DocumentBase.id),
        nullable=False
    )
    plr = relationship(
        Plr116PublicLawRestriction,
        backref='legal_provisions'
    )
    document = relationship(
        Plr116DocumentBase
    )
    article_numbers = sa.Column(sa.String, nullable=True)


# TODO: check translation
class Plr116DocumentReference(Base):
    __tablename__ = 'document_reference'
    __table_args__ = {'schema': 'plr116'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr116Document.id),
        nullable=False
    )
    reference_document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr116Document.id),
        nullable=False
    )
    document = relationship(
        Plr116Document,
        backref='referenced_documents',
        foreign_keys=[document_id]
    )
    referenced_document = relationship(
        Plr116Document,
        foreign_keys=[reference_document_id]
    )
    article_numbers = sa.Column(sa.String, nullable=True)


class Plr116DocumentReferenceDefinition(Base):
    __tablename__ = 'document_reference_definition'
    __table_args__ = {'schema': 'plr116'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr116Document.id),
        nullable=False
    )
    reference_definition_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr116ReferenceDefinition.id),
        nullable=False
    )


class Plr117Availability(Base):
    __table_args__ = {'schema': 'plr117'}
    __tablename__ = 'availability'
    fosnr = sa.Column(sa.Integer, primary_key=True)
    available = sa.Column(sa.Boolean, nullable=False, default=False)


class Plr117Office(Base):
    __table_args__ = {'schema': 'plr117'}
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


class Plr117ReferenceDefinition(Base):  # TODO: Check translation
    __table_args__ = {'schema': 'plr117'}
    __tablename__ = 'reference_definition'
    id = sa.Column(sa.Integer, primary_key=True)
    topic = sa.Column(sa.String, nullable=True)
    canton = sa.Column(sa.String(2), nullable=True)
    municipality = sa.Column(sa.Integer, nullable=True)
    office_id = sa.Column(sa.Integer, sa.ForeignKey(
        Plr117Office.id), nullable=False
    )
    responsible_office = relationship(Plr117Office)


class Plr117DocumentBase(Base):
    __table_args__ = {'schema': 'plr117'}
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


class Plr117Document(Plr117DocumentBase):
    __table_args__ = {'schema': 'plr117'}
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
        sa.ForeignKey(Plr117DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr117Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr117Office)


class Plr117Article(Plr117DocumentBase):
    __table_args__ = {'schema': 'plr117'}
    __tablename__ = 'article'
    __mapper_args__ = {
        'polymorphic_identity': 'article'
    }
    number = sa.Column(sa.String, nullable=False)
    text = sa.Column(sa.String, nullable=True)
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr117DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr117Document.id),
        nullable=False
    )
    document = relationship(
        Plr117Document,
        backref='articles',
        foreign_keys=[document_id]
    )


class Plr117LegalProvision(Plr117Document):
    __table_args__ = {'schema': 'plr117'}
    __tablename__ = 'legal_provision'
    __mapper_args__ = {
        'polymorphic_identity': 'legal_provision'
    }
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr117Document.id),
        primary_key=True,
        onupdate="cascade"
    )


class Plr117ViewService(Base):
    __table_args__ = {'schema': 'plr117'}
    __tablename__ = 'view_service'
    id = sa.Column(sa.Integer, primary_key=True)
    link_wms = sa.Column(sa.String, nullable=False)
    legend_web = sa.Column(sa.String, nullable=True)


class Plr117LegendEntry(Base):
    __table_args__ = {'schema': 'plr117'}
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
        sa.ForeignKey(Plr117ViewService.id),
        nullable=False
    )
    view_service = relationship(Plr117ViewService, backref='legends')


# TODO: check how the definition in base model from confederation can be realized
class Plr117PublicLawRestriction(Base):
    __table_args__ = {'schema': 'plr117'}
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
        sa.ForeignKey(Plr117ViewService.id),
        nullable=True
    )
    view_service = relationship(
        Plr117ViewService,
        backref='public_law_restrictions'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr117Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr117Office)


class Plr117Geometry(Base):
    __table_args__ = {'schema': 'plr117'}
    __tablename__ = 'geometry'
    id = sa.Column(sa.Integer, primary_key=True)
    legal_state = sa.Column(sa.String, nullable=False)
    published_from = sa.Column(sa.Date, nullable=False)
    geo_metadata = sa.Column(sa.String, nullable=True)  # TODO: Check translation
    geom = sa.Column(Geometry('POLYGON', srid=2056))
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr117PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction = relationship(
        Plr117PublicLawRestriction,
        backref='geometries'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr117Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr117Office)


class Plr117PublicLawRestrictionBase(Base):
    __tablename__ = 'public_law_restriction_base'
    __table_args__ = {'schema': 'plr117'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr117PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr117PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr117PublicLawRestriction,
        backref='basis',
        foreign_keys=[public_law_restriction_id]
    )
    base = relationship(
        Plr117PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr117PublicLawRestrictionRefinement(Base):
    __tablename__ = 'public_law_restriction_refinement'
    __table_args__ = {'schema': 'plr117'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr117PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr117PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr117PublicLawRestriction,
        backref='refinements',
        foreign_keys=[public_law_restriction_id]
    )
    refinement = relationship(
        Plr117PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr117PublicLawRestrictionDocument(Base):
    __tablename__ = 'public_law_restriction_document'
    __table_args__ = {'schema': 'plr117'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr117PublicLawRestriction.id),
        nullable=False
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr117DocumentBase.id),
        nullable=False
    )
    plr = relationship(
        Plr117PublicLawRestriction,
        backref='legal_provisions'
    )
    document = relationship(
        Plr117DocumentBase
    )
    article_numbers = sa.Column(sa.String, nullable=True)


# TODO: check translation
class Plr117DocumentReference(Base):
    __tablename__ = 'document_reference'
    __table_args__ = {'schema': 'plr117'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr117Document.id),
        nullable=False
    )
    reference_document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr117Document.id),
        nullable=False
    )
    document = relationship(
        Plr117Document,
        backref='referenced_documents',
        foreign_keys=[document_id]
    )
    referenced_document = relationship(
        Plr117Document,
        foreign_keys=[reference_document_id]
    )
    article_numbers = sa.Column(sa.String, nullable=True)


class Plr117DocumentReferenceDefinition(Base):
    __tablename__ = 'document_reference_definition'
    __table_args__ = {'schema': 'plr117'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr117Document.id),
        nullable=False
    )
    reference_definition_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr117ReferenceDefinition.id),
        nullable=False
    )


class Plr118Availability(Base):
    __table_args__ = {'schema': 'plr118'}
    __tablename__ = 'availability'
    fosnr = sa.Column(sa.Integer, primary_key=True)
    available = sa.Column(sa.Boolean, nullable=False, default=False)


class Plr118Office(Base):
    __table_args__ = {'schema': 'plr118'}
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


class Plr118ReferenceDefinition(Base):  # TODO: Check translation
    __table_args__ = {'schema': 'plr118'}
    __tablename__ = 'reference_definition'
    id = sa.Column(sa.Integer, primary_key=True)
    topic = sa.Column(sa.String, nullable=True)
    canton = sa.Column(sa.String(2), nullable=True)
    municipality = sa.Column(sa.Integer, nullable=True)
    office_id = sa.Column(sa.Integer, sa.ForeignKey(
        Plr118Office.id), nullable=False
    )
    responsible_office = relationship(Plr118Office)


class Plr118DocumentBase(Base):
    __table_args__ = {'schema': 'plr118'}
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


class Plr118Document(Plr118DocumentBase):
    __table_args__ = {'schema': 'plr118'}
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
        sa.ForeignKey(Plr118DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr118Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr118Office)


class Plr118Article(Plr118DocumentBase):
    __table_args__ = {'schema': 'plr118'}
    __tablename__ = 'article'
    __mapper_args__ = {
        'polymorphic_identity': 'article'
    }
    number = sa.Column(sa.String, nullable=False)
    text = sa.Column(sa.String, nullable=True)
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr118DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr118Document.id),
        nullable=False
    )
    document = relationship(
        Plr118Document,
        backref='articles',
        foreign_keys=[document_id]
    )


class Plr118LegalProvision(Plr118Document):
    __table_args__ = {'schema': 'plr118'}
    __tablename__ = 'legal_provision'
    __mapper_args__ = {
        'polymorphic_identity': 'legal_provision'
    }
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr118Document.id),
        primary_key=True,
        onupdate="cascade"
    )


class Plr118ViewService(Base):
    __table_args__ = {'schema': 'plr118'}
    __tablename__ = 'view_service'
    id = sa.Column(sa.Integer, primary_key=True)
    link_wms = sa.Column(sa.String, nullable=False)
    legend_web = sa.Column(sa.String, nullable=True)


class Plr118LegendEntry(Base):
    __table_args__ = {'schema': 'plr118'}
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
        sa.ForeignKey(Plr118ViewService.id),
        nullable=False
    )
    view_service = relationship(Plr118ViewService, backref='legends')


# TODO: check how the definition in base model from confederation can be realized
class Plr118PublicLawRestriction(Base):
    __table_args__ = {'schema': 'plr118'}
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
        sa.ForeignKey(Plr118ViewService.id),
        nullable=True
    )
    view_service = relationship(
        Plr118ViewService,
        backref='public_law_restrictions'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr118Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr118Office)


class Plr118Geometry(Base):
    __table_args__ = {'schema': 'plr118'}
    __tablename__ = 'geometry'
    id = sa.Column(sa.Integer, primary_key=True)
    legal_state = sa.Column(sa.String, nullable=False)
    published_from = sa.Column(sa.Date, nullable=False)
    geo_metadata = sa.Column(sa.String, nullable=True)  # TODO: Check translation
    geom = sa.Column(Geometry('POLYGON', srid=2056))
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr118PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction = relationship(
        Plr118PublicLawRestriction,
        backref='geometries'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr118Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr118Office)


class Plr118PublicLawRestrictionBase(Base):
    __tablename__ = 'public_law_restriction_base'
    __table_args__ = {'schema': 'plr118'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr118PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr118PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr118PublicLawRestriction,
        backref='basis',
        foreign_keys=[public_law_restriction_id]
    )
    base = relationship(
        Plr118PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr118PublicLawRestrictionRefinement(Base):
    __tablename__ = 'public_law_restriction_refinement'
    __table_args__ = {'schema': 'plr118'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr118PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr118PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr118PublicLawRestriction,
        backref='refinements',
        foreign_keys=[public_law_restriction_id]
    )
    refinement = relationship(
        Plr118PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr118PublicLawRestrictionDocument(Base):
    __tablename__ = 'public_law_restriction_document'
    __table_args__ = {'schema': 'plr118'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr118PublicLawRestriction.id),
        nullable=False
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr118DocumentBase.id),
        nullable=False
    )
    plr = relationship(
        Plr118PublicLawRestriction,
        backref='legal_provisions'
    )
    document = relationship(
        Plr118DocumentBase
    )
    article_numbers = sa.Column(sa.String, nullable=True)


# TODO: check translation
class Plr118DocumentReference(Base):
    __tablename__ = 'document_reference'
    __table_args__ = {'schema': 'plr118'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr118Document.id),
        nullable=False
    )
    reference_document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr118Document.id),
        nullable=False
    )
    document = relationship(
        Plr118Document,
        backref='referenced_documents',
        foreign_keys=[document_id]
    )
    referenced_document = relationship(
        Plr118Document,
        foreign_keys=[reference_document_id]
    )
    article_numbers = sa.Column(sa.String, nullable=True)


class Plr118DocumentReferenceDefinition(Base):
    __tablename__ = 'document_reference_definition'
    __table_args__ = {'schema': 'plr118'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr118Document.id),
        nullable=False
    )
    reference_definition_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr118ReferenceDefinition.id),
        nullable=False
    )


class Plr119Availability(Base):
    __table_args__ = {'schema': 'plr119'}
    __tablename__ = 'availability'
    fosnr = sa.Column(sa.Integer, primary_key=True)
    available = sa.Column(sa.Boolean, nullable=False, default=False)


class Plr119Office(Base):
    __table_args__ = {'schema': 'plr119'}
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


class Plr119ReferenceDefinition(Base):  # TODO: Check translation
    __table_args__ = {'schema': 'plr119'}
    __tablename__ = 'reference_definition'
    id = sa.Column(sa.Integer, primary_key=True)
    topic = sa.Column(sa.String, nullable=True)
    canton = sa.Column(sa.String(2), nullable=True)
    municipality = sa.Column(sa.Integer, nullable=True)
    office_id = sa.Column(sa.Integer, sa.ForeignKey(
        Plr119Office.id), nullable=False
    )
    responsible_office = relationship(Plr119Office)


class Plr119DocumentBase(Base):
    __table_args__ = {'schema': 'plr119'}
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


class Plr119Document(Plr119DocumentBase):
    __table_args__ = {'schema': 'plr119'}
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
        sa.ForeignKey(Plr119DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr119Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr119Office)


class Plr119Article(Plr119DocumentBase):
    __table_args__ = {'schema': 'plr119'}
    __tablename__ = 'article'
    __mapper_args__ = {
        'polymorphic_identity': 'article'
    }
    number = sa.Column(sa.String, nullable=False)
    text = sa.Column(sa.String, nullable=True)
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr119DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr119Document.id),
        nullable=False
    )
    document = relationship(
        Plr119Document,
        backref='articles',
        foreign_keys=[document_id]
    )


class Plr119LegalProvision(Plr119Document):
    __table_args__ = {'schema': 'plr119'}
    __tablename__ = 'legal_provision'
    __mapper_args__ = {
        'polymorphic_identity': 'legal_provision'
    }
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr119Document.id),
        primary_key=True,
        onupdate="cascade"
    )


class Plr119ViewService(Base):
    __table_args__ = {'schema': 'plr119'}
    __tablename__ = 'view_service'
    id = sa.Column(sa.Integer, primary_key=True)
    link_wms = sa.Column(sa.String, nullable=False)
    legend_web = sa.Column(sa.String, nullable=True)


class Plr119LegendEntry(Base):
    __table_args__ = {'schema': 'plr119'}
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
        sa.ForeignKey(Plr119ViewService.id),
        nullable=False
    )
    view_service = relationship(Plr119ViewService, backref='legends')


# TODO: check how the definition in base model from confederation can be realized
class Plr119PublicLawRestriction(Base):
    __table_args__ = {'schema': 'plr119'}
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
        sa.ForeignKey(Plr119ViewService.id),
        nullable=True
    )
    view_service = relationship(
        Plr119ViewService,
        backref='public_law_restrictions'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr119Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr119Office)


class Plr119Geometry(Base):
    __table_args__ = {'schema': 'plr119'}
    __tablename__ = 'geometry'
    id = sa.Column(sa.Integer, primary_key=True)
    legal_state = sa.Column(sa.String, nullable=False)
    published_from = sa.Column(sa.Date, nullable=False)
    geo_metadata = sa.Column(sa.String, nullable=True)  # TODO: Check translation
    geom = sa.Column(Geometry('POLYGON', srid=2056))
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr119PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction = relationship(
        Plr119PublicLawRestriction,
        backref='geometries'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr119Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr119Office)


class Plr119PublicLawRestrictionBase(Base):
    __tablename__ = 'public_law_restriction_base'
    __table_args__ = {'schema': 'plr119'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr119PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr119PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr119PublicLawRestriction,
        backref='basis',
        foreign_keys=[public_law_restriction_id]
    )
    base = relationship(
        Plr119PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr119PublicLawRestrictionRefinement(Base):
    __tablename__ = 'public_law_restriction_refinement'
    __table_args__ = {'schema': 'plr119'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr119PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr119PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr119PublicLawRestriction,
        backref='refinements',
        foreign_keys=[public_law_restriction_id]
    )
    refinement = relationship(
        Plr119PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr119PublicLawRestrictionDocument(Base):
    __tablename__ = 'public_law_restriction_document'
    __table_args__ = {'schema': 'plr119'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr119PublicLawRestriction.id),
        nullable=False
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr119DocumentBase.id),
        nullable=False
    )
    plr = relationship(
        Plr119PublicLawRestriction,
        backref='legal_provisions'
    )
    document = relationship(
        Plr119DocumentBase
    )
    article_numbers = sa.Column(sa.String, nullable=True)


# TODO: check translation
class Plr119DocumentReference(Base):
    __tablename__ = 'document_reference'
    __table_args__ = {'schema': 'plr119'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr119Document.id),
        nullable=False
    )
    reference_document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr119Document.id),
        nullable=False
    )
    document = relationship(
        Plr119Document,
        backref='referenced_documents',
        foreign_keys=[document_id]
    )
    referenced_document = relationship(
        Plr119Document,
        foreign_keys=[reference_document_id]
    )
    article_numbers = sa.Column(sa.String, nullable=True)


class Plr119DocumentReferenceDefinition(Base):
    __tablename__ = 'document_reference_definition'
    __table_args__ = {'schema': 'plr119'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr119Document.id),
        nullable=False
    )
    reference_definition_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr119ReferenceDefinition.id),
        nullable=False
    )


class Plr131Availability(Base):
    __table_args__ = {'schema': 'plr131'}
    __tablename__ = 'availability'
    fosnr = sa.Column(sa.Integer, primary_key=True)
    available = sa.Column(sa.Boolean, nullable=False, default=False)


class Plr131Office(Base):
    __table_args__ = {'schema': 'plr131'}
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


class Plr131ReferenceDefinition(Base):  # TODO: Check translation
    __table_args__ = {'schema': 'plr131'}
    __tablename__ = 'reference_definition'
    id = sa.Column(sa.Integer, primary_key=True)
    topic = sa.Column(sa.String, nullable=True)
    canton = sa.Column(sa.String(2), nullable=True)
    municipality = sa.Column(sa.Integer, nullable=True)
    office_id = sa.Column(sa.Integer, sa.ForeignKey(
        Plr131Office.id), nullable=False
    )
    responsible_office = relationship(Plr131Office)


class Plr131DocumentBase(Base):
    __table_args__ = {'schema': 'plr131'}
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


class Plr131Document(Plr131DocumentBase):
    __table_args__ = {'schema': 'plr131'}
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
        sa.ForeignKey(Plr131DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr131Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr131Office)


class Plr131Article(Plr131DocumentBase):
    __table_args__ = {'schema': 'plr131'}
    __tablename__ = 'article'
    __mapper_args__ = {
        'polymorphic_identity': 'article'
    }
    number = sa.Column(sa.String, nullable=False)
    text = sa.Column(sa.String, nullable=True)
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr131DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr131Document.id),
        nullable=False
    )
    document = relationship(
        Plr131Document,
        backref='articles',
        foreign_keys=[document_id]
    )


class Plr131LegalProvision(Plr131Document):
    __table_args__ = {'schema': 'plr131'}
    __tablename__ = 'legal_provision'
    __mapper_args__ = {
        'polymorphic_identity': 'legal_provision'
    }
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr131Document.id),
        primary_key=True,
        onupdate="cascade"
    )


class Plr131ViewService(Base):
    __table_args__ = {'schema': 'plr131'}
    __tablename__ = 'view_service'
    id = sa.Column(sa.Integer, primary_key=True)
    link_wms = sa.Column(sa.String, nullable=False)
    legend_web = sa.Column(sa.String, nullable=True)


class Plr131LegendEntry(Base):
    __table_args__ = {'schema': 'plr131'}
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
        sa.ForeignKey(Plr131ViewService.id),
        nullable=False
    )
    view_service = relationship(Plr131ViewService, backref='legends')


# TODO: check how the definition in base model from confederation can be realized
class Plr131PublicLawRestriction(Base):
    __table_args__ = {'schema': 'plr131'}
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
        sa.ForeignKey(Plr131ViewService.id),
        nullable=True
    )
    view_service = relationship(
        Plr131ViewService,
        backref='public_law_restrictions'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr131Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr131Office)


class Plr131Geometry(Base):
    __table_args__ = {'schema': 'plr131'}
    __tablename__ = 'geometry'
    id = sa.Column(sa.Integer, primary_key=True)
    legal_state = sa.Column(sa.String, nullable=False)
    published_from = sa.Column(sa.Date, nullable=False)
    geo_metadata = sa.Column(sa.String, nullable=True)  # TODO: Check translation
    geom = sa.Column(Geometry('POLYGON', srid=2056))
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr131PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction = relationship(
        Plr131PublicLawRestriction,
        backref='geometries'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr131Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr131Office)


class Plr131PublicLawRestrictionBase(Base):
    __tablename__ = 'public_law_restriction_base'
    __table_args__ = {'schema': 'plr131'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr131PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr131PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr131PublicLawRestriction,
        backref='basis',
        foreign_keys=[public_law_restriction_id]
    )
    base = relationship(
        Plr131PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr131PublicLawRestrictionRefinement(Base):
    __tablename__ = 'public_law_restriction_refinement'
    __table_args__ = {'schema': 'plr131'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr131PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr131PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr131PublicLawRestriction,
        backref='refinements',
        foreign_keys=[public_law_restriction_id]
    )
    refinement = relationship(
        Plr131PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr131PublicLawRestrictionDocument(Base):
    __tablename__ = 'public_law_restriction_document'
    __table_args__ = {'schema': 'plr131'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr131PublicLawRestriction.id),
        nullable=False
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr131DocumentBase.id),
        nullable=False
    )
    plr = relationship(
        Plr131PublicLawRestriction,
        backref='legal_provisions'
    )
    document = relationship(
        Plr131DocumentBase
    )
    article_numbers = sa.Column(sa.String, nullable=True)


# TODO: check translation
class Plr131DocumentReference(Base):
    __tablename__ = 'document_reference'
    __table_args__ = {'schema': 'plr131'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr131Document.id),
        nullable=False
    )
    reference_document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr131Document.id),
        nullable=False
    )
    document = relationship(
        Plr131Document,
        backref='referenced_documents',
        foreign_keys=[document_id]
    )
    referenced_document = relationship(
        Plr131Document,
        foreign_keys=[reference_document_id]
    )
    article_numbers = sa.Column(sa.String, nullable=True)


class Plr131DocumentReferenceDefinition(Base):
    __tablename__ = 'document_reference_definition'
    __table_args__ = {'schema': 'plr131'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr131Document.id),
        nullable=False
    )
    reference_definition_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr131ReferenceDefinition.id),
        nullable=False
    )


class Plr132Availability(Base):
    __table_args__ = {'schema': 'plr132'}
    __tablename__ = 'availability'
    fosnr = sa.Column(sa.Integer, primary_key=True)
    available = sa.Column(sa.Boolean, nullable=False, default=False)


class Plr132Office(Base):
    __table_args__ = {'schema': 'plr132'}
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


class Plr132ReferenceDefinition(Base):  # TODO: Check translation
    __table_args__ = {'schema': 'plr132'}
    __tablename__ = 'reference_definition'
    id = sa.Column(sa.Integer, primary_key=True)
    topic = sa.Column(sa.String, nullable=True)
    canton = sa.Column(sa.String(2), nullable=True)
    municipality = sa.Column(sa.Integer, nullable=True)
    office_id = sa.Column(sa.Integer, sa.ForeignKey(
        Plr132Office.id), nullable=False
    )
    responsible_office = relationship(Plr132Office)


class Plr132DocumentBase(Base):
    __table_args__ = {'schema': 'plr132'}
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


class Plr132Document(Plr132DocumentBase):
    __table_args__ = {'schema': 'plr132'}
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
        sa.ForeignKey(Plr132DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr132Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr132Office)


class Plr132Article(Plr132DocumentBase):
    __table_args__ = {'schema': 'plr132'}
    __tablename__ = 'article'
    __mapper_args__ = {
        'polymorphic_identity': 'article'
    }
    number = sa.Column(sa.String, nullable=False)
    text = sa.Column(sa.String, nullable=True)
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr132DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr132Document.id),
        nullable=False
    )
    document = relationship(
        Plr132Document,
        backref='articles',
        foreign_keys=[document_id]
    )


class Plr132LegalProvision(Plr132Document):
    __table_args__ = {'schema': 'plr132'}
    __tablename__ = 'legal_provision'
    __mapper_args__ = {
        'polymorphic_identity': 'legal_provision'
    }
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr132Document.id),
        primary_key=True,
        onupdate="cascade"
    )


class Plr132ViewService(Base):
    __table_args__ = {'schema': 'plr132'}
    __tablename__ = 'view_service'
    id = sa.Column(sa.Integer, primary_key=True)
    link_wms = sa.Column(sa.String, nullable=False)
    legend_web = sa.Column(sa.String, nullable=True)


class Plr132LegendEntry(Base):
    __table_args__ = {'schema': 'plr132'}
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
        sa.ForeignKey(Plr132ViewService.id),
        nullable=False
    )
    view_service = relationship(Plr132ViewService, backref='legends')


# TODO: check how the definition in base model from confederation can be realized
class Plr132PublicLawRestriction(Base):
    __table_args__ = {'schema': 'plr132'}
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
        sa.ForeignKey(Plr132ViewService.id),
        nullable=True
    )
    view_service = relationship(
        Plr132ViewService,
        backref='public_law_restrictions'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr132Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr132Office)


class Plr132Geometry(Base):
    __table_args__ = {'schema': 'plr132'}
    __tablename__ = 'geometry'
    id = sa.Column(sa.Integer, primary_key=True)
    legal_state = sa.Column(sa.String, nullable=False)
    published_from = sa.Column(sa.Date, nullable=False)
    geo_metadata = sa.Column(sa.String, nullable=True)  # TODO: Check translation
    geom = sa.Column(Geometry('POLYGON', srid=2056))
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr132PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction = relationship(
        Plr132PublicLawRestriction,
        backref='geometries'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr132Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr132Office)


class Plr132PublicLawRestrictionBase(Base):
    __tablename__ = 'public_law_restriction_base'
    __table_args__ = {'schema': 'plr132'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr132PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr132PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr132PublicLawRestriction,
        backref='basis',
        foreign_keys=[public_law_restriction_id]
    )
    base = relationship(
        Plr132PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr132PublicLawRestrictionRefinement(Base):
    __tablename__ = 'public_law_restriction_refinement'
    __table_args__ = {'schema': 'plr132'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr132PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr132PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr132PublicLawRestriction,
        backref='refinements',
        foreign_keys=[public_law_restriction_id]
    )
    refinement = relationship(
        Plr132PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr132PublicLawRestrictionDocument(Base):
    __tablename__ = 'public_law_restriction_document'
    __table_args__ = {'schema': 'plr132'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr132PublicLawRestriction.id),
        nullable=False
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr132DocumentBase.id),
        nullable=False
    )
    plr = relationship(
        Plr132PublicLawRestriction,
        backref='legal_provisions'
    )
    document = relationship(
        Plr132DocumentBase
    )
    article_numbers = sa.Column(sa.String, nullable=True)


# TODO: check translation
class Plr132DocumentReference(Base):
    __tablename__ = 'document_reference'
    __table_args__ = {'schema': 'plr132'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr132Document.id),
        nullable=False
    )
    reference_document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr132Document.id),
        nullable=False
    )
    document = relationship(
        Plr132Document,
        backref='referenced_documents',
        foreign_keys=[document_id]
    )
    referenced_document = relationship(
        Plr132Document,
        foreign_keys=[reference_document_id]
    )
    article_numbers = sa.Column(sa.String, nullable=True)


class Plr132DocumentReferenceDefinition(Base):
    __tablename__ = 'document_reference_definition'
    __table_args__ = {'schema': 'plr132'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr132Document.id),
        nullable=False
    )
    reference_definition_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr132ReferenceDefinition.id),
        nullable=False
    )


class Plr145Availability(Base):
    __table_args__ = {'schema': 'plr145'}
    __tablename__ = 'availability'
    fosnr = sa.Column(sa.Integer, primary_key=True)
    available = sa.Column(sa.Boolean, nullable=False, default=False)


class Plr145Office(Base):
    __table_args__ = {'schema': 'plr145'}
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


class Plr145ReferenceDefinition(Base):  # TODO: Check translation
    __table_args__ = {'schema': 'plr145'}
    __tablename__ = 'reference_definition'
    id = sa.Column(sa.Integer, primary_key=True)
    topic = sa.Column(sa.String, nullable=True)
    canton = sa.Column(sa.String(2), nullable=True)
    municipality = sa.Column(sa.Integer, nullable=True)
    office_id = sa.Column(sa.Integer, sa.ForeignKey(
        Plr145Office.id), nullable=False
    )
    responsible_office = relationship(Plr145Office)


class Plr145DocumentBase(Base):
    __table_args__ = {'schema': 'plr145'}
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


class Plr145Document(Plr145DocumentBase):
    __table_args__ = {'schema': 'plr145'}
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
        sa.ForeignKey(Plr145DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr145Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr145Office)


class Plr145Article(Plr145DocumentBase):
    __table_args__ = {'schema': 'plr145'}
    __tablename__ = 'article'
    __mapper_args__ = {
        'polymorphic_identity': 'article'
    }
    number = sa.Column(sa.String, nullable=False)
    text = sa.Column(sa.String, nullable=True)
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr145DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr145Document.id),
        nullable=False
    )
    document = relationship(
        Plr145Document,
        backref='articles',
        foreign_keys=[document_id]
    )


class Plr145LegalProvision(Plr145Document):
    __table_args__ = {'schema': 'plr145'}
    __tablename__ = 'legal_provision'
    __mapper_args__ = {
        'polymorphic_identity': 'legal_provision'
    }
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr145Document.id),
        primary_key=True,
        onupdate="cascade"
    )


class Plr145ViewService(Base):
    __table_args__ = {'schema': 'plr145'}
    __tablename__ = 'view_service'
    id = sa.Column(sa.Integer, primary_key=True)
    link_wms = sa.Column(sa.String, nullable=False)
    legend_web = sa.Column(sa.String, nullable=True)


class Plr145LegendEntry(Base):
    __table_args__ = {'schema': 'plr145'}
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
        sa.ForeignKey(Plr145ViewService.id),
        nullable=False
    )
    view_service = relationship(Plr145ViewService, backref='legends')


# TODO: check how the definition in base model from confederation can be realized
class Plr145PublicLawRestriction(Base):
    __table_args__ = {'schema': 'plr145'}
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
        sa.ForeignKey(Plr145ViewService.id),
        nullable=True
    )
    view_service = relationship(
        Plr145ViewService,
        backref='public_law_restrictions'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr145Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr145Office)


class Plr145Geometry(Base):
    __table_args__ = {'schema': 'plr145'}
    __tablename__ = 'geometry'
    id = sa.Column(sa.Integer, primary_key=True)
    legal_state = sa.Column(sa.String, nullable=False)
    published_from = sa.Column(sa.Date, nullable=False)
    geo_metadata = sa.Column(sa.String, nullable=True)  # TODO: Check translation
    geom = sa.Column(Geometry('POLYGON', srid=2056))
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr145PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction = relationship(
        Plr145PublicLawRestriction,
        backref='geometries'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr145Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr145Office)


class Plr145PublicLawRestrictionBase(Base):
    __tablename__ = 'public_law_restriction_base'
    __table_args__ = {'schema': 'plr145'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr145PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr145PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr145PublicLawRestriction,
        backref='basis',
        foreign_keys=[public_law_restriction_id]
    )
    base = relationship(
        Plr145PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr145PublicLawRestrictionRefinement(Base):
    __tablename__ = 'public_law_restriction_refinement'
    __table_args__ = {'schema': 'plr145'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr145PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr145PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr145PublicLawRestriction,
        backref='refinements',
        foreign_keys=[public_law_restriction_id]
    )
    refinement = relationship(
        Plr145PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr145PublicLawRestrictionDocument(Base):
    __tablename__ = 'public_law_restriction_document'
    __table_args__ = {'schema': 'plr145'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr145PublicLawRestriction.id),
        nullable=False
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr145DocumentBase.id),
        nullable=False
    )
    plr = relationship(
        Plr145PublicLawRestriction,
        backref='legal_provisions'
    )
    document = relationship(
        Plr145DocumentBase
    )
    article_numbers = sa.Column(sa.String, nullable=True)


# TODO: check translation
class Plr145DocumentReference(Base):
    __tablename__ = 'document_reference'
    __table_args__ = {'schema': 'plr145'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr145Document.id),
        nullable=False
    )
    reference_document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr145Document.id),
        nullable=False
    )
    document = relationship(
        Plr145Document,
        backref='referenced_documents',
        foreign_keys=[document_id]
    )
    referenced_document = relationship(
        Plr145Document,
        foreign_keys=[reference_document_id]
    )
    article_numbers = sa.Column(sa.String, nullable=True)


class Plr145DocumentReferenceDefinition(Base):
    __tablename__ = 'document_reference_definition'
    __table_args__ = {'schema': 'plr145'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr145Document.id),
        nullable=False
    )
    reference_definition_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr145ReferenceDefinition.id),
        nullable=False
    )


class Plr157Availability(Base):
    __table_args__ = {'schema': 'plr157'}
    __tablename__ = 'availability'
    fosnr = sa.Column(sa.Integer, primary_key=True)
    available = sa.Column(sa.Boolean, nullable=False, default=False)


class Plr157Office(Base):
    __table_args__ = {'schema': 'plr157'}
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


class Plr157ReferenceDefinition(Base):  # TODO: Check translation
    __table_args__ = {'schema': 'plr157'}
    __tablename__ = 'reference_definition'
    id = sa.Column(sa.Integer, primary_key=True)
    topic = sa.Column(sa.String, nullable=True)
    canton = sa.Column(sa.String(2), nullable=True)
    municipality = sa.Column(sa.Integer, nullable=True)
    office_id = sa.Column(sa.Integer, sa.ForeignKey(
        Plr157Office.id), nullable=False
    )
    responsible_office = relationship(Plr157Office)


class Plr157DocumentBase(Base):
    __table_args__ = {'schema': 'plr157'}
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


class Plr157Document(Plr157DocumentBase):
    __table_args__ = {'schema': 'plr157'}
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
        sa.ForeignKey(Plr157DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr157Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr157Office)


class Plr157Article(Plr157DocumentBase):
    __table_args__ = {'schema': 'plr157'}
    __tablename__ = 'article'
    __mapper_args__ = {
        'polymorphic_identity': 'article'
    }
    number = sa.Column(sa.String, nullable=False)
    text = sa.Column(sa.String, nullable=True)
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr157DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr157Document.id),
        nullable=False
    )
    document = relationship(
        Plr157Document,
        backref='articles',
        foreign_keys=[document_id]
    )


class Plr157LegalProvision(Plr157Document):
    __table_args__ = {'schema': 'plr157'}
    __tablename__ = 'legal_provision'
    __mapper_args__ = {
        'polymorphic_identity': 'legal_provision'
    }
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr157Document.id),
        primary_key=True,
        onupdate="cascade"
    )


class Plr157ViewService(Base):
    __table_args__ = {'schema': 'plr157'}
    __tablename__ = 'view_service'
    id = sa.Column(sa.Integer, primary_key=True)
    link_wms = sa.Column(sa.String, nullable=False)
    legend_web = sa.Column(sa.String, nullable=True)


class Plr157LegendEntry(Base):
    __table_args__ = {'schema': 'plr157'}
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
        sa.ForeignKey(Plr157ViewService.id),
        nullable=False
    )
    view_service = relationship(Plr157ViewService, backref='legends')


# TODO: check how the definition in base model from confederation can be realized
class Plr157PublicLawRestriction(Base):
    __table_args__ = {'schema': 'plr157'}
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
        sa.ForeignKey(Plr157ViewService.id),
        nullable=True
    )
    view_service = relationship(
        Plr157ViewService,
        backref='public_law_restrictions'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr157Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr157Office)


class Plr157Geometry(Base):
    __table_args__ = {'schema': 'plr157'}
    __tablename__ = 'geometry'
    id = sa.Column(sa.Integer, primary_key=True)
    legal_state = sa.Column(sa.String, nullable=False)
    published_from = sa.Column(sa.Date, nullable=False)
    geo_metadata = sa.Column(sa.String, nullable=True)  # TODO: Check translation
    geom = sa.Column(Geometry('POLYGON', srid=2056))
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr157PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction = relationship(
        Plr157PublicLawRestriction,
        backref='geometries'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr157Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr157Office)


class Plr157PublicLawRestrictionBase(Base):
    __tablename__ = 'public_law_restriction_base'
    __table_args__ = {'schema': 'plr157'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr157PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr157PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr157PublicLawRestriction,
        backref='basis',
        foreign_keys=[public_law_restriction_id]
    )
    base = relationship(
        Plr157PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr157PublicLawRestrictionRefinement(Base):
    __tablename__ = 'public_law_restriction_refinement'
    __table_args__ = {'schema': 'plr157'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr157PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr157PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr157PublicLawRestriction,
        backref='refinements',
        foreign_keys=[public_law_restriction_id]
    )
    refinement = relationship(
        Plr157PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr157PublicLawRestrictionDocument(Base):
    __tablename__ = 'public_law_restriction_document'
    __table_args__ = {'schema': 'plr157'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr157PublicLawRestriction.id),
        nullable=False
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr157DocumentBase.id),
        nullable=False
    )
    plr = relationship(
        Plr157PublicLawRestriction,
        backref='legal_provisions'
    )
    document = relationship(
        Plr157DocumentBase
    )
    article_numbers = sa.Column(sa.String, nullable=True)


# TODO: check translation
class Plr157DocumentReference(Base):
    __tablename__ = 'document_reference'
    __table_args__ = {'schema': 'plr157'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr157Document.id),
        nullable=False
    )
    reference_document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr157Document.id),
        nullable=False
    )
    document = relationship(
        Plr157Document,
        backref='referenced_documents',
        foreign_keys=[document_id]
    )
    referenced_document = relationship(
        Plr157Document,
        foreign_keys=[reference_document_id]
    )
    article_numbers = sa.Column(sa.String, nullable=True)


class Plr157DocumentReferenceDefinition(Base):
    __tablename__ = 'document_reference_definition'
    __table_args__ = {'schema': 'plr157'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr157Document.id),
        nullable=False
    )
    reference_definition_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr157ReferenceDefinition.id),
        nullable=False
    )


class Plr159Availability(Base):
    __table_args__ = {'schema': 'plr159'}
    __tablename__ = 'availability'
    fosnr = sa.Column(sa.Integer, primary_key=True)
    available = sa.Column(sa.Boolean, nullable=False, default=False)


class Plr159Office(Base):
    __table_args__ = {'schema': 'plr159'}
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


class Plr159ReferenceDefinition(Base):  # TODO: Check translation
    __table_args__ = {'schema': 'plr159'}
    __tablename__ = 'reference_definition'
    id = sa.Column(sa.Integer, primary_key=True)
    topic = sa.Column(sa.String, nullable=True)
    canton = sa.Column(sa.String(2), nullable=True)
    municipality = sa.Column(sa.Integer, nullable=True)
    office_id = sa.Column(sa.Integer, sa.ForeignKey(
        Plr159Office.id), nullable=False
    )
    responsible_office = relationship(Plr159Office)


class Plr159DocumentBase(Base):
    __table_args__ = {'schema': 'plr159'}
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


class Plr159Document(Plr159DocumentBase):
    __table_args__ = {'schema': 'plr159'}
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
        sa.ForeignKey(Plr159DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr159Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr159Office)


class Plr159Article(Plr159DocumentBase):
    __table_args__ = {'schema': 'plr159'}
    __tablename__ = 'article'
    __mapper_args__ = {
        'polymorphic_identity': 'article'
    }
    number = sa.Column(sa.String, nullable=False)
    text = sa.Column(sa.String, nullable=True)
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr159DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr159Document.id),
        nullable=False
    )
    document = relationship(
        Plr159Document,
        backref='articles',
        foreign_keys=[document_id]
    )


class Plr159LegalProvision(Plr159Document):
    __table_args__ = {'schema': 'plr159'}
    __tablename__ = 'legal_provision'
    __mapper_args__ = {
        'polymorphic_identity': 'legal_provision'
    }
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr159Document.id),
        primary_key=True,
        onupdate="cascade"
    )


class Plr159ViewService(Base):
    __table_args__ = {'schema': 'plr159'}
    __tablename__ = 'view_service'
    id = sa.Column(sa.Integer, primary_key=True)
    link_wms = sa.Column(sa.String, nullable=False)
    legend_web = sa.Column(sa.String, nullable=True)


class Plr159LegendEntry(Base):
    __table_args__ = {'schema': 'plr159'}
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
        sa.ForeignKey(Plr159ViewService.id),
        nullable=False
    )
    view_service = relationship(Plr159ViewService, backref='legends')


# TODO: check how the definition in base model from confederation can be realized
class Plr159PublicLawRestriction(Base):
    __table_args__ = {'schema': 'plr159'}
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
        sa.ForeignKey(Plr159ViewService.id),
        nullable=True
    )
    view_service = relationship(
        Plr159ViewService,
        backref='public_law_restrictions'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr159Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr159Office)


class Plr159Geometry(Base):
    __table_args__ = {'schema': 'plr159'}
    __tablename__ = 'geometry'
    id = sa.Column(sa.Integer, primary_key=True)
    legal_state = sa.Column(sa.String, nullable=False)
    published_from = sa.Column(sa.Date, nullable=False)
    geo_metadata = sa.Column(sa.String, nullable=True)  # TODO: Check translation
    geom = sa.Column(Geometry('POLYGON', srid=2056))
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr159PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction = relationship(
        Plr159PublicLawRestriction,
        backref='geometries'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr159Office.id),
        nullable=False
    )
    responsible_office = relationship(Plr159Office)


class Plr159PublicLawRestrictionBase(Base):
    __tablename__ = 'public_law_restriction_base'
    __table_args__ = {'schema': 'plr159'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr159PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr159PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr159PublicLawRestriction,
        backref='basis',
        foreign_keys=[public_law_restriction_id]
    )
    base = relationship(
        Plr159PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr159PublicLawRestrictionRefinement(Base):
    __tablename__ = 'public_law_restriction_refinement'
    __table_args__ = {'schema': 'plr159'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr159PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr159PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        Plr159PublicLawRestriction,
        backref='refinements',
        foreign_keys=[public_law_restriction_id]
    )
    refinement = relationship(
        Plr159PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class Plr159PublicLawRestrictionDocument(Base):
    __tablename__ = 'public_law_restriction_document'
    __table_args__ = {'schema': 'plr159'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr159PublicLawRestriction.id),
        nullable=False
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr159DocumentBase.id),
        nullable=False
    )
    plr = relationship(
        Plr159PublicLawRestriction,
        backref='legal_provisions'
    )
    document = relationship(
        Plr159DocumentBase
    )
    article_numbers = sa.Column(sa.String, nullable=True)


# TODO: check translation
class Plr159DocumentReference(Base):
    __tablename__ = 'document_reference'
    __table_args__ = {'schema': 'plr159'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr159Document.id),
        nullable=False
    )
    reference_document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr159Document.id),
        nullable=False
    )
    document = relationship(
        Plr159Document,
        backref='referenced_documents',
        foreign_keys=[document_id]
    )
    referenced_document = relationship(
        Plr159Document,
        foreign_keys=[reference_document_id]
    )
    article_numbers = sa.Column(sa.String, nullable=True)


class Plr159DocumentReferenceDefinition(Base):
    __tablename__ = 'document_reference_definition'
    __table_args__ = {'schema': 'plr159'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr159Document.id),
        nullable=False
    )
    reference_definition_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr159ReferenceDefinition.id),
        nullable=False
    )
