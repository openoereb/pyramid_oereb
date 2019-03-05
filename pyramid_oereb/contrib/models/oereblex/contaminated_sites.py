"""
This is a full representation of the data model defined by the federal definition.

**It is representing the topic: Contaminated Sites**

You can use it to
produce a own new topic for the oereb eco system in the specifications shape. To be able to adapt this
models to your own infrastructure you must implement the same attribute names! In fact that inheritance
is not easily made you need to make your own classes and adapt them to your database.
"""
import sqlalchemy as sa
from pyramid_oereb.standard.models import NAMING_CONVENTION
from pyramid_oereb.lib.config import Config
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2.types import Geometry as GeoAlchemyGeometry
from sqlalchemy.orm import relationship
from sqlalchemy_utils import JSONType

metadata = sa.MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base()
srid = Config.get('srid')


class Availability(Base):
    """
    A simple bucket for achieving a switch per municipality. Here you can configure via the imported data if
    a public law restriction is available or not. You need to fill it with the data you provided in the
    app schemas municipality table (fosnr).

    Attributes:
        fosnr (str): The identifier of the municipality in your system (id_bfs = fosnr)
        available (bool): The switch field to configure if this plr is available for the
            municipality or not.  This field has direct influence on the applications
            behaviour. See documentation for more info.
    """
    __table_args__ = {'schema': 'contaminated_sites'}
    __tablename__ = 'availability'
    fosnr = sa.Column(sa.String, primary_key=True, autoincrement=False)
    available = sa.Column(sa.Boolean, nullable=False, default=False)


class Office(Base):
    """
    The bucket to fill in all the offices you need to reference from public law restriction, document,
    geometry.

    Attributes:
        id (str): The identifier. This is used in the database only and must not be set manually. If
            you  don't like it - don't care about.
        name (dict): The multilingual name of the office.
        office_at_web (str): A web accessible url to a presentation of this office.
        uid (str): The uid of this office from https
        line1 (str): The first address line for this office.
        line2 (str): The second address line for this office.
        street (str): The streets name of the offices address.
        number (str): The number on street.
        postal_code (int): The ZIP-code.
        city (str): The name of the city.
    """
    __table_args__ = {'schema': 'contaminated_sites'}
    __tablename__ = 'office'
    id = sa.Column(sa.String, primary_key=True, autoincrement=False)
    name = sa.Column(JSONType, nullable=False)
    office_at_web = sa.Column(sa.String, nullable=True)
    uid = sa.Column(sa.String(12), nullable=True)
    line1 = sa.Column(sa.String, nullable=True)
    line2 = sa.Column(sa.String, nullable=True)
    street = sa.Column(sa.String, nullable=True)
    number = sa.Column(sa.String, nullable=True)
    postal_code = sa.Column(sa.Integer, nullable=True)
    city = sa.Column(sa.String, nullable=True)


class DataIntegration(Base):
    """
    The bucket to fill in the date when this whole schema was updated. It has a relation to the office to be
    able to find out who was the delivering instance.

    Attributes:
        id (str): The identifier. This is used in the database only and must not be set manually. If
            you  don't like it - don't care about.
        date (datetime.date): The date when this data set was delivered.
        office_id (str): A foreign key which points to the actual office instance.
        office (pyramid_oereb.standard.models.contaminated_sites.Office):
            The actual office instance which the id points to.
    """
    __table_args__ = {'schema': 'contaminated_sites'}
    __tablename__ = 'data_integration'
    id = sa.Column(sa.String, primary_key=True, autoincrement=False)
    date = sa.Column(sa.DateTime, nullable=False)
    office_id = sa.Column(
        sa.String,
        sa.ForeignKey(Office.id),
        nullable=False)
    office = relationship(Office)
    checksum = sa.Column(sa.String, nullable=True)


class ViewService(Base):
    """
    A view service aka WM(T)S which can deliver a cartographic representation via web.

    Attributes:
        id (str): The identifier. This is used in the database only and must not be set manually. If
            you  don't like it - don't care about.
        reference_wms (str): The actual url which leads to the desired cartographic representation.
        legend_at_web (dict of str): A multilingual dictionary of links. Keys are the language, values
            are links leading to a wms describing document (png).
    """
    __table_args__ = {'schema': 'contaminated_sites'}
    __tablename__ = 'view_service'
    id = sa.Column(sa.String, primary_key=True, autoincrement=False)
    reference_wms = sa.Column(sa.String, nullable=False)
    legend_at_web = sa.Column(JSONType, nullable=True)


