"""
This is a full representation of the data model defined by the federal definition.

**It is representing the topic: Contaminated Public Transport Sites**

You can use it to
produce a own new topic for the oereb eco system in the specifications shape. To be able to adapt this
models to your own infrastructure you must implement the same attribute names! In fact that inheritance
is not easily made you need to make your own classes and adapt them to your database.
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
    a public law restriction is available or not. You need to fill it with the data you provided in the
    app schemas municipality table (fosnr).

    :var fosnr: The identifier of the municipality in your system (id_bfs = fosnr)
    :vartype fosnr: int
    :var available: The switch field to configure if this plr is available for the municipality or not.
        This field has direct influence on the applications behaviour. See documentation for more info.
    :vartype available: bool
    """
    __table_args__ = {'schema': 'contaminated_public_transport_sites'}
    __tablename__ = 'availability'
    fosnr = sa.Column(sa.Integer, primary_key=True)
    available = sa.Column(sa.Boolean, nullable=False, default=False)


class Office(Base):
    """
    The bucket to fill in all the offices you need to reference from public law restriction, document,
    geometry.

    :var id: The identifier. This is used in the database only and must not be set manually. If you
        don't like it - don't care about.
    :vartype id: int
    :var name: The name of the office.
    :vartype name: str
    :var office_at_web: A web accessible url to a presentation of this office.
    :vartype office_at_web: str
    :var uid: The uid of this office from https://www.uid.admin.ch
    :vartype uid: str
    :var line1: The first address line for this office.
    :vartype line1: str
    :var line2: The second address line for this office.
    :vartype line2: str
    :var street: The streets name of the offices address.
    :vartype street: str
    :var number: The number on street.
    :vartype number: str
    :var postal_code: The ZIP-code.
    :vartype postal_code: int
    :var city: The name of the city.
    :vartype city: str
    """
    __table_args__ = {'schema': 'contaminated_public_transport_sites'}
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
    to the whole canton or a  whole municipality. It is used to have a place to store general documents
    which are related to an extract but not directly on a special public law restriction situation.

    :var id: The identifier. This is used in the database only and must not be set manually. If you
        don't like it - don't care about.
    :vartype id: int
    :var topic: The topic which this definition might be related to.
    :vartype topic: str
    :var canton: The canton this definition is related to.
    :vartype canton: str
    :var municipality: The municipality this definition is related to.
    :vartype municipality: int
    :var office_id: The foreign key constraint which the definition is related to.
    :vartype office_id: int
    :var office: The dedicated relation to the office instance from database.
    :vartype responsible_office: pyramid_oereb.standard.models.contaminated_public_transport_sites.Office
    """
    __table_args__ = {'schema': 'contaminated_public_transport_sites'}
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

    :var id: The identifier. This is used in the database only and must not be set manually. If you
        don't like it - don't care about.
    :vartype id: int
    :var text_web: A link which leads to the documents content in the web.
    :vartype text_web: str
    :var legal_state: The status switch if the document is legally approved or not.
    :vartype legal_state: str
    :var published_from: The date when the document should be available for publishing on extracts. This
        directly affects the behaviour of extract generation.
    :vartype published_from: datetime.date
    :var type: This is a sqlalchemy related attribute to provide database table inheritance.
    :vartype type: unicode
    """
    __table_args__ = {'schema': 'contaminated_public_transport_sites'}
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

    :var id: The identifier. This is used in the database only and must not be set manually. If you
        don't like it - don't care about.
    :vartype id: int
    :var title: The title or if existing the short title ot his document.
    :vartype title: str
    :var office_title: The official title of this document.
    :vartype office_title: str
    :var abbrevation: The shortened version of the documents title.
    :vartype abbrevation: str
    :var official_number: The official number which uniquely identifies this document.
    :vartype official_number: str
    :var canton: The short version of the canton which this document is about. If this is None this is
        assumed to be a federal document.
    :vartype canton: str
    :var municipality: The fosnr (=id bfs) of the municipality. If this is None it is assumed the document is
        related to the whole canton or even the confederation.
    :vartype municipality: int
    :var file: The document itself as a binary representation (PDF). It is string but BaseCode64 encoded.
    :vartype file: str
    :var office_id: The foreign key to the office which is in charge for this document.
    :vartype office_id: int
    :var responsible_office: The dedicated relation to the office instance from database.
    :vartype responsible_office: pyramid_oereb.standard.models.contaminated_public_transport_sites.Office
    """
    __table_args__ = {'schema': 'contaminated_public_transport_sites'}
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
    file = sa.Column(sa.String, nullable=True)
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

    :var id: The identifier. This is used in the database only and must not be set manually. If you
        don't like it - don't care about.
    :vartype id: int
    :var number: The number which identifies this article in its parent document.
    :vartype number: str
    :var text: A simple string to describe the article or give some related info.
    :vartype text: str
    :var document_id: The foreign key to the document this article is taken from.
    :vartype document_id: int
    :var document: The dedicated relation to the document instance from database.
    :vartype document_id: pyramid_oereb.standard.models.contaminated_public_transport_sites.Document
    """
    __table_args__ = {'schema': 'contaminated_public_transport_sites'}
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

    :var id: The identifier. This is used in the database only and must not be set manually. If you
        don't like it - don't care about.
    :vartype id: int
    """
    __table_args__ = {'schema': 'contaminated_public_transport_sites'}
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
    A view service aka WM(T)S which can deliver a cartographic representation via web.

    :var id: The identifier. This is used in the database only and must not be set manually. If you
        don't like it - don't care about.
    :vartype id: int
    :var link_wms: The actual url which leads to the desired cartographic representation.
    :vartype link_wms: str
    :var legend_web: A link leading to a wms describing document (png).
    :vartype legend_web: str
    """
    __table_args__ = {'schema': 'contaminated_public_transport_sites'}
    __tablename__ = 'view_service'
    id = sa.Column(sa.Integer, primary_key=True)
    link_wms = sa.Column(sa.String, nullable=False)
    legend_web = sa.Column(sa.String, nullable=True)


