.. _changes:

Changes/Hints for migration
===========================

This section will give you hints how to handle version migration. Since the project moves forward it will
introduce differences in the yml configuration file. So it would not be enough to simply install the newest
version. Often a version upgrade changes or adds parameters which are used.

Version 1.3.0
-------------

This version introduces an import facility for **federal data**. To support this, a new database attribute
was needed, you therefore need to apply some changes to your project if you have been using
:ref:`changes-version-1.2.3` or earlier.

Configuration
^^^^^^^^^^^^^
Add a download link in each oereb theme where you want to use the download script.
See the pyramid_oereb standard configuration file for an example. Or read optional installation hints chapter
:ref:`installation-step-sample-data`.

Models
^^^^^^
If you have custom models (for example, for oereblex), you need to add an attribute ``checksum`` of type
String to these (in class definition of *DataIntegration* model). Alternatively, you can recreate your models
using the standard scripts. This will solve it for you.

Database
^^^^^^^^
New column ``checksum`` in all oereb theme *DataIntegration* tables.

.. _changes-version-1.2.3:

Version 1.2.3
-------------

The version 1.2.3 fixes a print template bug present in :ref:`changes-version-1.2.2`. You do not need to change your configuration
or schema.

.. _changes-version-1.2.2:

Version 1.2.2
-------------

The version 1.2.2 is a bug-fix release for :ref:`changes-version-1.2.1`. You do not need to change your configuration
or schema. However, you may wish to use the new optional configuration parameter ``type_mapping`` within
``real_estate``, as this allows you to define the texts to be used for the types in the configuration, instead of
needing to have them in the data.

.. _changes-version-1.2.1:

Version 1.2.1
-------------

The version 1.2.1 is the first stable version that implements the new federal specification (published november 2017).
Because this specification contains some new attributes (including mandatory attributes), and some renaming
of attributes as compared to the previous version of the specification (implemented by pyramid_oereb
in :ref:`changes-version-1.1.0`), you need to adapt your configuration and your models if you have used the previous version.

.. _changes-new-config-options-1.2.1:

New configuration options in yml
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

These are the new configuration options for your project (yml file):

* within the ``plan_for_land_register`` section:

  * ``layer_index``
  * ``layer_opacity``

* ``plan_for_land_register_main_page``: new section, content like ``plan_for_land_register``

* within the ``extract`` section:

  * ``certification`` (replaces certificationText)
  * ``certification_at_web``

* within each theme, in the ``view_service`` section:

  * ``layer_index``
  * ``layer_opacity``

* within the ``print`` section:

  * ``furtherInformationText`` was removed. This information is not existing any longer regarding to changed
    federal specification for the static extract.

See the `pyramid_oereb_standard yml template <https://github.com/pyramidoereb/pyramid_oereb/blob/v1.2.1/pyramid_oereb/standard/pyramid_oereb.yml.mako>`__
for the correct style of the configuration and an explanation of the new attributes.

.. _changes-new-config-mapfish-print-1.2.1:

MapFish Print
"""""""""""""

These are the new configuration options for the printing of your extracts:

* ``display_real_estate_subunit_of_land_register``: flag whether to display the RealEstate_SubunitOfLandRegister (Grundbuchkreis)
  in the pdf extract or not

See the ``print`` section at this place in the
`pyramid_oereb_standard yml template <https://github.com/pyramidoereb/pyramid_oereb/blob/v1.2.1/pyramid_oereb/standard/pyramid_oereb.yml.mako#L65>`__
for the correct style of the configuration.

Database
^^^^^^^^

In the standard database schema, the following has changed:

* Primary keys in the standard tables are now of type ``VARCHAR`` (not ``INTEGER``). Foreign key types need to be adapted accordingly as well.
* In the ``document`` table of each theme (i.e. ``land_use_plans`` scheme etc.), new attribute ``document_type``.
* The ``document_type`` replaces the table ``legal_provision`` for each theme (i.e. ``land_use_plans`` scheme etc.), which no longer exists.

.. _changes-version-1.1.0:

Version 1.1.0
-------------

