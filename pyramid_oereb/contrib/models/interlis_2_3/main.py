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
from pyramid_oereb.contrib.models.interlis_2_3.theme import generic_models
from pyramid_oereb.standard.models.main import generic_models_main
from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy import String, Integer, LargeBinary, Date, DateTime, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from pyramid_oereb.lib.config import Config

Base = declarative_base()
app_schema_name = Config.get('app_schema').get('name')
srid = Config.get('srid')

Office, Document = generic_models(Base, app_schema_name, Integer)
RealEstate, Municipality, Address = generic_models_main(Base, app_schema_name)


class Theme(Base):
    """
    The OEREB themes of the application

    Attributes:
        t_id (int): identifier, used in the database only
        code (str): OEREB code of the theme - unique and used to link each PublicLawRestriction
            with the corresponding theme
        sub_code (str): OEREB code of the theme - unique and used to link each PublicLawRestriction
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
    code = Column('acode', String, nullable=False)
    sub_code = Column(String, nullable=True)
    title = Column('titel', Text, nullable=True)
    title_de = Column('titel_de', Text, nullable=True)
    title_fr = Column('titel_fr', Text, nullable=True)
    title_it = Column('titel_it', Text, nullable=True)
    title_rm = Column('titel_rm', Text, nullable=True)
    title_en = Column('titel_en', Text, nullable=True)
    extract_index = Column('auszugindex', Integer, nullable=False)

    UniqueConstraint(code, sub_code)


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
        code (str): The identifier given by a code
        title (text): The display name for the document type.
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
    code = Column('acode', String, nullable=False)
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
    code = Column('acode', String, nullable=False)


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
                         ForeignKey(Document.t_id),
                         nullable=True)
    logo_id = Column('logo_bild',
                     Integer,
                     ForeignKey(Logo.t_id),
                     nullable=True)
    document = relationship(
            'Document',
            backref='multilingual_blob'
    )
    logo = relationship(
            'Logo',
            backref='multilingual_blob'
    )


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


class RealEstateType(Base):
    """
    The container where you can throw in all the real estates type texts this application
    should have access to, for creating extracts.

    Attributes:
        t_id (int) The identifier. This is used in the database only and must not be set manually. If
            you  don't like it - don't care about.
        code (str): The identifier on federal level.
        title (str): The text for the multilingual text.
        title_de (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        title_fr (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        title_it (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        title_rm (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        title_en (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
    """
    __table_args__ = {'schema': app_schema_name}
    __tablename__ = 'grundstuecksarttxt'
    id = Column(Integer, primary_key=True, autoincrement=False)
    code = Column('acode', String, nullable=False)
    title = Column('titel', Text, nullable=True)
    title_de = Column('titel_de', Text, nullable=True)
    title_fr = Column('titel_fr', Text, nullable=True)
    title_it = Column('titel_it', Text, nullable=True)
    title_rm = Column('titel_rm', Text, nullable=True)
    title_en = Column('titel_en', Text, nullable=True)


class Glossary(Base):
    """
    The bucket you can throw all items you want to have in the extracts glossary as reading help.

    Attributes:
        t_id (int): The identifier. This is used in the database only and must not be set manually. If
            you  don't like it - don't care about.
        title (str): The title or abbreviation of a glossary item.
        title_de (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        title_fr (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        title_it (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        title_rm (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        title_en (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        content (str): The description or definition of a glossary item.
        content_de (text): Mapping of interlis type: LocalisationCH_V1.MultilingualMText.
        content_fr (text): Mapping of interlis type: LocalisationCH_V1.MultilingualMText.
        content_it (text): Mapping of interlis type: LocalisationCH_V1.MultilingualMText.
        content_rm (text): Mapping of interlis type: LocalisationCH_V1.MultilingualMText.
        content_en (text): Mapping of interlis type: LocalisationCH_V1.MultilingualMText.
    """
    __table_args__ = {'schema': app_schema_name}
    __tablename__ = 'glossar'
    t_id = Column(Integer, primary_key=True, autoincrement=False)
    title = Column('titel', Text, nullable=True)
    title_de = Column('titel_de', Text, nullable=True)
    title_fr = Column('titel_fr', Text, nullable=True)
    title_it = Column('titel_it', Text, nullable=True)
    title_rm = Column('titel_rm', Text, nullable=True)
    title_en = Column('titel_en', Text, nullable=True)
    content = Column('inhalt', Text, nullable=True)
    content_de = Column('inhalt_de', Text, nullable=True)
    congent_fr = Column('inhalt_fr', Text, nullable=True)
    content_it = Column('inhalt_it', Text, nullable=True)
    content_rm = Column('inhalt_rm', Text, nullable=True)
    content_en = Column('inhalt_en', Text, nullable=True)


class ExclusionOfLiability(Base):
    """
    The bucket you can throw all addresses in the application should be able to use for the get egrid
    webservice. This is a bypass for the moment. In the end it seems ways more flexible to bind a service here
    but if you like you can use it.

    Attributes:
        t_id (int) The identifier. This is used in the database only and must not be set manually. If
            you  don't like it - don't care about.
        title (str): The title which the exclusion of liability item has.
        title_de (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        title_fr (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        title_it (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        title_rm (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        title_en (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        content (str): The content which the exclusion of liability item has.
        content_de (text): Mapping of interlis type: LocalisationCH_V1.MultilingualMText.
        content_fr (text): Mapping of interlis type: LocalisationCH_V1.MultilingualMText.
        content_it (text): Mapping of interlis type: LocalisationCH_V1.MultilingualMText.
        content_rm (text): Mapping of interlis type: LocalisationCH_V1.MultilingualMText.
        content_en (text): Mapping of interlis type: LocalisationCH_V1.MultilingualMText.
        extract_index (int): index to sort the information in the extract, defined in the specification.
    """
    __table_args__ = {'schema': app_schema_name}
    __tablename__ = 'haftungshinweis'
    id = Column(Integer, primary_key=True, autoincrement=False)
    title = Column('titel', Text, nullable=True)
    title_de = Column('titel_de', Text, nullable=True)
    title_fr = Column('titel_fr', Text, nullable=True)
    title_it = Column('titel_it', Text, nullable=True)
    title_rm = Column('titel_rm', Text, nullable=True)
    title_en = Column('titel_en', Text, nullable=True)
    content = Column('inhalt', Text, nullable=True)
    content_de = Column('inhalt_de', Text, nullable=True)
    content_fr = Column('inhalt_fr', Text, nullable=True)
    content_it = Column('inhalt_it', Text, nullable=True)
    content_rm = Column('inhalt_rm', Text, nullable=True)
    content_en = Column('inhalt_en', Text, nullable=True)
    extract_index = Column('auszugindex', Integer, nullable=False)


class LawStatus(Base):
    """
    The container where you can throw in all the law status texts this application
    should have access to, for creating extracts.
    Attributes:
        t_id (int): The identifier. This is used in the database only and must not be set manually. If
            you  don't like it - don't care about.
        code (str): The identifier on federal level.
        title (str): The text for the multilingual text.
        title_de (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        title_fr (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        title_it (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        title_rm (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        title_en (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
    """
    __table_args__ = {'schema': app_schema_name}
    __tablename__ = 'rechtsstatustxt'
    id = Column(Integer, primary_key=True, autoincrement=False)
    code = Column('acode', String, nullable=False)
    title = Column('titel', Text, nullable=True)
    title_de = Column('titel_de', Text, nullable=True)
    title_fr = Column('titel_fr', Text, nullable=True)
    title_it = Column('titel_it', Text, nullable=True)
    title_rm = Column('titel_rm', Text, nullable=True)
    title_en = Column('titel_en', Text, nullable=True)


class GeneralInformation(Base):
    """
    The bucket to store the general information about the OEREB cadastre

    Attributes:
        t_id (int): The identifier. This is used in the database only and must not be set manually. If
            you  don't like it - don't care about.
        title (dict): The title of the general information (multilingual)
        title_de (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        title_fr (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        title_it (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        title_rm (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        title_en (text): Mapping of interlis type: LocalisationCH_V1.MultilingualText.
        content (dict): The actual information (multilingual)
        content_de (text): Mapping of interlis type: LocalisationCH_V1.MultilingualMText.
        content_fr (text): Mapping of interlis type: LocalisationCH_V1.MultilingualMText.
        content_it (text): Mapping of interlis type: LocalisationCH_V1.MultilingualMText.
        content_rm (text): Mapping of interlis type: LocalisationCH_V1.MultilingualMText.
        content_en (text): Mapping of interlis type: LocalisationCH_V1.MultilingualMText.
        extract_index (int): index to sort the information in the extract, defined in the specification
    """
    __table_args__ = {'schema': app_schema_name}
    __tablename__ = 'information'
    id = Column(Integer, primary_key=True, autoincrement=False)
    title = Column('titel', Text, nullable=True)
    title_de = Column('titel_de', Text, nullable=True)
    title_fr = Column('titel_fr', Text, nullable=True)
    title_it = Column('titel_it', Text, nullable=True)
    title_rm = Column('titel_rm', Text, nullable=True)
    title_en = Column('titel_en', Text, nullable=True)
    content = Column('inhalt', Text, nullable=True)
    content_de = Column('inhalt_de', Text, nullable=True)
    content_fr = Column('inhalt_fr', Text, nullable=True)
    content_it = Column('inhalt_it', Text, nullable=True)
    content_rm = Column('inhalt_rm', Text, nullable=True)
    content_en = Column('inhalt_en', Text, nullable=True)
    extract_index = Column('auszugindex', Integer, nullable=False)


class DataIntegration(Base):
    """
    The bucket to fill in the date when this whole schema was updated. It has a relation to the
    office to be able to find out who was the delivering instance.
    Attributes:
        t_id (str): The identifier. This is used in the database only and must not be set manually. If
            you  don't like it - don't care about.
        date (datetime.date): The date when this data set was delivered.
        dataset_identifier (str): BasketId or filename or complete WFS request
    """
    __table_args__ = {'schema': app_schema_name}
    __tablename__ = 'datenaufnahme'
    t_id = Column(Integer, primary_key=True, autoincrement=False)
    date = Column('datum', Date, nullable=False)
    dataset_identifier = Column('datensatzidentifikation', String, nullable=False)


class MunicipalityWithPLR(Base):
    """
    t_id (str): The identifier. This is used in the database only and must not be set manually. If
        you  don't like it - don't care about.
    municipality (int): FSO number
    basic_data_status (date): status of basic data
    basic_data_metadata (str): metadata of basic data
    subunit_cadastral_register (str): descriptor of the subunit of the cadastral register
    """
    table_args__ = {'schema': app_schema_name}
    __tablename__ = 'gemeindemitoerebk'
    t_id = Column(Integer, primary_key=True, autoincrement=False)
    municipality = Column(Integer, nullable=False)
    basic_data_status = Column(DateTime, nullable=True)
    basic_data_metadata = Column(String, nullable=True)
    subunit_cadastral_register = Column(String, nullable=True)


class CadastralRegisterDistrict(Base):
    """
    id (str): The identifier. This is used in the database only and must not be set manually. If
        you  don't like it - don't care about.
    canton (str): Canton
    municipality (int): FSO number
    nbident (str): NBIdent according to surveying data
    name (str): Name of the cadastral register district
    egris_subdistrict (str): sub-district according to cadastral register
    egris_lot (str): lot according to cadastral register
    """
    table_args__ = {'schema': app_schema_name}
    __tablename__ = 'grundbuchkreis'
    t_id = Column(Integer, primary_key=True, autoincrement=False)
    canton = Column(String, nullable=False)
    municipality = Column(Integer, nullable=False)
    nbident = Column(String, nullable=False)
    name = Column('aname', String, nullable=False)
    egris_subdistrict = Column('egris_subkreis', String, nullable=True)
    egris_los = Column('egris_los', String, nullable=True)


class MapLayering(Base):
    """
    id (str): The identifier. This is used in the database only and must not be set manually. If
        you  don't like it - don't care about.
    view_service (str): Darstellungsdienst
    layer_index (int): Index for sorting the layering of the view services for a theme
    layer_opacity (str): Deckkraft eines Darstellungsdienstes
    """
    table_args__ = {'schema': app_schema_name}
    __tablename__ = 'maplayering'
    t_id = Column(Integer, primary_key=True, autoincrement=False)
    view_service = Column('verweiswms', String, nullable=False)
    layer_index = Column('layerindex', Integer, nullable=False)
    layer_opacity = Column('layerdeckkraft', Float, nullable=False)


class ThemeRef(Base):
    """
    id (str): The identifier. This is used in the database only and must not be set manually. If
        you  don't like it - don't care about.
    code (str): OEREB code of the theme - unique and used to link each PublicLawRestriction
        with the corresponding theme
    subcode (str): OEREB code of the theme - unique and used to link each PublicLawRestriction
        with the corresponding subtheme
    municipality_with_plr_id (int): The foreign key to the related municipality with PLR
    """
    table_args__ = {'schema': app_schema_name}
    __tablename__ = 'themaref'
    t_id = Column(Integer, primary_key=True, autoincrement=False)
    code = Column('thema', String, nullable=False)
    subcode = Column('subthema', String, nullable=True)
    municipality_with_plr_id = Column('gemeindemitoerebk_themen',
                                      Integer,
                                      ForeignKey(MunicipalityWithPLR.t_id),
                                      nullable=False)
    municipality_with_plr = relationship(
                                'MunicipalityWithPLR',
                                backref='municipality_with_plr_themes'
    )
