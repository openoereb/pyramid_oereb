# -*- coding: utf-8 -*-
import sqlalchemy as sa
from geoalchemy2 import Geometry
from sqlalchemy.ext.declarative import declarative_base

from pyramid_oereb.standard.models import NAMING_CONVENTION
from pyramid_oereb import app_schema_name, srid

metadata = sa.MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base()

# use standard values if they are not provided via config
if not app_schema_name:
    app_schema_name = 'pyramid_oereb_main'
if not srid:
    srid = 2056


class Municipality(Base):
    __table_args__ = {'schema': app_schema_name}
    __tablename__ = 'municipality'
    fosnr = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    published = sa.Column(sa.Boolean, nullable=False, default=False, server_default=sa.text('FALSE'))
    logo = sa.Column(sa.String, nullable=False)
    geom = sa.Column(Geometry('MULTIPOLYGON', srid=srid), nullable=True)


class RealEstate(Base):
    __table_args__ = {'schema': app_schema_name}
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
    limit = sa.Column(Geometry('MULTIPOLYGON', srid=srid))


class Address(Base):
    __table_args__ = (
        sa.PrimaryKeyConstraint("street_name", "street_number", "zip_code"),
        {'schema': app_schema_name}
    )
    __tablename__ = 'address'
    street_name = sa.Column(sa.Unicode, nullable=False)
    street_number = sa.Column(sa.String, nullable=False)
    zip_code = sa.Column(sa.Integer, nullable=False)
    geom = sa.Column(Geometry('POINT', srid=srid))


class Glossary(Base):
    __table_args__ = {'schema': app_schema_name}
    __tablename__ = 'glossary'
    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String, nullable=False)
    content = sa.Column(sa.String, nullable=False)


class ExclusionOfLiability(Base):
    __table_args__ = {'schema': app_schema_name}
    __tablename__ = 'exclusion_of_liability'
    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String, nullable=False)
    content = sa.Column(sa.String, nullable=False)