The stable version 1.1.0 contains a lot of changes. It can be counted as the first version to be used in
production mode. When you are updating from previous version to 1.1.0 you will have to adjust your yml file.
Description below will try to classify new options whether they are *optional* or **mandatory** to use the
new version.
Of course you also could use the way described in the ``installation-step-configuration``. But then it will
create a completely new yml but valid file. In order to do that its up to your decision: Migrate new options
to your existing configuration or migrate your custom configuration into a newly created file.

Here is a list of features this version additionally implements compared to
`1.0.1 <https://github.com/pyramidoereb/pyramid_oereb/releases/tag/v1.0.1>`__:

.. _changes-oereb-lex:

OEREBlex
^^^^^^^^

This version includes binding/adapter to oereb lex. The code can be found
`here <https://github.com/pyramidoereb/pyramid_oereb/blob/v1.1.0/pyramid_oereb/contrib/sources/plr_oereblex.py>`__.
This should enable you to use OEREBlex with a minimum of configuration.
See :ref:`changes-new-config-oereb-lex` for further details of configuration options.

The idea of this oereb lex adapter is to access OEREBlex documents directly via API provided by OEREBlex.
You can configure this per theme. If you have a theme which has all documents stored in OEREBlex you
will need a link to the dedicated set of documents for every public law restriction in this theme. You will
end up with an attribute in the database table for your public law restriction which contains the link.

.. note:: OREBlex uses unique ids for the document sets. To prevent from storing redundant data and for
    simplifying things we decided to not store the complete link in database attribute but the id only!

Regarding to the note above we assume you have stored the correct id of your OEREBlex document set per public
law restriction in your database table.

The next step is to define the sqlalchemy mappings. This works like normal mapping definition described here:
:ref:`configuration-adapt-models`. The difference to the standard database configuration is here:

- All document related model classes are obsolete.
- The public law restriction class gets an attribute which is called geolink.
- Since all document related mapping can be ignored the mapping is slightly shorter than standard mapping.

Below you can find an example mapping.

.. note:: Have a detailed look at the PublicLawRestriction class and its attribute geolink. The name geolink
    must exist in the class to be able to use the prepared OEREBlex adapter. If you use different name in
    your database you can map it the known way:

    `geolink = sa.Column('meine_eigene_spaltenbezeichnung', sa.Integer, nullable=True)`

