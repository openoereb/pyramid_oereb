# -*- coding: utf-8 -*-
"""
This Package provides all models fitting to the standard database configuration. It is separated by the 17
mandatory topics the federation asks for.
"""


from sqlalchemy import Column, ForeignKey
from sqlalchemy import String, Integer, Float, Date
from geoalchemy2.types import Geometry as GeoAlchemyGeometry
from sqlalchemy.orm import relationship
from sqlalchemy_utils import JSONType


NAMING_CONVENTION = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}


def get_office(base, schema_name, pk_type):
    """
    Factory to produce a generic office model.

    Args:
        base (sqlalchemy.orm.decl_api.DeclarativeMeta): The SQLAlchemy base which is assigned to the models.
        schema_name (str): The name of the database schema where this models belong to.
        pk_type (sqlalchemy.sql.type_api.TypeEngine): The type of the primary column. E.g.
            sqlalchemy.String or sqlalchemy.Integer or another one fitting the underlying DB
            needs

    Returns:
        sqlalchemy.orm.decl_api.DeclarativeMeta: The generated office model.
    """

    class Office(base):
        """
        The bucket to fill in all the offices you need to reference from public law restriction, document,
        geometry.

        Attributes:
            id (str): The identifier. This is used in the database only and must not be set manually. If
                you  don't like it - don't care about.
            name (dict): The multilingual name of the office.
            office_at_web (dict): A web accessible url to a presentation of this office (multilingual).
            uid (str): The uid of this office from https
            line1 (str): The first address line for this office.
            line2 (str): The second address line for this office.
            street (str): The streets name of the offices address.
            number (str): The number on street.
            postal_code (int): The ZIP-code.
            city (str): The name of the city.
        """
        __table_args__ = {'schema': schema_name}
        __tablename__ = 'office'
        id = Column(pk_type, primary_key=True, autoincrement=False)
        name = Column(JSONType, nullable=False)
        office_at_web = Column(JSONType, nullable=True)
        uid = Column(String(12), nullable=True)
        line1 = Column(String, nullable=True)
        line2 = Column(String, nullable=True)
        street = Column(String, nullable=True)
        number = Column(String, nullable=True)
        postal_code = Column(Integer, nullable=True)
        city = Column(String, nullable=True)

    return Office


def get_document(base, schema_name, pk_type, Office):
    """
    Factory to produce a generic document model.

    Args:
        base (sqlalchemy.orm.decl_api.DeclarativeMeta): The SQLAlchemy base which is assigned to the models.
        schema_name (str): The name of the database schema where this models belong to.
        pk_type (sqlalchemy.sql.type_api.TypeEngine): The type of the primary column. E.g.
            sqlalchemy.String or sqlalchemy.Integer or another one fitting the underlying DB
            needs
        Office (sqlalchemy.orm.decl_api.DeclarativeMeta): The office model.

    Returns:
        sqlalchemy.orm.decl_api.DeclarativeMeta: The generated office model.
    """

    class Document(base):
        """
        THE DOCUMENT
        This represents the main document in the whole system.

        Attributes:
            id (int): The identifier. This is used in the database only and must not be set manually. If
                you  don't like it - don't care about.
            document_type (str): The document type. It must be "Rechtsvorschrift", "GesetzlicheGrundlage"
                or "Hinweis".
            index (int): An index used to sort the documents.
            law_status (str): The status switch if the document is legally approved or not.
            title (dict): The multilingual title or if existing the short title ot his document.
            office_id (str): The foreign key to the office which is in charge for this document.
            responsible_office (pyramid_oereb.standard.models.railways_project_planning_zones.Office):
                The dedicated relation to the office instance from database.
            published_from (datetime.date): The date from when the document should be available for
                publishing in extracts. This  directly affects the behaviour of extract
                generation.
            published_until (datetime.date): The date until when the document should be available for
                publishing on extracts. This  directly affects the behaviour of extract
                generation.
            text_at_web (dict): A multilingual link which leads to the documents content in the web.
            abbreviation (dict): The multilingual shortened version of the documents title.
            official_number (dict): The multilingual official number which uniquely identifies this document.
            only_in_municipality (int): The fosnr (=id bfs) of the municipality. If this is None it is assumed
                the document is  related to the whole canton or even the confederation.
            file (str): The document itself as a binary representation (PDF). It is string but
                BaseCode64 encoded.
        """
        __table_args__ = {'schema': schema_name}
        __tablename__ = 'document'
        id = Column(pk_type, primary_key=True, autoincrement=False)
        document_type = Column(String, nullable=False)
        index = Column(Integer, nullable=False)
        law_status = Column(String, nullable=False)
        title = Column(JSONType, nullable=False)
        office_id = Column(
            ForeignKey(Office.id),
            nullable=False
        )
        responsible_office = relationship(Office)
        published_from = Column(Date, nullable=False)
        published_until = Column(Date, nullable=True)
        text_at_web = Column(JSONType, nullable=True)
        abbreviation = Column(JSONType, nullable=True)
        official_number = Column(JSONType, nullable=True)
        only_in_municipality = Column(Integer, nullable=True)
        file = Column(String, nullable=True)

    return Document


