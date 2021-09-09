# -*- coding: utf-8 -*-
"""
This is representing the applications working data schema. It provides buckets for general data you will need
to run this application in standard mode.
The buckets are:

* Municipality
* Real Estate
* Address
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
from sqlalchemy import Column, PrimaryKeyConstraint
from sqlalchemy import Unicode, String, Text, Integer, Boolean, LargeBinary
from sqlalchemy.sql.schema import ForeignKey
from geoalchemy2 import Geometry
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import JSONType

from pyramid_oereb.lib.config import Config

Base = declarative_base()
app_schema_name = Config.get('app_schema').get('name')
srid = Config.get('srid')


class Theme(Base):
    """
    The OEREB themes of the application

    Attributes:
        t_id (int): identifier, used in the database only
        code (str): OEREB code of the theme - unique and used to link each PublicLawRestriction
            with the corresponding theme
        subcode (str): OEREB code of the theme - unique and used to link each PublicLawRestriction
            with the corresponding subtheme
        title (text): The multilingual title of his document.
                    Interlis type: LocalisationCH_V1.MultilingualText.
        title_de (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        title_fr (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        title_it (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        title_rm (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        title_en (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        extract_index (int): index to sort the themes in the extract, defined in the specification
    """
    __table_args__ = {'schema': app_schema_name}
    __tablename__ = 'thema'
    t_id = Column(Integer, primary_key=True, autoincrement=False)
    code = Column('acode', String, unique=True, nullable=False)
    subcode = Column(String, unique=True, nullable=True)
    title = Column('titel', text, nullable=True)
    title_de = Column('titel_de', text, nullable=True)
    title_fr = Column('titel_fr', text, nullable=True)
    title_it = Column('titel_it', text, nullable=True)
    title_rm = Column('titel_rm', text, nullable=True)
    title_en = Column('titel_en', text, nullable=True)
    extract_index = Column('auszugindex', Integer, nullable=False)

class Office(Base):
    """
    The bucket to fill in all the offices you need to reference from public law restriction, document,
    geometry.

    Attributes:
        t_id (int): The identifier. This is used in the database only and must not be set manually.
                If you  don't like it - don't care about.
        t_ili_tid (str): TID from the transfer file.
        name (text): The name of the office. Interlis type: LocalisationCH_V1.MultilingualText.
        name_de (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        name_fr (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        name_it (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        name_rm (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        name_en (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        uid (str): The uid of this office from https
        line1 (str): The first address line for this office.
        line2 (str): The second address line for this office.
        street (str): The streets name of the offices address.
        number (str): The number on street.
        postal_code (int): The ZIP-code.
        city (str): The name of the city.
    """
    __table_args__ = {'schema': app_schema_name}
    __tablename__ = 'amt'
    t_id = Column(Integer, primary_key=True, autoincrement=False)
    t_ili_tid = Column(String, nullable=True)
    name = Column('aname', Text, nullable=True)
    name_de = Column('aname_de', Text, nullable=True)
    name_fr = Column('aname_fr', Text, nullable=True)
    name_it = Column('aname_it', Text, nullable=True)
    name_rm = Column('aname_rm', Text, nullable=True)
    name_en = Column('aname_en', Text, nullable=True)
    uid = Column('auid', String(12), nullable=True)
    line1 = Column('zeile1', String, nullable=True)
    line2 = Column('zeile2', String, nullable=True)
    street = Column('strasse', String, nullable=True)
    number = Column('hausnr', String, nullable=True)
    postal_code = Column('plz', Integer, nullable=True)
    city = Column('ort', String, nullable=True)

class Document(Base):
    """
    THE DOCUMENT
    This represents the main document in the whole system.

    Attributes:
        t_id (int): The identifier. This is used in the database only and must not be set manually.
                    If you  don't like it - don't care about.
        t_ili_tid (str): TID from the transfer file.
        document_type (str): The document type. It must be "Rechtsvorschrift", "GesetzlicheGrundlage"
            or "Hinweis".
        title (text): The multilingual title of his document.
                   Interlis type: LocalisationCH_V1.MultilingualText.
        title_de (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        title_fr (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        title_it (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        title_rm (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        title_en (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        abbreviation (text): The multilingual shortened version of the documents title.
                        Interlis type: LocalisationCH_V1.MultilingualText.
        abbreviation_de (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        abbreviation_fr (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        abbreviation_it (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        abbreviation_rm (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        abbreviation_en (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        official_number (text): The multilingual official number which uniquely identifies this document.
                                Interlis type: LocalisationCH_V1.MultilingualText.
        official_number_de (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        official_number_fr (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        official_number_it (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        official_number_rm (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        official_number_en (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        only_in_municipality (int): The fosnr (=id bfs) of the municipality. If this is None it is assumed
            the document is  related to the whole canton or even the confederation.
        index (int): An index used to sort the documents.
        law_status (str): The status switch if the document is legally approved or not.
        published_from (datetime.date): The date from when the document should be available for
            publishing in extracts. This  directly affects the behaviour of extract
            generation.
        published_until (datetime.date): The date until when the document should be available for
            publishing on extracts. This  directly affects the behaviour of extract
            generation.
        office_id (int): The foreign key to the office which is in charge for this document.
        responsible_office (pyramid_oereb.standard.models.railways_project_planning_zones.Office):
            The dedicated relation to the office instance from database.
    """
    __table_args__ = {'schema': app_schema_name}
    __tablename__ = 'dokument'
    t_id = Column(Integer, primary_key=True, autoincrement=False)
    t_ili_tid = Column(String, nullable=True)
    document_type = Column('type', String, nullable=False)
    title = Column('titel', Text, nullable=True)
    title_de = Column('titel_de', Text, nullable=True)
    title_fr = Column('titel_fr', Text, nullable=True)
    title_it = Column('titel_it', Text, nullable=True)
    title_rm = Column('titel_rm', Text, nullable=True)
    title_en = Column('titel_en', Text, nullable=True)
    abbreviation = Column('abkuerzung', Text, nullable=True)
    abbreviation_de = Column('abkuerzung_de', Text, nullable=True)
    abbreviation_fr = Column('abkuerzung_fr', Text, nullable=True)
    abbreviation_it = Column('abkuerzung_it', Text, nullable=True)
    abbreviation_rm = Column('abkuerzung_rm', Text, nullable=True)
    abbreviation_en = Column('abkuerzung_en', Text, nullable=True)
    official_number = Column('offiziellenr', Text, nullable=True)
    official_number_de = Column('offiziellenr_de', Text, nullable=True)
    official_number_fr = Column('offiziellenr_fr', Text, nullable=True)
    official_number_it = Column('offiziellenr_it', Text, nullable=True)
    official_number_rm = Column('offiziellenr_rm', Text, nullable=True)
    official_number_en = Column('offiziellenr_en', Text, nullable=True)
    only_in_municipality = Column('nuringemeinde', Integer, nullable=True)
    index = Column('auszugindex', Integer, nullable=False)
    law_status = Column('rechtsstatus', String, nullable=False)
    published_from = Column('publiziertab', Date, nullable=False)
    published_until = Column('publiziertbis', Date, nullable=True)
    office_id = Column(
        Integer,
        ForeignKey(Office.t_id),
        nullable=False
    )
    responsible_office = relationship(Office)

class ThemeDocument(Base):
    """
    Attributes:
        t_id (int): The identifier. This is used in the database only and must not be set manually.
                    If you  don't like it - don't care about.
        theme_id (int): The foreign key to the theme.
        document_id (int): The foreign key to the document.
        theme The dedicated relation to the theme instance from database.
        document The dedicated relation to the document instance from database.
    """
    __table_args__ = {'schema': app_schema_name}
    __tablename__ = 'themagesetz'
    t_id = Column(Integer, primary_key=True, autoincrement=False)
    theme_id = Column('thema', Integer, ForeignKey(Theme.t_id), nullable=False)
    document_id = Column('gesetz', Integer, ForeignKey(Document.t_id), nullable=False)
    theme = relationship(
        Theme,
        backref='legal_provisions'
    )
    document = relationship(
        Document
    )

class ArticleNumber(Base):
    """
    Attributes:
        t_id (int): The identifier. This is used in the database only and must not be set manually.
                    If you  don't like it - don't care about.
        value (str): Article number
        theme_id (int): The foreign key to the theme.
        theme_document_id (int): The foreign key to the ThemeDocument.
        theme_document The dedicated relation to the theme_document instance from database.
    """
    __table_args__ = {'schema': app_schema_name}
    __tablename__ = 'artikelnummer_'
    t_id = Column(Integer, primary_key=True, autoincrement=False)
    value = Column('avalue', String, nullable=False)
    theme_document_id = Column('themagesetz_artikelnr', 
                            Integer, 
                            ForeignKey(ThemeDocument.t_id),
                            nullable=False)
    theme_document = relationship(
        ThemeDocument,
        backref='article_numbers'
    )

class DocumentTypeText(Base):
    """
        t_id (int): The identifier. This is used in the database only and must not be set manually.
                    If you  don't like it - don't care about.
        code (str): according to enumeration
        title (text): The multilingual title of his document.
                    Interlis type: LocalisationCH_V1.MultilingualText.
        title_de (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        title_fr (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        title_it (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        title_rm (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        title_en (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
    """
    __table_args__ = {'schema': app_schema_name}
    __tablename__ = 'dokumenttyptxt'
    t_id = Column(Integer, primary_key=True, autoincrement=False)
    title = Column('titel', Text, nullable=True)
    title_de = Column('titel_de', Text, nullable=True)
    title_fr = Column('titel_fr', Text, nullable=True)
    title_it = Column('titel_it', Text, nullable=True)
    title_rm = Column('titel_rm', Text, nullable=True)
    title_en = Column('titel_en', Text, nullable=True)

class Logo(Base):
    """
    The container for all logos and municipality coat of arms

    Attributes:
        t_id (int): identifier, used in the database only
        code (str): The identifier given by a code
    """
    __table_args__ = {'schema': app_schema_name}
    __tablename__ = 'logo'
    t_id = Column(Integer, primary_key=True, autoincrement=False)
    code = Column(String, nullable=False)

class MultilingualBlob(Base):
    """
    Bucket to resolve entries related to OeREBKRM_V2_0.MultilingualBlob.

    Attributes:
        t_id (int): identifier, used in the database only
        document_id (int): The foreign key to the document this multilingual blob
                is related to.
        logo_id (int): The foreign key to the logo this multilingual blob
                is related to.
    """
    table_args__ = {'schema': app_schema_name}
    __tablename__ = 'multilingualblob'
    t_id = Column(Integer, primary_key=True, autoincrement=False)
    document_id = Column('dokument_dokument',
                    Integer, 
                    ForeignKey=Document.t_id,
                    nullable = True)
    logo_id = Column('logo_bild',
                    Integer, 
                    ForeignKey=Logo.t_id,
                    nullable = True)

class LocalisedBlob(Base):
    """
    Bucket to resolve entries related to OeREBKRM_V2_0.LocalisedBlob.

    Attributes:
        t_id (int): The identifier. This is used in the database only and must not be set manually. If
            you  don't like it - don't care about.
        language (str): Interlis: InternationalCodes_V1.LanguageCode_ISO639_1.
        blob (large binary): Interlis: BLACKBOX BINARY
        multilingualblob_id (int): The foreign key to the multilingual blob this localised blob
            is related to.
    """
    __table_args__ = {'schema': app_schema_name}
    __tablename__ = 'localisedblob'
    t_id = Column(Integer, primary_key=True, autoincrement=False)
    language = Column('alanguage', String, nullable=True)
    blob = Column('ablob', LargeBinary, nullable=False)
    multilingualblob_id = Column(
        'multilingualblob_localisedblob',
        Integer,
        ForeignKey(MultilingualBlob.t_id),
        nullable=True
    )

class Municipality(Base):
    """
    The municipality is the place where you hold the information about all the municipalities you are having
    in your canton. This is used also in the applications process to check whether a municipality is published
    or not.

    Attributes:
        fosnr (int): The identifier of the municipality. It is the commonly known id_bfs or as or
            nofs in the  french part.
        name (str): The Name of the municipality.
        published (bool): Switch whether a municipality is published or not. This has direct
            influence on extract  generation.
        geom (geoalchemy2.types.Geometry): The geometry of municipality borders. For type
            information see geoalchemy2_.  .. _geoalchemy2:
            https://geoalchemy-2.readthedocs.io/en/0.2.4/types.html  docs dependent on the
            configured type.  This concrete one is MULTIPOLYGON
    """
    __table_args__ = {'schema': app_schema_name}
    __tablename__ = 'municipality'
    fosnr = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String, nullable=False)
    published = Column(Boolean, nullable=False, default=False, server_default=text('FALSE'))
    geom = Column(Geometry('MULTIPOLYGON', srid=srid), nullable=True)


class RealEstate(Base):
    """
    The container where you can throw in all the real estates this application should have access to, for
    creating extracts.

    Attributes:
        id (int): The identifier. This is used in the database only and must not be set manually. If
            you  don't like it - don't care about.
        identdn (str): The identifier on cantonal level.
        number (str): The identifier on municipality level.
        egrid (str): The identifier on federal level (the all unique one...)
        type (str): The type of the real estate (This must base on DM01)
        canton (str): Which canton this real estate is situated in (use official shortened Version
            here. e.g. 'BE')
        municipality (str): The name of the municipality this real estate is situated in.
        subunit_of_land_register (str): The name of the maybe existing sub unit of land register if
            municipality in  combination with number does not offer a unique constraint.
            Else you can skip that.
        fosnr (int): The identifier of the municipality. It is the commonly known id_bfs.
        metadata_of_geographical_base_data (str): A link to the metadata which this geometry is
            based on which is  delivering a machine readable response format (XML).
        land_registry_area (str): The amount of the area of this real estate as it is declared in
            the land  registers information.
        limit (geoalchemy2.types.Geometry): The geometry of real estates border. For type
            information see geoalchemy2_.  .. _geoalchemy2:
            https://geoalchemy-2.readthedocs.io/en/0.2.4/types.html  docs dependent on the
            configured type.  This concrete one is MULTIPOLYGON
    """
    __table_args__ = {'schema': app_schema_name}
    __tablename__ = 'real_estate'
    id = Column(Integer, primary_key=True, autoincrement=False)
    identdn = Column(String, nullable=True)
    number = Column(String, nullable=True)
    egrid = Column(String, nullable=True)
    type = Column(String, nullable=False)
    canton = Column(String, nullable=False)
    municipality = Column(String, nullable=False)
    subunit_of_land_register = Column(String, nullable=True)
    fosnr = Column(Integer, nullable=False)
    metadata_of_geographical_base_data = Column(String, nullable=True)
    land_registry_area = Column(Integer, nullable=False)
    limit = Column(Geometry('MULTIPOLYGON', srid=srid))


class RealEstateType(Base):
    """
    The container where you can throw in all the real estates type texts this application
    should have access to, for creating extracts.

    Attributes:
        code (str): The identifier on federal level.
        text (str): The text for the multilingual text.
    """
    __table_args__ = {'schema': app_schema_name}
    __tablename__ = 'real_estate_type'
    code = Column(String, primary_key=True)
    text = Column(JSONType, nullable=False)


class Address(Base):
    """
    The bucket you can throw all addresses in the application should be able to use for the get egrid
    webservice. This is a bypass for the moment. In the end it seems ways more flexible to bind a service here
    but if you like you can use it.

    Attributes:
        street_name (unicode): The street name for this address.
        street_number (str): The house number of this address.
        zip_code (int): The ZIP code for this address.
        geom (geoalchemy2.types.Geometry): The geometry of real estates border. For type information
            see geoalchemy2_.  .. _geoalchemy2:
            https://geoalchemy-2.readthedocs.io/en/0.2.4/types.html  docs dependent on the
            configured type.  This concrete one is POINT
    """
    __table_args__ = (
        PrimaryKeyConstraint("street_name", "street_number", "zip_code"),
        {'schema': app_schema_name}
    )
    __tablename__ = 'address'
    street_name = Column(Unicode, nullable=False)
    street_number = Column(String, nullable=False)
    zip_code = Column(Integer, nullable=False, autoincrement=False)
    geom = Column(Geometry('POINT', srid=srid))


class Glossary(Base):
    """
    The bucket you can throw all items you want to have in the extracts glossary as reading help.

    Attributes:
        id (int): The identifier. This is used in the database only and must not be set manually. If
            you  don't like it - don't care about.
        title (str): The title or abbreviation of a glossary item.
        content (str): The description or definition of a glossary item.
    """
    __table_args__ = {'schema': app_schema_name}
    __tablename__ = 'glossar'
    id = Column(Integer, primary_key=True, autoincrement=False)
    title = Column(JSONType, nullable=False)
    content = Column(JSONType, nullable=False)


class ExclusionOfLiability(Base):
    """
    The bucket you can throw all addresses in the application should be able to use for the get egrid
    webservice. This is a bypass for the moment. In the end it seems ways more flexible to bind a service here
    but if you like you can use it.

    Attributes:
        id (int): The identifier. This is used in the database only and must not be set manually. If
            you  don't like it - don't care about.
        title (str): The title which the exclusion of liability item has.
        content (str): The content which the exclusion of liability item has.
    """
    __table_args__ = {'schema': app_schema_name}
    __tablename__ = 'exclusion_of_liability'
    id = Column(Integer, primary_key=True, autoincrement=False)
    title = Column(JSONType, nullable=False)
    content = Column(JSONType, nullable=False)


class LawStatus(Base):
    """
    The container where you can throw in all the law status texts this application
    should have access to, for creating extracts.
    Attributes:
        code (str): The identifier on federal level.
        text (JSONType): The text for the multilingual text.
    """
    __table_args__ = {'schema': app_schema_name}
    __tablename__ = 'law_status'
    code = Column(String, primary_key=True)
    text = Column(JSONType, nullable=False)


class DocumentTypeText(Base):
    """
    The element holding the different document types and their translations.

    Attributes:
        code (str): The identifier given by a code
        text (str): The display name for the document type
    """
    __table_args__ = {'schema': app_schema_name}
    __tablename__ = 'document_types'
    code = Column(String, primary_key=True)
    text = Column(JSONType, nullable=False)


class GeneralInformation(Base):
    """
    The bucket to store the general information about the OEREB cadastre

    Attributes:
        id (int): The identifier. This is used in the database only and must not be set manually. If
            you  don't like it - don't care about.
        title (dict): The title of the general information (multilingual)
        content (dict): The actual information (multilingual)
    """
    __table_args__ = {'schema': app_schema_name}
    __tablename__ = 'general_information'
    id = Column(Integer, primary_key=True, autoincrement=False)
    title = Column(JSONType, nullable=False)
    content = Column(JSONType, nullable=False)