.. code-block:: python

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
        Attributes:
            fosnr (int): The identifier of the municipality in your system (id_bfs = fosnr)
            available (bool): The switch field to configure if this plr is available for the
                municipality or not.  This field has direct influence on the applications
                behaviour. See documentation for more info.
        """
        __table_args__ = {'schema': 'land_use_plans'}
        __tablename__ = 'availability'
        fosnr = sa.Column(sa.Integer, primary_key=True)
        available = sa.Column(sa.Boolean, nullable=False, default=False)


    class Office(Base):
        """
        The bucket to fill in all the offices you need to reference from public law restriction, document,
        geometry.
        Attributes:
            id (int): The identifier. This is used in the database only and must not be set manually. If
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
        __table_args__ = {'schema': 'land_use_plans'}
        __tablename__ = 'office'
        id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
        name = sa.Column(sa.String, nullable=False)
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
            id (int): The identifier. This is used in the database only and must not be set manually. If
                you  don't like it - don't care about.
            date (datetime.date): The date when this data set was delivered.
            office_id (int): A foreign key which points to the actual office instance.
            office (oereb_server.models.land_use_plans.Office):
                The actual office instance which the id points to.
        """
        __table_args__ = {'schema': 'land_use_plans'}
        __tablename__ = 'data_integration'
        id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
        date = sa.Column(sa.DateTime, nullable=False)
        office_id = sa.Column(sa.Integer, sa.ForeignKey(Office.id), nullable=False)
        office = relationship(Office)


    class ViewService(Base):
        """
        A view service aka WM(T)S which can deliver a cartographic representation via web.
        Attributes:
            id (int): The identifier. This is used in the database only and must not be set manually. If
                you  don't like it - don't care about.
            reference_wms (str): The actual url which leads to the desired cartographic representation.
            legend_at_web (str): A link leading to a wms describing document (png).
        """
        __table_args__ = {'schema': 'land_use_plans'}
        __tablename__ = 'view_service'
        id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
        reference_wms = sa.Column(sa.String, nullable=False)
        legend_at_web = sa.Column(sa.String, nullable=True)


    class LegendEntry(Base):
        """
        A class based legend system which is directly related to
        :meth:`oereb_server.models.land_use_plans.ViewService`.
        Attributes:
            id (int): The identifier. This is used in the database only and must not be set manually. If
                you  don't like it - don't care about.
            symbol (str): An image with represents the legend entry. This can be png or svg. It is string
                but BaseCode64  encoded.
            legend_text (str): Multilingual text to describe this legend entry.
            type_code (str): Type code of the public law restriction which is represented by this legend
                entry.
            type_code_list (str): List of all public law restrictions which are described through this
                legend  entry.
            topic (str): Statement to describe to which public law restriction this legend entry
                belongs.
            sub_theme (str): Description for sub topics this legend entry might belonging to.
            other_theme (str): A link to additional topics. It must be like the following patterns
                * ch.{canton}.{topic}  * fl.{topic}  * ch.{bfsnr}.{topic}  This with {canton} as
                the official two letters short version (e.g.'BE') {topic} as the name of the
                topic and {bfsnr} as the municipality id of the federal office of statistics.
            view_service_id (int): The foreign key to the view service this legend entry is related to.
            view_service (oereb_server.models.land_use_plans.ViewService):
                The dedicated relation to the view service instance from database.
        """
        __table_args__ = {'schema': 'land_use_plans'}
        __tablename__ = 'legend_entry'
        id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
        symbol = sa.Column(sa.String, nullable=False)
        legend_text = sa.Column(sa.String, nullable=False)
        type_code = sa.Column(sa.String(40), nullable=False)
        type_code_list = sa.Column(sa.String, nullable=False)
        topic = sa.Column(sa.String, nullable=False)
        sub_theme = sa.Column(sa.String, nullable=True)
        other_theme = sa.Column(sa.String, nullable=True)
        view_service_id = sa.Column(
            sa.Integer,
            sa.ForeignKey(ViewService.id),
            nullable=False
        )
        view_service = relationship(ViewService, backref='legends')


    class PublicLawRestriction(Base):
        """
        The container where you can fill in all your public law restrictions to the topic.
        Attributes:
            id (int): The identifier. This is used in the database only and must not be set manually. If
                you  don't like it - don't care about.
            information (dict): The multilingual textual representation of the public law restriction.
            topic (str): Category for this public law restriction (name of the topic).
            sub_theme (str): Textual explanation to subtype the topic attribute.
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
            geolink (int): ID of the referenced documents in OEREBlex.
            geom (geoalchemy2.types.Geometry): The geometry of the public law restriction.
            geo_metadata (uri): Link to the metadata.
            basis (list of oereb_server.models.land_use_plans.PublicLawRestriction):
                Public law restricitons as basis.
            refinements (list of oereb_server.models.land_use_plans.PublicLawRestriction):
                Public law restricitons as refinements.
            view_service_id (int): The foreign key to the view service this public law restriction is
                related to.
            view_service (oereb_server.models.land_use_plans.ViewService):
                The dedicated relation to the view service instance from database.
            office_id (int): The foreign key to the office which is responsible to this public law
                restriction.
            responsible_office (oereb_server.models.land_use_plans.Office):
                The dedicated relation to the office instance from database.
        """
        __table_args__ = {'schema': 'land_use_plans'}
        __tablename__ = 'public_law_restriction'
        id = sa.Column(sa.String, primary_key=True)
        information = sa.Column(sa.String, nullable=False)
        topic = sa.Column(sa.String, nullable=False)
        sub_theme = sa.Column(sa.String, nullable=True)
        other_theme = sa.Column(sa.String, nullable=True)
        type_code = sa.Column(sa.String(40), nullable=True)
        type_code_list = sa.Column(sa.String, nullable=True)
        law_status = sa.Column(sa.String, nullable=False)
        published_from = sa.Column(sa.Date, nullable=False)
        geolink = sa.Column(sa.Integer, nullable=True)
        view_service_id = sa.Column(
            sa.Integer,
            sa.ForeignKey(ViewService.id),
            nullable=False
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
        Attributes:
            id (int): The identifier. This is used in the database only and must not be set manually. If
                you  don't like it - don't care about.
            law_status (str): The status switch if the document is legally approved or not.
            published_from (datetime.date): The date when the document should be available for
                publishing on extracts. This  directly affects the behaviour of extract
                generation.
            geo_metadata (str): A link to the metadata which this geometry is based on which delivers
                machine  readable response format (XML).
            public_law_restriction_id (int): The foreign key to the public law restriction this geometry
                is  related to.
            public_law_restriction (pyramid_oereb.standard.models.land_use_plans
                .PublicLawRestriction): The dedicated relation to the public law restriction instance from
                database.
            office_id (int): The foreign key to the office which is responsible to this public law
                restriction.
            responsible_office (pyramid_oereb.standard.models.land_use_plans.Office):
                The dedicated relation to the office instance from database.
            geom (geoalchemy2.types.Geometry): The geometry it's self. For type information see
                geoalchemy2_.  .. _geoalchemy2:
                https://geoalchemy-2.readthedocs.io/en/0.2.4/types.html  docs dependent on the
                configured type.  This concrete one is POLYGON
        """
        __table_args__ = {'schema': 'land_use_plans'}
        __tablename__ = 'geometry'
        id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
        law_status = sa.Column(sa.String, nullable=False)
        published_from = sa.Column(sa.Date, nullable=False)
        geo_metadata = sa.Column(sa.String, nullable=True)
        geom = sa.Column(GeoAlchemyGeometry('POLYGON', srid=srid), nullable=False)
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
        Attributes:
            id (int): The identifier. This is used in the database only and must not be set manually. If
                you  don't like it - don't care about.
            public_law_restriction_id (int): The foreign key to the public law restriction which bases
                on another  public law restriction.
            public_law_restriction_base_id (int): The foreign key to the public law restriction which is
                the  base for the public law restriction.
            plr (pyramid_oereb.standard.models.land_use_plans.PublicLawRestriction):
                The dedicated relation to the public law restriction (which bases on) instance from  database.
            base (pyramid_oereb.standard.models.land_use_plans.PublicLawRestriction):
                The dedicated relation to the public law restriction (which is the base) instance from database.
        """
        __tablename__ = 'public_law_restriction_base'
        __table_args__ = {'schema': 'land_use_plans'}
        id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
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
        Attributes:
            id (int): The identifier. This is used in the database only and must not be set manually. If
                you  don't like it - don't care about.
            public_law_restriction_id (int): The foreign key to the public law restriction which is
                refined by  another public law restriction.
            public_law_restriction_refinement_id (int): The foreign key to the public law restriction
                which is  the refinement of the public law restriction.
            plr (pyramid_oereb.standard.models.land_use_plans.PublicLawRestriction):
                The dedicated relation to the public law restriction (which refines) instance from  database.
            base (pyramid_oereb.standard.models.land_use_plans.PublicLawRestriction):
                The dedicated relation to the public law restriction (which is refined) instance from database.
        """
        __tablename__ = 'public_law_restriction_refinement'
        __table_args__ = {'schema': 'land_use_plans'}
        id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
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