def get_view_service(base, schema_name, pk_type):
    """
    Factory to produce a generic view service model.

    Args:
        base (sqlalchemy.orm.decl_api.DeclarativeMeta): The SQLAlchemy base which is assigned to the models.
        schema_name (str): The name of the database schema where this models belong to.
        pk_type (sqlalchemy.sql.type_api.TypeEngine): The type of the primary column. E.g.
            sqlalchemy.String or sqlalchemy.Integer or another one fitting the underlying DB
            needs

    Returns:
        sqlalchemy.orm.decl_api.DeclarativeMeta: The generated office model.
    """

    class ViewService(base):
        """
        A view service aka WM(T)S which can deliver a cartographic representation via web.

        Attributes:
            id (str): The identifier. This is used in the database only and must not be set
                manually. If you  don't like it - don't care about.
            reference_wms (dict of str): The actual url which leads to the desired cartographic
                representation (multilingual).
            layer_index (int): Index for sorting the layering of the view services for a theme
            layer_opacity (float): Opacity of a view service
        """
        __table_args__ = {'schema': schema_name}
        __tablename__ = 'view_service'
        id = Column(pk_type, primary_key=True, autoincrement=False)
        reference_wms = Column(JSONType, nullable=False)
        layer_index = Column(Integer, nullable=False)
        layer_opacity = Column(Float, nullable=False)

    return ViewService


def get_legend_entry(base, schema_name, pk_type, ViewService):
    """
    Factory to produce a generic legend entry model.

    Args:
        base (sqlalchemy.orm.decl_api.DeclarativeMeta): The SQLAlchemy base which is assigned to the models.
        schema_name (str): The name of the database schema where this models belong to.
        pk_type (sqlalchemy.sql.type_api.TypeEngine): The type of the primary column. E.g.
            sqlalchemy.String or sqlalchemy.Integer or another one fitting the underlying DB
            needs
        ViewService (sqlalchemy.orm.decl_api.DeclarativeMeta): The view service model.

    Returns:
        sqlalchemy.orm.decl_api.DeclarativeMeta: The generated office model.
    """

    class LegendEntry(base):
        """
        A class based legend system which is directly related to :class:`ViewService`.

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
            theme (str): Theme code to link this legend entry with the correct public law restriction.
            sub_theme (str): Sub-theme code to link this legend entry with the sub-theme of the public
                law restriction if there is a sub-theme.
            view_service_id (str): The foreign key to the view service this legend entry is related to.
            view_service (ViewService):
                The dedicated relation to the view service instance from database.
        """
        __table_args__ = {'schema': schema_name}
        __tablename__ = 'legend_entry'
        id = Column(pk_type, primary_key=True, autoincrement=False)
        symbol = Column(String, nullable=False)
        legend_text = Column(JSONType, nullable=False)
        type_code = Column(String(40), nullable=False)
        type_code_list = Column(String, nullable=False)
        theme = Column(String, nullable=False)
        sub_theme = Column(String, nullable=True)
        view_service_id = Column(
            ForeignKey(ViewService.id),
            nullable=False
        )
        view_service = relationship(ViewService, backref='legends')

    return LegendEntry