class LegendEntry(Base):
    """
    A class based legend system which is directly related to
    :ref:`pyramid_oereb.standard.models.contaminated_sites.ViewService`.

    Attributes:
        id (str): The identifier. This is used in the database only and must not be set manually. If
            you  don't like it - don't care about.
        symbol (str): An image with represents the legend entry. This can be png or svg. It is string
            but BaseCode64  encoded.
        legend_text (dict): Multilingual text to describe this legend entry.
        type_code (str): Type code of the public law restriction which is represented by this legend
            entry.
        type_code_list (str): List of all public law restrictions which are described through this
            legend  entry.
        topic (str): Statement to describe to which public law restriction this legend entry
            belongs.
        sub_theme (dict): Multilingual description for sub topics this legend entry might belonging to.
        other_theme (str): A link to additional topics. It must be like the following patterns
            * ch.{canton}.{topic}  * fl.{topic}  * ch.{bfsnr}.{topic}  This with {canton} as
            the official two letters short version (e.g.'BE') {topic} as the name of the
            topic and {bfsnr} as the municipality id of the federal office of statistics.
        view_service_id (str): The foreign key to the view service this legend entry is related to.
        view_service (pyramid_oereb.standard.models.contaminated_sites.ViewService):
            The dedicated relation to the view service instance from database.
    """
    __table_args__ = {'schema': 'contaminated_sites'}
    __tablename__ = 'legend_entry'
    id = sa.Column(sa.String, primary_key=True, autoincrement=False)
    symbol = sa.Column(sa.String, nullable=False)
    legend_text = sa.Column(JSONType, nullable=False)
    type_code = sa.Column(sa.String(40), nullable=False)
    type_code_list = sa.Column(sa.String, nullable=False)
    topic = sa.Column(sa.String, nullable=False)
    sub_theme = sa.Column(JSONType, nullable=True)
    other_theme = sa.Column(sa.String, nullable=True)
    view_service_id = sa.Column(
        sa.String,
        sa.ForeignKey(ViewService.id),
        nullable=False
    )
    view_service = relationship(ViewService, backref='legends')


class PublicLawRestriction(Base):
    """
    The container where you can fill in all your public law restrictions to the topic.

    Attributes:
        id (str): The identifier. This is used in the database only and must not be set manually. If
            you  don't like it - don't care about.
        information (dict): The multilingual textual representation of the public law restriction.
        topic (str): Category for this public law restriction (name of the topic).
        sub_theme (dict): Multilingual textual explanation to subtype the topic attribute.
        other_theme (str): A link to additional topics. It must be like the following patterns
            * ch.{canton}.{topic}  * fl.{topic}  * ch.{bfsnr}.{topic}  This with {canton} as
            the official two letters short version (e.g.'BE') {topic} as the name of the
            topic and {bfsnr} as the municipality id of the federal office of statistics.
        type_code (str): Type code of the public law restriction machine readable based on the
            original data  model of this public law restriction.
        type_code_list (str): List of full range of type_codes for this public law restriction in a
            machine  readable format.
        law_status (str): The status switch if the document is legally approved or not.
        published_from (datetime.date): The date when the document should be available for
            publishing on extracts. This  directly affects the behaviour of extract
            generation.
        view_service_id (str): The foreign key to the view service this public law restriction is
            related to.
        view_service (pyramid_oereb.standard.models.contaminated_sites.ViewService):
            The dedicated relation to the view service instance from database.
        office_id (str): The foreign key to the office which is responsible to this public law
            restriction.
        responsible_office (pyramid_oereb.standard.models.contaminated_sites.Office):
            The dedicated relation to the office instance from database.
    """
    __table_args__ = {'schema': 'contaminated_sites'}
    __tablename__ = 'public_law_restriction'
    id = sa.Column(sa.String, primary_key=True, autoincrement=False)
    information = sa.Column(JSONType, nullable=False)
    topic = sa.Column(sa.String, nullable=False)
    sub_theme = sa.Column(JSONType, nullable=True)
    other_theme = sa.Column(sa.String, nullable=True)
    type_code = sa.Column(sa.String(40), nullable=True)
    type_code_list = sa.Column(sa.String, nullable=True)
    law_status = sa.Column(sa.String, nullable=False)
    published_from = sa.Column(sa.Date, nullable=False)
    geolink = sa.Column(sa.Integer, nullable=True)
    view_service_id = sa.Column(
        sa.String,
        sa.ForeignKey(ViewService.id),
        nullable=False
    )
    view_service = relationship(
        ViewService,
        backref='public_law_restrictions'
    )
    office_id = sa.Column(
        sa.String,
        sa.ForeignKey(Office.id),
        nullable=False
    )
    responsible_office = relationship(Office)