Next step would be configuration of the theme which is same like known. Only difference will be the use of
oereb lex source. See chapter :ref:`changes-new-config-oereb-lex` to know how.


.. _changes-new-config-options:

New configuration options in yml
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _changes-new-config-mapfish-print:

MapFish Print
"""""""""""""

See the `pyramid_oereb_standard.yml <https://github.com/pyramidoereb/pyramid_oereb/blob/v1.1.0/pyramid_oereb/standard/pyramid_oereb.yml.mako#L65>`__
for the correct style of the configuration.

- improved print templates to fit federal definitions as good as possible
- improved configuration in the ``pyramid_oereb.yml`` to better support requirements of different operators (multilingual)
    - **template_name**:
        Defines the name of the mapfish print template which is used to provide static extract.
    - **headers**:
        Defines the content type which is sent to mapfish print service by mapfish print proxy.
        This must be set to `Content-Type: application/json; charset=UTF-8`
    - **furtherInformationText**:
        It must contain at least one of the following sub items which can contain a
        free text. It is used to point user to more cantonal information about the oereb. It can contain
        simple html markup. As sub item at least the configured default language must be defined: *de*, *fr*,
        *it*, *rm*
        Otherwise a '-' will be shown in resulting PDF.
    - **certificationText** :
        It must contain at least one of the following sub items which can contain a
        free text. It is used to specify cantonal information about certification. It can contain
        simple html markup. As sub item at least the configured default language must be defined: *de*, *fr*,
        *it*, *rm*
        Otherwise a '-' will be shown in resulting PDF.

