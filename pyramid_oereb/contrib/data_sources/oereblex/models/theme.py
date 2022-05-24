from sqlalchemy import Column, ForeignKey
from sqlalchemy import String, Integer, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from pyramid_oereb.contrib.data_sources.standard.models import (
    get_office,
    get_view_service,
    get_legend_entry,
    get_geometry
)


class Models(object):

    def __init__(self, office, view_service,
                 legend_entry, public_law_restriction, geometry, base,
                 db_connection, schema_name):

        self.Office = office
        self.ViewService = view_service
        self.LegendEntry = legend_entry
        self.PublicLawRestriction = public_law_restriction
        self.Geometry = geometry
        self.Base = base
        self.db_connection = db_connection
        self.schema_name = schema_name


def model_factory(schema_name, pk_type, geometry_type, srid, db_connection):
    """
    Factory to produce a set of standard models.

    Args:
        schema_name (str): The name of the database schema where this models belong to.
        pk_type (sqlalchemy.sql.type_api.TypeEngine): The type of the primary column. E.g.
            sqlalchemy.String or sqlalchemy.Integer or another one fitting the underlying DB
            needs
        geometry_type (str): The geoalchemy geometry type defined as well known string.
        srid (int): The SRID defining the projection of the geometries stored in standard db schema.
    """
    Base = declarative_base()

    Office = get_office(Base, schema_name, pk_type)
    ViewService = get_view_service(Base, schema_name, pk_type)
    LegendEntry = get_legend_entry(Base, schema_name, pk_type, ViewService)

    class PublicLawRestriction(Base):
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
            geolink (int): The OEREBlex GEO-Link ID to query the documents.
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
        geolink = Column(Integer, nullable=False)
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

    Geometry = get_geometry(Base, schema_name, pk_type, geometry_type, srid, PublicLawRestriction)

    return Models(
        Office, ViewService,
        LegendEntry, PublicLawRestriction, Geometry, Base,
        db_connection, schema_name
    )


def model_factory_string_pk(schema_name, geometry_type, srid, db_connection):
    """
    Args:
        schema_name (str): The name of the database schema where this models belong to.
        geometry_type (str): The geoalchemy geometry type defined as well known string.
        srid (int): The SRID defining the projection of the geometries stored in standard db schema.
        db_connection (str): the db connection string

    Returns:
        Models: the produced set of standard models
    """
    return model_factory(schema_name, String, geometry_type, srid, db_connection)


def model_factory_integer_pk(schema_name, geometry_type, srid, db_connection):
    """
    Args:
        schema_name (str): The name of the database schema where this models belong to.
        geometry_type (str): The geoalchemy geometry type defined as well known string.
        srid (int): The SRID defining the projection of the geometries stored in standard db schema.
        db_connection (str): the db connection string

    Returns:
        Models: the produced set of standard models
    """
    return model_factory(schema_name, Integer, geometry_type, srid, db_connection)
