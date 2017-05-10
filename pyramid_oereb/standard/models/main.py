# -*- coding: utf-8 -*-
"""
This is representing the applications working data schema. It provides buckets for general data you will need
to run this application in standard mode.
The buckets are:

* Municipality
* Real Estate
* Adress
* Glossary
* Exclusion of liability

The geographical projection system which is used out of the box is LV95 aka EPSG:2056. Of course you can
configure a different one.
The name of the schema will be::

    pyramid_oereb_main

But you can change it also via configuration.

    .. note::

        Whenever you configure your own sqlalchemy ORM's to use them in this application you must imitate
        the behaviour of the ORM's here. This means the names class variables as well as the types of these
        variables.

"""
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
    """
    The municipality is the place where you hold the information about all the municipalities you are having
    in your canton. This is used also in the applications process to check whether a municipality is published
    or not.

    :var fosnr: The identifier of the municipality. It is the commonly known id_bfs.
    :vartype fosnr: int
    :var name: The Name of the municipality.
    :vartype name: str
    :var published: Switch whether a municipality is published or not. This has direct influence on extract
        generation.
    :vartype published: bool
    :var logo: The emblem of the municipality as string but encoded by BaseCode64. Please refer to the
        specification for more details about format and dimensons.
    :vartype logo: str
    :var geom: The geometry of municipality borders. For type information see geoalchemy2_.

        .. _geoalchemy2: https://geoalchemy-2.readthedocs.io/en/0.2.4/types.html

        docs dependent on the configured type.

        This concrete one is MULTIPOLYGON
    :vartype geom: geoalchemy2.types.Geometry
    """
    __table_args__ = {'schema': app_schema_name}
    __tablename__ = 'municipality'
    fosnr = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    published = sa.Column(sa.Boolean, nullable=False, default=False, server_default=sa.text('FALSE'))
    logo = sa.Column(sa.String, nullable=False)
    geom = sa.Column(Geometry('MULTIPOLYGON', srid=srid), nullable=True)


class RealEstate(Base):
    """
    The bucket where you can throw in all the real estates this application should have access to, for
    creating extracts.

    :var id: The identifier. This is used in the database only and must not be set manually. If you
        don't like-don't care about.
    :vartype id: int
    :var identdn: The identifier in cantonal level
    :vartype identdn: str
    :var number: The identifier on municipality level.
    :vartype number: str
    :var egrid: The identifier on federal level (the all unique one...)
    :vartype egrid: str
    :var type: The type of the real estate (This must base on DM01)
    :vartype type: str
    :var canton: Which canton this real estate is situated in (use official shortened Version here. e.g. 'BE')
    :vartype canton: str
    :var municipality: The name of the municipality this real estate is situated in.
    :vartype municipality: str
    :var subunit_of_land_register: The name of the maybe existing sub unit of land register if municipality in
        combination with number does not offer a unique constraint. Else you can skip that.
    :vartype subunit_of_land_register: str
    :var fosnr: The identifier of the municipality. It is the commonly known id_bfs.
    :vartype fosnr: int
    :var metadata_of_geographical_base_data: A link to the metadata which this geometry is based on which
        delivers machine readable response format (XML).
    :vartype metadata_of_geographical_base_data: str
    :var land_registry_area: The amount of the area of this real estate as it is declared in the land
        registers information.
    :vartype land_registry_area: str
    :var limit: The geometry of real estates border. For type information see geoalchemy2_.

        .. _geoalchemy2: https://geoalchemy-2.readthedocs.io/en/0.2.4/types.html

        docs dependent on the configured type.

        This concrete one is MULTIPOLYGON
    :vartype limit: geoalchemy2.types.Geometry
    """
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
    """
    The bucket you can throw all addresses in the application should be able to use for the get egrid
    webservice. This is a bypass for the moment. In the end it seems ways more flexible to bind a service here
    but if you like you can use it.

    :var street_name: The street name for this address.
    :vartype street_name: unicode
    :var street_number: The house number of this address.
    :vartype street_number: str
    :var zip_code: The ZIP code for this address.
    :vartype zip_code: int
    :var geom: The geometry of real estates border. For type information see geoalchemy2_.

        .. _geoalchemy2: https://geoalchemy-2.readthedocs.io/en/0.2.4/types.html

        docs dependent on the configured type.

        This concrete one is POINT
    :vartype geom: geoalchemy2.types.Geometry
    """
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
    """
    The bucket you can throw all items you want to have in the extracts glossary as reading help.

    :var id: The identifier. This is used in the database only and must not be set manually. If you
        don't like-don't care about.
    :vartype id: int
    :var title: The title which the glossary item has.
    :vartype title: str
    :var content: The content which the glossary item has.
    :vartype content: str
    """
    __table_args__ = {'schema': app_schema_name}
    __tablename__ = 'glossary'
    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String, nullable=False)
    content = sa.Column(sa.String, nullable=False)


class ExclusionOfLiability(Base):
    """
    The bucket you can throw all addresses in the application should be able to use for the get egrid
    webservice. This is a bypass for the moment. In the end it seems ways more flexible to bind a service here
    but if you like you can use it.

    :var id: The identifier. This is used in the database only and must not be set manually. If you
        don't like-don't care about.
    :vartype id: int
    :var title: The title which the exclusion of liability item has.
    :vartype title: str
    :var content: The content which the exclusion of liability item has.
    :vartype content: str
    """
    __table_args__ = {'schema': app_schema_name}
    __tablename__ = 'exclusion_of_liability'
    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String, nullable=False)
    content = sa.Column(sa.String, nullable=False)
