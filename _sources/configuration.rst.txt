.. _configuration:

Configuration
=============

You are looking at a highly configurable piece of software. To get a good understanding of the server it
is recommended to read this part carefully.

The specifications of the oereb data model, the web services, the data extracts and the print layout 
by the Swiss Confederation are very precise `OEREB specifications
<https://www.cadastre.ch/de/manual-oereb/publication/instruction.html>`__ . Code development was guided 
by the exact implementation of the specifications and the user requirements. Using this pyramid plugin, 
you will get a running server providing all the services defined by the federal specifications. 
The binding of cantonal and federal data to the server is done by the configuration options.

This section describes the different possibilities to adapt the application to work with various data structures or
even custom data sources. If you are planning to implement such modifications, we suggest to check all possible
solutions first, as the necessary effort can vary significantly depending on your specific needs.

.. _configuration-initial-setup:

Create the inital database setup
--------------------------------

Out of the box the pyramid_oereb server supports three different topic configurations in the database:

  - the **pyramid_oereb standard model**
  - the **interlis 2.3 OeREBKRM transfer model**
  - the **OEREBlex model**

Pyramid_oereb Standard Model
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This schema and table structure is based on the initial topic structure used in the pyramid_oereb
v1.x versions. It's mainly used for cantonal topics which are not (yet) stored in the interlis 2.3 OeREBKRM-
Transfer structure and by cantons that do not use OeREB-Lex to manage the legal documents.

Interlis 2.3 OeREBKRM Transfer Model
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All the federal data sets are provided in this data structure. So this is the schema and table model you
want to use for all the federal topics unless you want to transform the data to a specific database structure.
If your cantonal data is also stored based on this model, then you probably want to use this structure 
for all topics to homogenize your database content.
The `Ili2pg Oereb Data Import Manual <https://github.com/openoereb/ili2pg_oereb_data_import_manual>`__
explains how to use the ili2pg tool to create the corresponding schema and how to import the XML data.


OEREBlex Topic Model
^^^^^^^^^^^^^^^^^^^^

This third model is usefull if you maintain your legal documents using the OEREBlex application and you
have a specific cantonal model for your data. It is similar to the pyramid_oereb standard model, but all
the document related tables are omitted. Instead the documents are linked by the geolink attribute. 

.. _configuration-additional-topics:

Add additional standard topics
------------------------------

If you like to add one or more additional topics based on the *pyramid_oereb standard* database structure
you can use the internal command below creating an SQL script to establish the topic schema.

But before creating any new topic structure you have to add its configuration. Open the configuration file
(pyramid_oereb.yml) and copy the section from one of the existing **standard** topics which usually 
looks like this:

.. code-block:: yaml

    - code: ch.NE.Baulinien
      geometry_type: LINESTRING
      thresholds:
        length:
          limit: 1.0
        area:
          limit: 1.0
      language: fr
      federal: false
      view_service:
        layer_index: 1
        layer_opacity: 0.75
      source:
        class: pyramid_oereb.contrib.data_sources.standard.sources.plr.DatabaseSource
        params:
          db_connection: *main_db_connection
          # model_factory: pyramid_oereb.contrib.data_sources.standard.models.theme.model_factory_integer_pk
          # uncomment line above and comment line below to use integer type for primary keys
          model_factory: pyramid_oereb.contrib.data_sources.standard.models.theme.model_factory_string_pk
          schema_name: road_building_lines
      hooks:
        get_symbol: pyramid_oereb.contrib.data_sources.standard.hook_methods.get_symbol
        get_symbol_ref: pyramid_oereb.core.hook_methods.get_symbol_ref
      law_status_lookup:
        - data_code: inKraft
          transfer_code: inKraft
          extract_code: inForce
        - data_code: AenderungMitVorwirkung
          transfer_code: AenderungMitVorwirkung
          extract_code: changeWithPreEffect
        - data_code: AenderungOhneVorwirkung
          transfer_code: AenderungOhneVorwirkung
          extract_code: changeWithoutPreEffect
      document_types_lookup:
        - data_code: LegalProvision
          transfer_code: Rechtsvorschrift
          extract_code: LegalProvision
        - data_code: Law
          transfer_code: GesetzlicheGrundlage
          extract_code: Law
        - data_code: Hint
          transfer_code: Hinweis
          extract_code: Hint

Apply the necessary modifications/replacements for the new topic. This should at least be the schema name, 
code, geometry type and of course the models property within the source parameters:
Make sure that this source class is `pyramid_oereb.contrib.data_sources.*standard*.sources.plr.DatabaseSource`
and not interlis_2_3. - The same goes for the model_factory and the get_symbol element. It should be set to
*standard*.

