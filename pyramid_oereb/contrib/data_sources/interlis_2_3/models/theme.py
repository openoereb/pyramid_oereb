from sqlalchemy import Column, ForeignKey
from sqlalchemy import LargeBinary, String, Integer, Date, Text
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2.types import Geometry as GeoAlchemyGeometry
from sqlalchemy.orm import relationship


class Models(object):

    def __init__(self, office, document, view_service,
                 legend_entry, public_law_restriction, geometry,
                 public_law_restriction_document,
                 localised_blob, localised_uri, multilingual_blob, multilingual_uri,
                 base, db_connection, schema_name):

        self.Office = office
        self.Document = document
        self.ViewService = view_service
        self.LegendEntry = legend_entry
        self.PublicLawRestriction = public_law_restriction
        self.Geometry = geometry
        self.PublicLawRestrictionDocument = public_law_restriction_document
        self.LocalisedBlob = localised_blob
        self.LocalisedUri = localised_uri
        self.MultilingualBlob = multilingual_blob
        self.MultilingualUri = multilingual_uri
        self.Base = base
        self.db_connection = db_connection
        self.schema_name = schema_name


def generic_models(base, schema_name, pk_type):
    """
    Factory to produce a set of generic standard models.

    Args:
        base (): The SQLAlchemy base which is assigned to the models.
        schema_name (str): The name of the database schema where this models belong to.
        pk_type (sqlalchemy.sql.type_api.TypeEngine): The type of the primary column. E.g.
            sqlalchemy.String or sqlalchemy.Integer or another one fitting the underlying DB
            needs

    Returns:
        list: First element is the Office model and second is the Document model.
    """

    class Office(base):
        """
        The bucket to fill in all the offices you need to reference from public law restriction, document,
        geometry.

        Attributes:
            t_id (int): The identifier. This is used in the database only and must not be set manually.
                        If you  don't like it - don't care about.
            t_ili_tid (str): TID from the transfer file.
            name (text): The name of the office. Interlis type: LocalisationCH_V1.MultilingualText.
            name_de (text): Mapping of sources type: LocalisationCH_V1.MultilingualText.
            name_fr (text): Mapping of sources type: LocalisationCH_V1.MultilingualText.
            name_it (text): Mapping of sources type: LocalisationCH_V1.MultilingualText.
            name_rm (text): Mapping of sources type: LocalisationCH_V1.MultilingualText.
            name_en (text): Mapping of sources type: LocalisationCH_V1.MultilingualText.
            uid (str): The uid of this office from https
            line1 (str): The first address line for this office.
            line2 (str): The second address line for this office.
            street (str): The streets name of the offices address.
            number (str): The number on street.
            postal_code (int): The ZIP-code.
            city (str): The name of the city.
        """
        __table_args__ = {'schema': schema_name}
        __tablename__ = 'amt'
        t_id = Column(pk_type, primary_key=True, autoincrement=False)
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

    class Document(base):
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
            title_de (text): Mapping of sources type: LocalisationCH_V1.MultilingualText.
            title_fr (text): Mapping of sources type: LocalisationCH_V1.MultilingualText.
            title_it (text): Mapping of sources type: LocalisationCH_V1.MultilingualText.
            title_rm (text): Mapping of sources type: LocalisationCH_V1.MultilingualText.
            title_en (text): Mapping of sources type: LocalisationCH_V1.MultilingualText.
            abbreviation (text): The multilingual shortened version of the documents title.
                                Interlis type: LocalisationCH_V1.MultilingualText.
            abbreviation_de (text): Mapping of sources type: LocalisationCH_V1.MultilingualText.
            abbreviation_fr (text): Mapping of sources type: LocalisationCH_V1.MultilingualText.
            abbreviation_it (text): Mapping of sources type: LocalisationCH_V1.MultilingualText.
            abbreviation_rm (text): Mapping of sources type: LocalisationCH_V1.MultilingualText.
            abbreviation_en (text): Mapping of sources type: LocalisationCH_V1.MultilingualText.
            official_number (text): The multilingual official number which uniquely identifies this document.
                                    Interlis type: LocalisationCH_V1.MultilingualText.
            official_number_de (text): Mapping of sources type: LocalisationCH_V1.MultilingualText.
            official_number_fr (text): Mapping of sources type: LocalisationCH_V1.MultilingualText.
            official_number_it (text): Mapping of sources type: LocalisationCH_V1.MultilingualText.
            official_number_rm (text): Mapping of sources type: LocalisationCH_V1.MultilingualText.
            official_number_en (text): Mapping of sources type: LocalisationCH_V1.MultilingualText.
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
        __table_args__ = {'schema': schema_name}
        __tablename__ = 'dokument'
        t_id = Column(pk_type, primary_key=True, autoincrement=False)
        t_ili_tid = Column(String, nullable=True)
        document_type = Column('typ', String, nullable=False)
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
            'zustaendigestelle',
            ForeignKey(Office.t_id),
            nullable=False
        )
        responsible_office = relationship(Office)

    return [Office, Document]


