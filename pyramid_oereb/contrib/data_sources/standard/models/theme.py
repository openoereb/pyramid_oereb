from sqlalchemy import String, Integer
from sqlalchemy.ext.declarative import declarative_base

from pyramid_oereb.contrib.data_sources.standard.models import (
    get_office,
    get_document,
    get_view_service,
    get_legend_entry,
    get_public_law_restriction,
    get_geometry,
    get_public_law_restriction_document
)


class Models(object):

    def __init__(self, office, document, view_service,
                 legend_entry, public_law_restriction, geometry,
                 public_law_restriction_document, base, db_connection, schema_name):

        self.Office = office
        self.Document = document
        self.ViewService = view_service
        self.LegendEntry = legend_entry
        self.PublicLawRestriction = public_law_restriction
        self.Geometry = geometry
        self.PublicLawRestrictionDocument = public_law_restriction_document
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
        db_connection (str): the db connection string

    Returns:
        Models: the produced set of standard models
    """
    Base = declarative_base()

    Office = get_office(Base, schema_name, pk_type)
    Document = get_document(Base, schema_name, pk_type, Office)
    ViewService = get_view_service(Base, schema_name, pk_type)
    LegendEntry = get_legend_entry(Base, schema_name, pk_type, ViewService)
    PublicLawRestriction = get_public_law_restriction(Base, schema_name, pk_type, Office, ViewService,
                                                      LegendEntry)
    Geometry = get_geometry(Base, schema_name, pk_type, geometry_type, srid, PublicLawRestriction)
    PublicLawRestrictionDocument = get_public_law_restriction_document(Base, schema_name, pk_type,
                                                                       PublicLawRestriction, Document)

    return Models(
        Office, Document, ViewService,
        LegendEntry, PublicLawRestriction, Geometry, PublicLawRestrictionDocument,
        Base, db_connection, schema_name
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