class Geometry(Base):
    """
    The dedicated model for all geometries in relation to their public law restriction.

    Attributes:
        id (str): The identifier. This is used in the database only and must not be set manually. If
            you  don't like it - don't care about.
        law_status (str): The status switch if the document is legally approved or not.
        published_from (datetime.date): The date when the document should be available for
            publishing on extracts. This  directly affects the behaviour of extract
            generation.
        geo_metadata (str): A link to the metadata which this geometry is based on which delivers
            machine  readable response format (XML).
        public_law_restriction_id (str): The foreign key to the public law restriction this geometry
            is  related to.
        public_law_restriction (pyramid_oereb.standard.models.contaminated_sites
            .PublicLawRestriction): The dedicated relation to the public law restriction instance from
            database.
        office_id (str): The foreign key to the office which is responsible to this public law
            restriction.
        responsible_office (pyramid_oereb.standard.models.contaminated_sites.Office):
            The dedicated relation to the office instance from database.
        geom (geoalchemy2.types.Geometry): The geometry it's self. For type information see
            geoalchemy docs (https://geoalchemy-2.readthedocs.io/en/0.4.2/types.html) dependent on the
            configured type.  This concrete one is GEOMETRYCOLLECTION
    """
    __table_args__ = {'schema': 'contaminated_sites'}
    __tablename__ = 'geometry'
    id = sa.Column(sa.String, primary_key=True, autoincrement=False)
    law_status = sa.Column(sa.String, nullable=False)
    published_from = sa.Column(sa.Date, nullable=False)
    geo_metadata = sa.Column(sa.String, nullable=True)
    geom = sa.Column(GeoAlchemyGeometry('GEOMETRYCOLLECTION', srid=srid), nullable=False)
    public_law_restriction_id = sa.Column(
        sa.String,
        sa.ForeignKey(PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction = relationship(
        PublicLawRestriction,
        backref='geometries'
    )
    office_id = sa.Column(
        sa.String,
        sa.ForeignKey(Office.id),
        nullable=False
    )
    responsible_office = relationship(Office)


class PublicLawRestrictionBase(Base):
    """
    Meta bucket (join table) for public law restrictions which acts as a base for other public law
    restrictions.

    Attributes:
        id (str): The identifier. This is used in the database only and must not be set manually. If
            you  don't like it - don't care about.
        public_law_restriction_id (str): The foreign key to the public law restriction which bases
            on another  public law restriction.
        public_law_restriction_base_id (str): The foreign key to the public law restriction which is
            the  base for the public law restriction.
        plr (pyramid_oereb.standard.models.contaminated_sites.PublicLawRestriction):
            The dedicated relation to the public law restriction (which bases on) instance from  database.
        base (pyramid_oereb.standard.models.contaminated_sites.PublicLawRestriction):
            The dedicated relation to the public law restriction (which is the base) instance from database.
    """
    __tablename__ = 'public_law_restriction_base'
    __table_args__ = {'schema': 'contaminated_sites'}
    id = sa.Column(sa.String, primary_key=True, autoincrement=False)
    public_law_restriction_id = sa.Column(
        sa.String,
        sa.ForeignKey(PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.String,
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

    Attributes:
        id (str): The identifier. This is used in the database only and must not be set manually. If
            you  don't like it - don't care about.
        public_law_restriction_id (str): The foreign key to the public law restriction which is
            refined by  another public law restriction.
        public_law_restriction_refinement_id (str): The foreign key to the public law restriction
            which is  the refinement of the public law restriction.
        plr (pyramid_oereb.standard.models.contaminated_sites.PublicLawRestriction):
            The dedicated relation to the public law restriction (which refines) instance from  database.
        base (pyramid_oereb.standard.models.contaminated_sites.PublicLawRestriction):
            The dedicated relation to the public law restriction (which is refined) instance from database.
    """
    __tablename__ = 'public_law_restriction_refinement'
    __table_args__ = {'schema': 'contaminated_sites'}
    id = sa.Column(sa.String, primary_key=True, autoincrement=False)
    public_law_restriction_id = sa.Column(
        sa.String,
        sa.ForeignKey(PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_refinement_id = sa.Column(
        sa.String,
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
