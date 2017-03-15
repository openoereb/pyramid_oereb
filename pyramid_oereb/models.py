
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


class Plr108Authority(Base):
    __table_args__ = {'schema': 'plr108'}
    __tablename__ = 'authority'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    authority_web = sa.Column(sa.String, nullable=True)
    uid = sa.Column(sa.String(12), nullable=True)


class Plr108ReferenceDefinition(Base):  # TODO: Check translation
    __table_args__ = {'schema': 'plr108'}
    __tablename__ = 'reference_definition'
    id = sa.Column(sa.Integer, primary_key=True)
    topic = sa.Column(sa.String, nullable=True)
    canton = sa.Column(sa.String(2), nullable=True)
    municipality = sa.Column(sa.Integer, nullable=True)
    authority_id = sa.Column(sa.Integer, sa.ForeignKey(
        Plr108Authority.id), nullable=True
    )
    authority = relationship(Plr108Authority, backref='reference_definitions')


class Plr108DocumentBase(Base):
    __table_args__ = {'schema': 'plr108'}
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


class Plr108Document(Plr108DocumentBase):
    __table_args__ = {'schema': 'plr108'}
    __tablename__ = 'document'
    title = sa.Column(sa.String, nullable=False)
    official_title = sa.Column(sa.String, nullable=True)
    abbreviation = sa.Column(sa.String, nullable=True)
    official_number = sa.Column(sa.String, nullable=True)
    canton = sa.Column(sa.String(2), nullable=True)
    municipality = sa.Column(sa.Integer, nullable=True)
    document = sa.Column(sa.Binary, nullable=True)
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr108DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    type = sa.Column(sa.Unicode, nullable=True, server_default="document")
    __mapper_args__ = {
        'polymorphic_identity': 'document'
    }
    authority_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr108Authority.id),
        nullable=True
    )
    authority = relationship(Plr108Authority, backref='documents')


class Plr108Article(Plr108DocumentBase):
    __table_args__ = {'schema': 'plr108'}
    __tablename__ = 'article'
    number = sa.Column(sa.String, nullable=False)
    text = sa.Column(sa.String, nullable=True)
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr108DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    type = sa.Column(sa.Unicode, nullable=True, server_default="article")
    __mapper_args__ = {
        'polymorphic_identity': 'article'
    }
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr108Document.id),
        nullable=False
    )
    document = relationship(Plr108Document, backref='articles')


class Plr108LegalProvision(Plr108Document):
    __table_args__ = {'schema': 'plr108'}
    __tablename__ = 'legal_provision'
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr108Document.id),
        primary_key=True,
        onupdate="cascade"
    )
    type = sa.Column(sa.Unicode, nullable=True, server_default="legal_provision")
    __mapper_args__ = {
        'polymorphic_identity': 'legal_provision'
    }


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
    symbol = sa.Column(sa.Binary, nullable=False)
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
    authority_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr108Authority.id),
        nullable=True
    )
    authority = relationship(Plr108Authority, backref='geometries')


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
    authority_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr108Authority.id),
        nullable=True
    )
    authority = relationship(
        Plr108Authority,
        backref='public_law_restrictions'
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


# TODO: check translation
class Plr108DocumentHint(Base):
    __tablename__ = 'document_hint'
    __table_args__ = {'schema': 'plr108'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr108Document.id),
        nullable=False
    )
    hint_document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr108Document.id),
        nullable=False
    )


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


class Plr97Authority(Base):
    __table_args__ = {'schema': 'plr97'}
    __tablename__ = 'authority'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    authority_web = sa.Column(sa.String, nullable=True)
    uid = sa.Column(sa.String(12), nullable=True)


class Plr97ReferenceDefinition(Base):  # TODO: Check translation
    __table_args__ = {'schema': 'plr97'}
    __tablename__ = 'reference_definition'
    id = sa.Column(sa.Integer, primary_key=True)
    topic = sa.Column(sa.String, nullable=True)
    canton = sa.Column(sa.String(2), nullable=True)
    municipality = sa.Column(sa.Integer, nullable=True)
    authority_id = sa.Column(sa.Integer, sa.ForeignKey(
        Plr97Authority.id), nullable=True
    )
    authority = relationship(Plr97Authority, backref='reference_definitions')


class Plr97DocumentBase(Base):
    __table_args__ = {'schema': 'plr97'}
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


class Plr97Document(Plr97DocumentBase):
    __table_args__ = {'schema': 'plr97'}
    __tablename__ = 'document'
    title = sa.Column(sa.String, nullable=False)
    official_title = sa.Column(sa.String, nullable=True)
    abbreviation = sa.Column(sa.String, nullable=True)
    official_number = sa.Column(sa.String, nullable=True)
    canton = sa.Column(sa.String(2), nullable=True)
    municipality = sa.Column(sa.Integer, nullable=True)
    document = sa.Column(sa.Binary, nullable=True)
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr97DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    type = sa.Column(sa.Unicode, nullable=True, server_default="document")
    __mapper_args__ = {
        'polymorphic_identity': 'document'
    }
    authority_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr97Authority.id),
        nullable=True
    )
    authority = relationship(Plr97Authority, backref='documents')