Also set the language of the data and if it's a federal (true) or cantonal topic (false). You also want to
define what lookup codes are for the law_status and document types.

Once the configuration set, run the following command:

.. code-block:: shell

   create_standard_tables -c <YOUR_YAML_CONFIGURATION> -T [flag used to skip schema creation] 
    --sql-file=<PATH_AND_SQL_SCRIPTNAME> -w [to over-write existing sql instead of append]

The first parameter ``-c or --configuration=YAML`` is the path to your YAML configuration file. 
By default it's *pyramid_oereb.yml*

The second optional parameter ``-s or --section=SECTION`` allows you to specify the section containing
the configuration part to use. Default is *pyramid_oereb*.

The parameter ``-T or --tables-only`` skips the schema creation and creates only the tables.

The option ``--sql-file=SQL_FILE`` generates an SQL file containing the schema and table creation 
commands. *SQL_FILE* should be the name or the absolute path of the file. E.g: my_sql_script.sql

If your yaml file uses the c2ctemplate style (starting with vars) you need to add the
``--c2ctemplate-style`` parameter.

The option ``-w or --over-write`` allows you to overwrite an existing sql file. Default is append.

Now you have set up an empty additional topic in your database and you can proceed with deploying 
your data into it.

Add additional interlis topics
------------------------------

Follow the `Ili2pg Oereb Data Import Manual <https://github.com/openoereb/ili2pg_oereb_data_import_manual>`__
to create a new topic schema based on the OeREBKRM Transfer model and about how to import the XML data.

Once the schema is created do not forget to add the corresponding topic configuration in the *pyramid_oereb.yml*

.. code-block:: yaml

    - code: ch.BaulinienNationalstrassen
      geometry_type: LINESTRING
      thresholds:
        length:
          limit: 1.0
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm²'
          precision: 2
        percentage:
          precision: 1
      language: de
      federal: true
      view_service:
        layer_index: 1
        layer_opacity: 0.75
      source:
        class: pyramid_oereb.contrib.data_sources.interlis_2_3.sources.plr.DatabaseSource
        params:
          db_connection: *main_db_connection
          # model_factory: pyramid_oereb.contrib.data_sources.standard.models.theme.model_factory_integer_pk
          # uncomment line above and comment line below to use integer type for primary keys
          model_factory: pyramid_oereb.contrib.data_sources.interlis_2_3.models.theme.model_factory_integer_pk
          schema_name: motorways_building_lines
      hooks:
        get_symbol: pyramid_oereb.contrib.data_sources.interlis_2_3.hook_methods.get_symbol
        get_symbol_ref: pyramid_oereb.core.hook_methods.get_symbol_ref
      law_status_lookup:
        - data_code: inKraft
          transfer_code: inKraft
          extract_code: inForce
        - data_code: AenderungMitVorwirkung
          transfer_code: AenderungMitVorwirkung
          extract_code: changeWithPreEffect
        - data_code: AenderungOhneVorwirkung
          transfer_code: AenderungOhneVorwirkung
          extract_code: changeWithoutPreEffect
      document_types_lookup:
        - data_code: Rechtsvorschrift
          transfer_code: Rechtsvorschrift
          extract_code: LegalProvision
        - data_code: GesetzlicheGrundlage
          transfer_code: GesetzlicheGrundlage
          extract_code: Law
        - data_code: Hinweis
          transfer_code: Hinweis
          extract_code: Hint

Make sure to set the schema name to the one you defined using ili2pg, also set code, geometry type
and of course the models property within the source parameters:
Here the source class is `pyramid_oereb.contrib.data_sources.*interlis_2_3*.sources.plr.DatabaseSource`
and not standard. - The same goes for the model_factory and the get_symbol element. It should be set to
*interlis_2_3*.

Also define the language of the data and if it's a federal (true) or cantonal topic (false). You also want to
define that it is *NOT* the standard structure (false) and what lookup codes are used for the law_status 
and document types.

Add an OEREBLex Topic
---------------------

If you want to use the OEREBlex structure for a topic, you can proceed as described in the previous section,
but using a different script to generate the required models.

.. code-block:: shell

   create_oereblex_tables -c <YOUR_NEW_TOPIC_CODE> -g <GEOMETRY_TYPE> -p <TARGET_PATH> -k TRUE

For all topics
--------------

Do not forget to add the availability information in the *pyramid_oereb_main.availability* table to activate (or not)
the topic for a municipality.