Since behaviour of mapfish print service was updated you may want have a more detailed look at the docs of
this package.

.. _changes-new-config-themes:

Theme configuration
"""""""""""""""""""

Each theme configuration block included a threshold configuration like this:

.. code-block:: yaml

    thresholds:
      length:
        limit: 1.0
        # Unit used internally only until now!
        unit: 'm'
        precision: 2
      area:
        limit: 1.0
        # Unit used internally only until now!
        unit: 'm²'
        precision: 2
      percentage:
        precision: 1

Due to many code reorganisations and cleaning it turned out that this is not needed any longer. So now the
block looks ways simpler as follows:

.. code-block:: yaml

    thresholds:
      length:
        limit: 1.0
      area:
        limit: 1.0

.. _changes-new-config-oereb-lex:

OEREBlex
""""""""

We assume you already defined your model mapping definition and your data is organized like described in
chapter :ref:`changes-oereb-lex`. Then you only need to add/adjust your config in little details.

The OEREBlex configuration is done in two places:

#. dedicated configuration block for OEREBlex common config
#. inside of each theme configuration block which should use OEREBlex

Find an example configuration for OEREBlex below:

.. code-block:: yaml

    # Configuration for OEREBlex
    oereblex:
      # OEREBlex host
      host: https://oereblex.bl.ch
      # geoLink schema version
      version: 1.1.0
      # Pass schema version in URL
      pass_version: true
      # Language of returned values
      language: de
      # Value for canton attribute
      canton: BL
      # Mapping for other optional attributes
      # mapping:
      #   official_number: number
      #   abbreviation: abbreviation
      # Handle related decree also as main document
      # By default a related decree will be added as reference of the type "legal provision" to the main
      # document. Set this flag to true, if you want the related decree to be added as additional legal
      # provision directly to the public law restriction. This might have an impact on client side rendering.
      related_decree_as_main: true
      # Proxy to be used for web requests
      proxy:
        http: http://xxx:xxx@proxy.ch:8088
        https: https://xxx:xxx@proxy.ch:8088
      # auth:
      #   username: preview
      #   password: preview

.. note:: The configuration above is an example only. If you want to know more in detail what to configure
    and why please have a detailed look at the documentation of the used package
    `python_geolink_formatter <https://gf-bl.gitlab.io/python-geolink-formatter/v1.3.0/index.html>`__ and
    :ref:`api-pyramid_oereb-contrib-sources-document-oereblexsource`.


Find an example configuration for land use plans below:

.. code-block:: yaml

    - name: plr73
      code: LandUsePlans
      geometry_type: GEOMETRYCOLLECTION
      # Define the minmal area and length for public law restrictions that should be considered as 'true' restrictions
      # and not as calculation errors (false true's) due to topological imperfections
      thresholds:
        length:
          limit: 1.0
        area:
          limit: 1.0
      text:
        de: Nutzungsplanung kommunal
      language: de
      federal: false
      standard: true
      source:
        class: pyramid_oereb.contrib.sources.plr_oereblex.DatabaseOEREBlexSource
        params:
          db_connection: <your db connection>
          models: <path_to_your_models>.land_use_plans
      hooks:
        get_symbol: pyramid_oereb.standard.hook_methods.get_symbol
        get_symbol_ref: pyramid_oereb.standard.hook_methods.get_symbol_ref
      law_status:
        in_force: inForce
        running_modifications: runningModifications