class Plr97Article(Plr97DocumentBase):
    __table_args__ = {'schema': 'plr97'}
    __tablename__ = 'article'
    number = sa.Column(sa.String, nullable=False)
    text = sa.Column(sa.String, nullable=True)
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr97DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    type = sa.Column(sa.Unicode, nullable=True, server_default="article")
    __mapper_args__ = {
        'polymorphic_identity': 'article'
    }
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr97Document.id),
        nullable=False
    )
    document = relationship(Plr97Document, backref='articles')


class Plr97LegalProvision(Plr97Document):
    __table_args__ = {'schema': 'plr97'}
    __tablename__ = 'legal_provision'
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr97Document.id),
        primary_key=True,
        onupdate="cascade"
    )
    type = sa.Column(sa.Unicode, nullable=True, server_default="legal_provision")
    __mapper_args__ = {
        'polymorphic_identity': 'legal_provision'
    }


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
    symbol = sa.Column(sa.Binary, nullable=False)
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
    authority_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr97Authority.id),
        nullable=True
    )
    authority = relationship(Plr97Authority, backref='geometries')


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
    authority_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr97Authority.id),
        nullable=True
    )
    authority = relationship(
        Plr97Authority,
        backref='public_law_restrictions'
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


# TODO: check translation
class Plr97DocumentHint(Base):
    __tablename__ = 'document_hint'
    __table_args__ = {'schema': 'plr97'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr97Document.id),
        nullable=False
    )
    hint_document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr97Document.id),
        nullable=False
    )


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


class Plr96Authority(Base):
    __table_args__ = {'schema': 'plr96'}
    __tablename__ = 'authority'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    authority_web = sa.Column(sa.String, nullable=True)
    uid = sa.Column(sa.String(12), nullable=True)


class Plr96ReferenceDefinition(Base):  # TODO: Check translation
    __table_args__ = {'schema': 'plr96'}
    __tablename__ = 'reference_definition'
    id = sa.Column(sa.Integer, primary_key=True)
    topic = sa.Column(sa.String, nullable=True)
    canton = sa.Column(sa.String(2), nullable=True)
    municipality = sa.Column(sa.Integer, nullable=True)
    authority_id = sa.Column(sa.Integer, sa.ForeignKey(
        Plr96Authority.id), nullable=True
    )
    authority = relationship(Plr96Authority, backref='reference_definitions')


class Plr96DocumentBase(Base):
    __table_args__ = {'schema': 'plr96'}
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


class Plr96Document(Plr96DocumentBase):
    __table_args__ = {'schema': 'plr96'}
    __tablename__ = 'document'
    title = sa.Column(sa.String, nullable=False)
    official_title = sa.Column(sa.String, nullable=True)
    abbreviation = sa.Column(sa.String, nullable=True)
    official_number = sa.Column(sa.String, nullable=True)
    canton = sa.Column(sa.String(2), nullable=True)
    municipality = sa.Column(sa.Integer, nullable=True)
    document = sa.Column(sa.Binary, nullable=True)
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr96DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    type = sa.Column(sa.Unicode, nullable=True, server_default="document")
    __mapper_args__ = {
        'polymorphic_identity': 'document'
    }
    authority_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr96Authority.id),
        nullable=True
    )
    authority = relationship(Plr96Authority, backref='documents')


class Plr96Article(Plr96DocumentBase):
    __table_args__ = {'schema': 'plr96'}
    __tablename__ = 'article'
    number = sa.Column(sa.String, nullable=False)
    text = sa.Column(sa.String, nullable=True)
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr96DocumentBase.id),
        primary_key=True,
        onupdate="cascade"
    )
    type = sa.Column(sa.Unicode, nullable=True, server_default="article")
    __mapper_args__ = {
        'polymorphic_identity': 'article'
    }
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr96Document.id),
        nullable=False
    )
    document = relationship(Plr96Document, backref='articles')


class Plr96LegalProvision(Plr96Document):
    __table_args__ = {'schema': 'plr96'}
    __tablename__ = 'legal_provision'
    id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr96Document.id),
        primary_key=True,
        onupdate="cascade"
    )
    type = sa.Column(sa.Unicode, nullable=True, server_default="legal_provision")
    __mapper_args__ = {
        'polymorphic_identity': 'legal_provision'
    }


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
    symbol = sa.Column(sa.Binary, nullable=False)
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
    authority_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr96Authority.id),
        nullable=True
    )
    authority = relationship(Plr96Authority, backref='geometries')


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
    authority_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr96Authority.id),
        nullable=True
    )
    authority = relationship(
        Plr96Authority,
        backref='public_law_restrictions'
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


# TODO: check translation
class Plr96DocumentHint(Base):
    __tablename__ = 'document_hint'
    __table_args__ = {'schema': 'plr96'}
    id = sa.Column(sa.Integer, primary_key=True)
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr96Document.id),
        nullable=False
    )
    hint_document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Plr96Document.id),
        nullable=False
    )


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