def model_factory(schema_name, pk_type, srid, db_connection):
    """
    Factory to produce a set of standard models.

    Args:
        schema_name (str): The name of the database schema where this models belong to.
        pk_type (sqlalchemy.sql.type_api.TypeEngine): The type of the primary column. E.g.
            sqlalchemy.String or sqlalchemy.Integer or another one fitting the underlying DB
            needs
        geometry_type (str): The geoalchemy geometry type defined as well known string.
        srid (int): The SRID defining the projection of the geometries stored in standard db schema.

    Returns:
        Models: the produced set of standard models

    """
    Base = declarative_base()

    Office, Document = generic_models(Base, schema_name, pk_type)

    class ViewService(Base):
        """
        A view service aka WM(T)S which can deliver a cartographic representation via web.

        Attributes:
            t_id (int): The identifier. This is used in the database only and must not be set manually. If
                you  don't like it - don't care about.
        """
        __table_args__ = {'schema': schema_name}
        __tablename__ = 'darstellungsdienst'
        t_id = Column(pk_type, primary_key=True, autoincrement=False)

    class LegendEntry(Base):
        """
        A class based legend system which is directly related to
        :class:`pyramid_oereb.standard.models.land_use_plans.ViewService`.

        Attributes:
            t_id (int): The identifier. This is used in the database only and must not be set manually. If
                you  don't like it - don't care about.
            symbol (str): An image with represents the legend entry. This can be png or svg. It is string
                but BaseCode64  encoded.
            legend_text (dict): Multilingual text to describe this legend entry.
            legend_text_de (text): Mapping of sources type: LocalisationCH_V1.MultilingualText.
            legend_text_fr (text): Mapping of sources type: LocalisationCH_V1.MultilingualText.
            legend_text_it (text): Mapping of sources type: LocalisationCH_V1.MultilingualText.
            legend_text_rm (text): Mapping of sources type: LocalisationCH_V1.MultilingualText.
            legend_text_en (text): Mapping of sources type: LocalisationCH_V1.MultilingualText.

            type_code (str): Type code of the public law restriction which is represented by this legend
                entry.
            type_code_list (str): List of all public law restrictions which are described through this
                legend  entry.
            theme (str): Statement to describe to which public law restriction this legend entry
                belongs.
            sub_theme (dict): Multilingual description for sub topics this legend entry might belonging to.
            view_service_id (str): The foreign key to the view service this legend entry is related to.
            view_service (pyramid_oereb.standard.models.land_use_plans.ViewService):
                The dedicated relation to the view service instance from database.
        """
        __table_args__ = {'schema': schema_name}
        __tablename__ = 'legendeeintrag'
        t_id = Column(pk_type, primary_key=True, autoincrement=False)
        symbol = Column(LargeBinary, nullable=False)
        legend_text = Column('legendetext', Text, nullable=True)
        legend_text_de = Column('legendetext_de', Text, nullable=True)
        legend_text_fr = Column('legendetext_fr', Text, nullable=True)
        legend_text_it = Column('legendetext_it', Text, nullable=True)
        legend_text_rm = Column('legendetext_rm', Text, nullable=True)
        legend_text_en = Column('legendetext_en', Text, nullable=True)
        type_code = Column('artcode', String(40), nullable=False)
        type_code_list = Column('artcodeliste', String, nullable=False)
        theme = Column('thema', String, nullable=False)
        sub_theme = Column('subthema', String, nullable=True)
        view_service_id = Column(
            'darstellungsdienst',
            ForeignKey(ViewService.t_id),
            nullable=False
        )
        view_service = relationship(ViewService, backref='legends')

    class PublicLawRestriction(Base):
        """
        The container where you can fill in all your public law restrictions to the topic.

        Attributes:
            t_id (int): The identifier. This is used in the database only and must not be set manually. If
                you  don't like it - don't care about.
            law_status (str): The status switch if the document is legally approved or not.
            published_from (datetime.date): The date when the document should be available for
                publishing on extracts. This  directly affects the behaviour of extract
                generation.
            published_until (datetime.date): The date starting from which the document should not be
                published anymore on extracts. This directly affects the behaviour of extract generation.
            view_service_id (int): The foreign key to the view service this public law restriction is
                related to.
            view_service (pyramid_oereb.standard.models.land_use_plans.ViewService):
                The dedicated relation to the view service instance from database.
            legend_entry_id (int): The foreign key to the legend entry this public law restriction is
                related to.
            legend_entry (pyramid_oereb.standard.models.airports_building_lines.LegendEntry):
                The dedicated relation to the legend entry instance from database.
            office_id (int): The foreign key to the office which is responsible to this public law
                restriction.
            responsible_office (pyramid_oereb.standard.models.land_use_plans.Office):
                The dedicated relation to the office instance from database.
        """
        __table_args__ = {'schema': schema_name}
        __tablename__ = 'eigentumsbeschraenkung'
        t_id = Column(pk_type, primary_key=True, autoincrement=False)
        law_status = Column('rechtsstatus', String, nullable=False)
        published_from = Column('publiziertab', Date, nullable=False)
        published_until = Column('publiziertbis', Date, nullable=True)
        view_service_id = Column(
            'darstellungsdienst',
            ForeignKey(ViewService.t_id),
            nullable=False
        )
        view_service = relationship(
            'ViewService',
            backref='public_law_restrictions'
        )
        legend_entry_id = Column(
            'legende',
            ForeignKey(LegendEntry.t_id),
            nullable=False
        )
        legend_entry = relationship(
            'LegendEntry',
            backref='public_law_restrictions')
        office_id = Column(
            'zustaendigestelle',
            ForeignKey(Office.t_id),
            nullable=False
        )
        responsible_office = relationship(Office)

    class Geometry(Base):
        """
        The dedicated model for all geometries in relation to their public law restriction.

        Attributes:
            t_id (int): The identifier. This is used in the database only and must not be set manually. If
                you  don't like it - don't care about.
            point (geoalchemy2.types.Geometry): Interlis type: GeometryCHLV95_V1.Coord2
            line (geoalchemy2.types.Geometry): Interlis type: GeometryCHLV95_V1.Line
            surface (geoalchemy2.types.Geometry): Interlis type: GeometryCHLV95_V1.Surface
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
                is related to.
            public_law_restriction (pyramid_oereb.standard.models.land_use_plans
                .PublicLawRestriction): The dedicated relation to the public law restriction instance from
                database.
        """
        __table_args__ = {'schema': schema_name}
        __tablename__ = 'geometrie'
        t_id = Column(pk_type, primary_key=True, autoincrement=False)
        point = Column('punkt', GeoAlchemyGeometry('POINT', srid=srid), nullable=True)
        line = Column('linie', GeoAlchemyGeometry('LINESTRING', srid=srid), nullable=True)
        surface = Column('flaeche', GeoAlchemyGeometry('POLYGON', srid=srid), nullable=True)
        law_status = Column('rechtsstatus', String, nullable=False)
        published_from = Column('publiziertab', Date, nullable=False)
        published_until = Column('publiziertbis', Date, nullable=True)
        geo_metadata = Column('metadatengeobasisdaten', String, nullable=True)
        public_law_restriction_id = Column(
            'eigentumsbeschraenkung',
            ForeignKey(PublicLawRestriction.t_id),
            nullable=False
        )
        public_law_restriction = relationship(
            PublicLawRestriction,
            backref='geometries'
        )

    class MultilingualUri(Base):
        """
        Bucket to resolve entries related to OeREBKRM_V2_0.MultilingualUri.

        Attributes:
            t_id (int): The identifier. This is used in the database only and must not be set manually. If
                you  don't like it - don't care about.
            t_seq (int): Order of the structure elements.
            language (str): Interlis: InternationalCodes_V1.LanguageCode_ISO639_1.
            text (str): Interlis: URI.
            office_id (int): The foreign key to the office this multilingual uri
                is related to.
            document_id (int): The foreign key to the document this multilingual uri
                is related to.
            view_service_id (int): The foreign key to the view service this multilingual uri
                is related to.
        """
        __table_args__ = {'schema': schema_name}
        __tablename__ = 'multilingualuri'
        t_id = Column(pk_type, primary_key=True, autoincrement=False)
        t_seq = Column(Integer, nullable=True)
        office_id = Column(
            'amt_amtimweb',
            ForeignKey(Office.t_id),
            nullable=True
        )
        document_id = Column(
            'dokument_textimweb',
            ForeignKey(Document.t_id),
            nullable=True
        )
        view_service_id = Column(
            'darstellungsdienst_verweiswms',
            ForeignKey(ViewService.t_id),
            nullable=True
        )
        office = relationship(
            'Office',
            backref='multilingual_uri'
        )
        document = relationship(
            'Document',
            backref='multilingual_uri'
        )
        view_service = relationship(
            'ViewService',
            backref='multilingual_uri'
        )

    class MultilingualBlob(Base):
        """
        Bucket to resolve entries related to OeREBKRM_V2_0.MultilingualBlob.

        Attributes:
            t_id (int): The identifier. This is used in the database only and must not be set manually. If
                you  don't like it - don't care about.
            t_seq (int): Order of the structure elements.
            document_id (int): The foreign key to the document this multilingual uri
                is related to.
        """
        __table_args__ = {'schema': schema_name}
        __tablename__ = 'multilingualblob'
        t_id = Column(pk_type, primary_key=True, autoincrement=False)
        t_seq = Column(Integer, nullable=True)
        document_id = Column(
            'dokument_dokument',
            ForeignKey(Document.t_id),
            nullable=True
        )

    class LocalisedUri(Base):
        """
        Bucket to resolve entries related to OeREBKRM_V2_0.LocalisedUri.

        Attributes:
            t_id (int): The identifier. This is used in the database only and must not be set manually. If
                you  don't like it - don't care about.
            t_seq (int): Order of the structure elements.
            language (str): Interlis: InternationalCodes_V1.LanguageCode_ISO639_1.
            text (str): Interlis: URI.
            multilingualuri_id (int): The foreign key to the multilingual uri this localised uri
                is related to.
        """
        __table_args__ = {'schema': schema_name}
        __tablename__ = 'localiseduri'
        t_id = Column(pk_type, primary_key=True, autoincrement=False)
        t_seq = Column(Integer, nullable=True)
        language = Column('alanguage', String, nullable=True)
        text = Column('atext', String, nullable=False)
        multilingualuri_id = Column(
            'multilingualuri_localisedtext',
            ForeignKey(MultilingualUri.t_id),
            nullable=False
        )
        multilingualuri = relationship(
            'MultilingualUri',
            backref='localised_uri'
        )

    class LocalisedBlob(Base):
        """
        Bucket to resolve entries related to OeREBKRM_V2_0.LocalisedBlob.

        Attributes:
            t_id (int): The identifier. This is used in the database only and must not be set manually. If
                you  don't like it - don't care about.
            t_seq (int): Order of the structure elements.
            language (str): Interlis: InternationalCodes_V1.LanguageCode_ISO639_1.
            text (str): Interlis: URI.
            multilingualblob_id (int): The foreign key to the multilingual blob this localised blob
                is related to.
        """
        __table_args__ = {'schema': schema_name}
        __tablename__ = 'localisedblob'
        t_id = Column(pk_type, primary_key=True, autoincrement=False)
        language = Column('alanguage', String, nullable=True)
        blob = Column('ablob', LargeBinary, nullable=False)
        multilingualblob_id = Column(
            'multilingualblob_localisedblob',
            ForeignKey(MultilingualBlob.t_id),
            nullable=True
        )
        multilingualblob = relationship(
            'MultilingualBlob',
            backref='localised_uri'
        )

    class PublicLawRestrictionDocument(Base):
        """
        Meta bucket (join table) for the relationship between public law restrictions and documents.

        Attributes:
            t_id (int): The identifier. This is used in the database only and must not be set manually. If
                you  don't like it - don't care about.
            public_law_restriction_id (int): The foreign key to the public law restriction which has
                relation to  a document.
            document_id (int): The foreign key to the document which has relation to the public law
                restriction.
            plr (pyramid_oereb.standard.models.land_use_plans.PublicLawRestriction):
                The dedicated relation to the public law restriction instance from database.
            document (pyramid_oereb.standard.models.land_use_plans.DocumentBase):
                The dedicated relation to the document instance from database.
        """
        __table_args__ = {'schema': schema_name}
        __tablename__ = 'hinweisvorschrift'
        t_id = Column(pk_type, primary_key=True, autoincrement=False)
        public_law_restriction_id = Column(
            'eigentumsbeschraenkung',
            ForeignKey(PublicLawRestriction.t_id),
            nullable=False
        )
        document_id = Column(
            'vorschrift',
            ForeignKey(Document.t_id),
            nullable=False
        )
        plr = relationship(
            PublicLawRestriction,
            backref='legal_provisions'
        )
        document = relationship(
            Document
        )

    return Models(
        Office, Document, ViewService,
        LegendEntry, PublicLawRestriction, Geometry, PublicLawRestrictionDocument,
        LocalisedBlob, LocalisedUri, MultilingualBlob, MultilingualUri,
        Base, db_connection, schema_name
    )


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
    if geometry_type is not None:
        geometry_type = None
    return model_factory(schema_name, Integer, srid, db_connection)