def get_public_law_restriction(base, schema_name, pk_type, Office, ViewService, LegendEntry):
    """
    Factory to produce a generic public law restriction model.

    Args:
        base (sqlalchemy.orm.decl_api.DeclarativeMeta): The SQLAlchemy base which is assigned to the models.
        schema_name (str): The name of the database schema where this models belong to.
        pk_type (sqlalchemy.sql.type_api.TypeEngine): The type of the primary column. E.g.
            sqlalchemy.String or sqlalchemy.Integer or another one fitting the underlying DB
            needs
        Office (sqlalchemy.orm.decl_api.DeclarativeMeta): The office model.
        ViewService (sqlalchemy.orm.decl_api.DeclarativeMeta): The view service model.
        LegendEntry (sqlalchemy.orm.decl_api.DeclarativeMeta): The legend entry model.

    Returns:
        sqlalchemy.orm.decl_api.DeclarativeMeta: The generated office model.
    """

    class PublicLawRestriction(base):
        """
        The container where you can fill in all your public law restrictions to the topic.

        Attributes:
            id (str): The identifier. This is used in the database only and must not be set manually. If
                you  don't like it - don't care about.
            law_status (str): The status switch if the document is legally approved or not.
            published_from (datetime.date): The date when the document should be available for
                publishing on extracts. This  directly affects the behaviour of extract
                generation.
            published_until (datetime.date): The date starting from which the document should not be
                published anymore on extracts. This directly affects the behaviour of extract generation.
            view_service_id (str): The foreign key to the view service this public law restriction is
                related to.
            view_service (ViewService):
                The dedicated relation to the view service instance from database.
            office_id (str): The foreign key to the office which is responsible to this public law
                restriction.
            responsible_office (Office):
                The dedicated relation to the office instance from database.
            legend_entry_id (str): The foreign key to the legend entry this public law restriction is
                related to.
            legend_entry (pyramid_oereb.standard.models.airports_building_lines.LegendEntry):
                The dedicated relation to the legend entry instance from database.
        """
        __table_args__ = {'schema': schema_name}
        __tablename__ = 'public_law_restriction'
        id = Column(pk_type, primary_key=True, autoincrement=False)
        law_status = Column(String, nullable=False)
        published_from = Column(Date, nullable=False)
        published_until = Column(Date, nullable=True)
        view_service_id = Column(
            ForeignKey(ViewService.id),
            nullable=False
        )
        view_service = relationship(
            ViewService,
            backref='public_law_restrictions'
        )
        office_id = Column(
            ForeignKey(Office.id),
            nullable=False
        )
        responsible_office = relationship(Office)
        legend_entry_id = Column(
            ForeignKey(LegendEntry.id),
            nullable=False
        )
        legend_entry = relationship('LegendEntry', backref='public_law_restrictions')

    return PublicLawRestriction