class LegendEntry(Base):
    """
    A class based legend system which is directly related to
    :ref:`pyramid_oereb.standard.models.contaminated_public_transport_sites.ViewService`.

    :var id: The identifier. This is used in the database only and must not be set manually. If you
        don't like it - don't care about.
    :vartype id: int
    :var file: An image with represents the legend entry. This can be png or svg. It is string but BaseCode64
        encoded.
    :vartype file: str
    :var legend_text: Text to describe this legend entry.
    :vartype legend_text: str
    :var type_code: Type code of the public law restriction which is represented by this legend entry.
    :vartype type_code: str
    :var type_code_list: List of all public law restrictions which are described through this legend
        entry.
    :vartype type_code_list: str
    :var topic: Statement to describe to which public law restriction this legend entry belongs.
    :vartype topic: str
    :var subtopic: Description for sub topics this legend entry might belonging to.
    :vartype subtopic: str
    :var additional_topic: A link to additional topics. It must be like the following patterns:

        * ch.{canton}.{topic}
        * fl.{topic}
        * ch.{bfsnr}.{topic}

        This with {canton} as the official two letters short version (e.g.'BE') {topic} as the name of the
        topic and {bfsnr} as the municipality id of the federal office of statistics.
    :vartype additional_topic: str
    :var view_service_id: The foreign key to the view service this legend entry is related to.
    :vartype view_service_id: int
    :var view_service: The dedicated relation to the view service instance from database.
    :vartype view_service: pyramid_oereb.standard.models.contaminated_public_transport_sites.ViewService
    """
    __table_args__ = {'schema': 'contaminated_public_transport_sites'}
    __tablename__ = 'legend_entry'
    id = sa.Column(sa.Integer, primary_key=True)
    file = sa.Column(sa.String, nullable=False)
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
    The container where you can fill in all your public law restrictions to the topic.

    :var id: The identifier. This is used in the database only and must not be set manually. If you
        don't like it - don't care about.
    :vartype id: int
    :var content: The textual representation of the public law restriction.
    :vartype content: str
    :var topic: Category for this public law restriction (name of the topic).
    :vartype topic: str
    :var subtopic: Textual explanation to subtype the topic attribute.
    :vartype subtopic: str
    :var additional_topic: A link to additional topics. It must be like the following patterns:
        * ch.{canton}.{topic}
        * fl.{topic}
        * ch.{bfsnr}.{topic}
        This with {canton} as the official two letters short version (e.g.'BE') {topic} as the name of the
        topic and {bfsnr} as the municipality id of the federal office of statistics.
    :vartype additional_topic: str
    :var type_code: Type code of the public law restriction machine readable based on the original data
        model of this public law restriction.
    :vartype type_code: str
    :var type_code_list: List of full range of type_codes for this public law restriction in a machine
        readable format.
    :vartype type_code_list: str
    :var legal_state: The status switch if the document is legally approved or not.
    :vartype legal_state: str
    :var published_from: The date when the document should be available for publishing on extracts. This
        directly affects the behaviour of extract generation.
    :vartype published_from: datetime.date
    :var view_service_id: The foreign key to the view service this public law restriction is related to.
    :vartype view_service_id: int
    :var view_service: The dedicated relation to the view service instance from database.
    :vartype view_service: pyramid_oereb.standard.models.contaminated_public_transport_sites.ViewService
    :var office_id: The foreign key to the office which is responsible to this public law restriction.
    :vartype office_id: int
    :var responsible_office: The dedicated relation to the office instance from database.
    :vartype responsible_office: pyramid_oereb.standard.models.contaminated_public_transport_sites.Office
    """
    __table_args__ = {'schema': 'contaminated_public_transport_sites'}
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
    """
    The dedicated model for all geometries in relation to their public law restriction.

    :var id: The identifier. This is used in the database only and must not be set manually. If you
        don't like it - don't care about.
    :vartype id: int
    :var legal_state: The status switch if the document is legally approved or not.
    :vartype legal_state: str
    :var published_from: The date when the document should be available for publishing on extracts. This
        directly affects the behaviour of extract generation.
    :vartype published_from: datetime.date
    :var geo_metadata: A link to the metadata which this geometry is based on which delivers machine
        readable response format (XML).
    :vartype geo_metadata: str
    :var geom: The geometry it's self. For type information see geoalchemy2_.

        .. _geoalchemy2: https://geoalchemy-2.readthedocs.io/en/0.2.4/types.html

        docs dependent on the configured type.

        This concrete one is GEOMETRYCOLLECTION
    :vartype geom: geoalchemy2.types.Geometry
    :var public_law_restriction_id: The foreign key to the public law restriction this geometry is
        related to.
    :vartype public_law_restriction_id: int
    :var public_law_restriction: The dedicated relation to the public law restriction instance from
        database.
    :vartype public_law_restriction:
        pyramid_oereb.standard.models.contaminated_public_transport_sites.PublicLawRestriction
    :var office_id: The foreign key to the office which is responsible to this public law restriction.
    :vartype office_id: int
    :var responsible_office: The dedicated relation to the office instance from database.
    :vartype responsible_office: pyramid_oereb.standard.models.contaminated_public_transport_sites.Office
    """
    __table_args__ = {'schema': 'contaminated_public_transport_sites'}
    __tablename__ = 'geometry'
    id = sa.Column(sa.Integer, primary_key=True)
    legal_state = sa.Column(sa.String, nullable=False)
    published_from = sa.Column(sa.Date, nullable=False)
    geo_metadata = sa.Column(sa.String, nullable=True)  # TODO: Check translation
    geom = sa.Column(GeoAlchemyGeometry('GEOMETRYCOLLECTION', srid=srid))
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
    """
    Meta bucket (join table) for public law restrictions which acts as a base for other public law
    restrictions.

    :var id: The identifier. This is used in the database only and must not be set manually. If you
        don't like it - don't care about.
    :vartype id: int
    :var public_law_restriction_id: The foreign key to the public law restriction which bases on another
        public law restriction.
    :vartype public_law_restriction_id: int
    :var public_law_restriction_base_id: The foreign key to the public law restriction which is the
        base for the public law restriction.
    :vartype public_law_restriction_base_id: int
    :var plr: The dedicated relation to the public law restriction (which bases on) instance from
        database.
    :vartype plr: pyramid_oereb.standard.models.contaminated_public_transport_sites.PublicLawRestriction
    :var base: The dedicated relation to the public law restriction (which is the base) instance from
        database.
    :vartype base: pyramid_oereb.standard.models.contaminated_public_transport_sites.PublicLawRestriction
    """
    __tablename__ = 'public_law_restriction_base'
    __table_args__ = {'schema': 'contaminated_public_transport_sites'}
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
    """
    Meta bucket (join table) for public law restrictions which acts as a refinement for other public law
    restrictions.

    :var id: The identifier. This is used in the database only and must not be set manually. If you
        don't like it - don't care about.
    :vartype id: int
    :var public_law_restriction_id: The foreign key to the public law restriction which is refined by
        another public law restriction.
    :vartype public_law_restriction_id: int
    :var public_law_restriction_refinement_id: The foreign key to the public law restriction which is
        the refinement of the public law restriction.
    :vartype public_law_restriction_refinement_id: int
    :var plr: The dedicated relation to the public law restriction (which refines) instance from
        database.
    :vartype plr: pyramid_oereb.standard.models.contaminated_public_transport_sites.PublicLawRestriction
    :var base: The dedicated relation to the public law restriction (which is refined) instance from
        database.
    :vartype base: pyramid_oereb.standard.models.contaminated_public_transport_sites.PublicLawRestriction
    """
    __tablename__ = 'public_law_restriction_refinement'
    __table_args__ = {'schema': 'contaminated_public_transport_sites'}
    id = sa.Column(sa.Integer, primary_key=True)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_refinement_id = sa.Column(
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
        foreign_keys=[public_law_restriction_refinement_id]
    )


class PublicLawRestrictionDocument(Base):
    """
    Meta bucket (join table) for the relationship between public law restrictions and documents.

    :var id: The identifier. This is used in the database only and must not be set manually. If you
        don't like it - don't care about.
    :vartype id: int
    :var public_law_restriction_id: The foreign key to the public law restriction which has relation to
        a document.
    :vartype public_law_restriction_id: int
    :var document_id: The foreign key to the document which has relation to the public law restriction.
    :vartype document_id: int
    :var plr: The dedicated relation to the public law restriction instance from database.
    :vartype plr: pyramid_oereb.standard.models.contaminated_public_transport_sites.PublicLawRestriction
    :var document: The dedicated relation to the document instance from database.
    :vartype document: pyramid_oereb.standard.models.contaminated_public_transport_sites.DocumentBase
    """
    __tablename__ = 'public_law_restriction_document'
    __table_args__ = {'schema': 'contaminated_public_transport_sites'}
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
    """
    Meta bucket (join table) for the relationship between documents.

    :var id: The identifier. This is used in the database only and must not be set manually. If you
        don't like it - don't care about.
    :vartype id: int
    :var document_id: The foreign key to the document which references to another document.
    :vartype document_id: int
    :var reference_document_id: The foreign key to the document which is referenced.
    :vartype reference_document_id: int
    :var document: The dedicated relation to the document (which references) instance from database.
    :vartype document: pyramid_oereb.standard.models.contaminated_public_transport_sites.Document
    :var referenced_document: The dedicated relation to the document (which is referenced) instance from
        database.
    :vartype referenced_document: pyramid_oereb.standard.models.contaminated_public_transport_sites.Document
    :var article_numbers: A colon of article numbers which clarify the reference. This is a string
        separated by '|'.
    :vartype article_numbers: str
    """
    __tablename__ = 'document_reference'
    __table_args__ = {'schema': 'contaminated_public_transport_sites'}
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
    """
    Meta bucket (join table) for the relationship between documents and the reference definition.

    :var id: The identifier. This is used in the database only and must not be set manually. If you
        don't like it - don't care about.
    :vartype id: int
    :var document_id: The foreign key to the document which is related to a reference definition.
    :vartype document_id: int
    :var reference_definition_id: The foreign key to the document which is related to a reference
        definition.
    :vartype reference_definition_id: int
    """
    __tablename__ = 'document_reference_definition'
    __table_args__ = {'schema': 'contaminated_public_transport_sites'}
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