.. _configuration-adapt-models:

Adapt existing models
---------------------

Another option to modify the standard configuration, is to adapt the existing models to fit another database
structure. This method is recommended if you are using an existing database supported by GeoAlchemy2 and
already containing all the necessary data but in a different structure. In this case you should check, if it
is possible to transform the data by extending the existing models with a mapping to fit your structure.

The easiest example is a simple mapping of table and column names, if you use a different language. Using the
possibilities of SQLAlchemy, you could extend the existing
pyramid_oereb.core.models.motorways_building_lines.office
:ref:`api-pyramid_oereb-core-models-motorways_building_lines-office` like this:

.. code-block:: python

   from pyramid_oereb.lib.standard.models import motorways_building_lines

   class Office(motorways_building_lines.Office):
       """
       The bucket to fill in all the offices you need to reference from public law restriction,
       document, geometry.

       Attributes:
           id (int): The identifier. This is used in the database only and must not be set manually.
               If you don't like it - don't care about.
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
       __table_args__ = {'schema': 'baulinien_nationalstrassen'}
       __tablename__ = 'amt'
       id = sa.Column('oid', sa.Integer, primary_key=True)
       office_at_web = sa.Column('amt_im_web', sa.String, nullable=True)
       line1 = sa.Column('zeile1', sa.String, nullable=True)
       line2 = sa.Column('zeile2', sa.String, nullable=True)
       street = sa.Column('strasse', sa.String, nullable=True)
       number = sa.Column('hausnr', sa.String, nullable=True)
       postal_code = sa.Column('plz', sa.Integer, nullable=True)
       city = sa.Column('ort', sa.String, nullable=True)

       (...)

The only thing, you have to care about, if you want to stay using the standard sources, is to keep the class
name, the names of the properties and their data types.

After extending the models, do not forget to change the models module in the configuration of the topic's
source.

.. code-block:: yaml

   - name: plr88
       code: ch.BaulinienNationalstrassen
       (...)
       source:
         class: pyramid_oereb.lib.sources.plr.DatabaseSource
         params:
           db_connection: postgresql://postgres:password@localhost:5432/pyramid_oereb
           models: my_application.models.motorways_building_lines
       get_symbol_method: pyramid_oereb.standard.methods.get_symbol


.. _configuration-create-sources:

Create custom sources
---------------------

If the possibilities described above do not fit your needs, you can implement your own sources. This is the
only possible way, if their are no existing sources available to access your data. For example, this could be
the case, if you are trying to access a kind of file system or some other proprietary data source.

As for the models, basically every source can be replaced using the configuration. In the configuration, every
source is defined by a `class` property, pointing on the class that should be used to instantiate it, and a
`params` property containing keyword arguments passed to its constructor.

For example, the real estate source for the standard database is configured with two parameters, the database
connection and the model class, which looks like the following.

.. code-block:: yaml

   real_estate:
     (...)
     source:
       # The source must have a class which represents the accessor to the source. In this case it
       # is a source already implemented which reads data from a database.
       class: pyramid_oereb.lib.sources.real_estate.DatabaseSource
       # The configured class accepts params which are also necessary to define
       params:
         # The connection path where the database can be found
         db_connection: "postgresql://postgres:password@localhost:5432/pyramid_oereb"
         # The model which maps the real estate database table.
         model: pyramid_oereb.standard.models.main.RealEstate

You can use the base source and extend it to create your own customized source implementations. With the
parameters passed as keyword arguments, you are free to pass as many arguments you need. There are only two
restrictions on implementing a custom source:

   1.  The source has to implement the method `read()` with the arguments used in its base source. For
       example, your custom real estate source has to accept the arguments defined in
       :ref:`api-pyramid_oereb-contrib-data_sources-standard-sources-real_estate-databasesource`.

   2.  The method `read()` has to add records of the corresponding type to the source' records list. Every
       source has list property called `records`. In case of a real estate source, the method `read()` has to
       create one or more instances of the :ref:`api-pyramid_oereb-core-records-real_estate-realestaterecord`
       and add them to this list.

This way, you should be able to create sources for nearly every possible data source.

.. note:: Implementing a custom source for public law restrictions, requires to create public law restriction
   records with all referenced records of other classes according to the `OEREB Data Extract
   <https://www.cadastre.ch/content/cadastre-internet/de/manual-oereb/publication/publication.download/
   cadastre-internet/de/documents/oereb-weisungen/OEREB-Data-Extract_de.pdf>`__ model (page 5).