def get_geometry(base, schema_name, pk_type, geometry_type, srid, PublicLawRestriction):
    """
    Factory to produce a generic geometry model.

    Args:
        base (sqlalchemy.orm.decl_api.DeclarativeMeta): The SQLAlchemy base which is assigned to the models.
        schema_name (str): The name of the database schema where this models belong to.
        pk_type (sqlalchemy.sql.type_api.TypeEngine): The type of the primary column. E.g.
            sqlalchemy.String or sqlalchemy.Integer or another one fitting the underlying DB
            needs
        geometry_type (str): The geoalchemy geometry type defined as well known string.
        srid (int): The SRID defining the projection of the geometries stored in standard db schema.
        PublicLawRestriction (sqlalchemy.orm.decl_api.DeclarativeMeta): The public law restriction model.

    Returns:
        sqlalchemy.orm.decl_api.DeclarativeMeta: The generated office model.
    """

    class Geometry(base):
        """
        The dedicated model for all geometries in relation to their public law restriction.

        Attributes:
            id (str): The identifier. This is used in the database only and must not be set manually. If
                you  don't like it - don't care about.
            law_status (str): The status switch if the document is legally approved or not.
            published_from (datetime.date): The date when the geometry should be available for
                publishing on extracts. This directly affects the behaviour of extract
                generation.
            published_until (datetime.date): The date from when the geometry should not be available
                anymore for publishing on extracts. This directly affects the behaviour of extract
                generation.
            geo_metadata (str): A link to the metadata which this geometry is based on which delivers
                machine  readable response format (XML).
            public_law_restriction_id (str): The foreign key to the public law restriction this geometry
                is  related to.
            public_law_restriction (PublicLawRestriction): The dedicated relation to the public law
                restriction instance from database.
            geom (geoalchemy2.types.Geometry): The geometry it's self. For type information see
                geoalchemy docs (https://geoalchemy-2.readthedocs.io/en/0.4.2/types.html) dependent on the
                configured type.  This concrete one is LINESTRING
        """
        __table_args__ = {'schema': schema_name}
        __tablename__ = 'geometry'
        id = Column(pk_type, primary_key=True, autoincrement=False)
        law_status = Column(String, nullable=False)
        published_from = Column(Date, nullable=False)
        published_until = Column(Date, nullable=True)
        geo_metadata = Column(String, nullable=True)
        geom = Column(GeoAlchemyGeometry(geometry_type, srid=srid), nullable=False)
        public_law_restriction_id = Column(
            ForeignKey(PublicLawRestriction.id),
            nullable=False
        )
        public_law_restriction = relationship(
            PublicLawRestriction,
            backref='geometries'
        )

    return Geometry


def get_public_law_restriction_document(base, schema_name, pk_type, PublicLawRestriction, Document):
    """
    Factory to produce a generic public law restriction document model.

    Args:
        base (sqlalchemy.orm.decl_api.DeclarativeMeta): The SQLAlchemy base which is assigned to the models.
        schema_name (str): The name of the database schema where this models belong to.
        pk_type (sqlalchemy.sql.type_api.TypeEngine): The type of the primary column. E.g.
            sqlalchemy.String or sqlalchemy.Integer or another one fitting the underlying DB
            needs
        PublicLawRestriction (sqlalchemy.orm.decl_api.DeclarativeMeta): The public law restriction model.
        Document (sqlalchemy.orm.decl_api.DeclarativeMeta): The document model.

    Returns:
        sqlalchemy.orm.decl_api.DeclarativeMeta: The generated office model.
    """

    class PublicLawRestrictionDocument(base):
        """
        Meta bucket (join table) for the relationship between public law restrictions and documents.

        Attributes:
            id (str): The identifier. This is used in the database only and must not be set manually. If
                you  don't like it - don't care about.
            public_law_restriction_id (str): The foreign key to the public law restriction which has
                relation to  a document.
            document_id (str): The foreign key to the document which has relation to the public law
                restriction.
            plr (PublicLawRestriction):
                The dedicated relation to the public law restriction instance from database.
            document (Document):
                The dedicated relation to the document instance from database.
        """
        __tablename__ = 'public_law_restriction_document'
        __table_args__ = {'schema': schema_name}
        id = Column(pk_type, primary_key=True, autoincrement=False)
        public_law_restriction_id = Column(
            ForeignKey(PublicLawRestriction.id),
            nullable=False
        )
        document_id = Column(
            ForeignKey(Document.id),
            nullable=False
        )
        plr = relationship(
            PublicLawRestriction,
            backref='legal_provisions'
        )
        document = relationship(
            Document
        )

    return PublicLawRestrictionDocument
