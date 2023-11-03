.. _configuration:

Configuration
=============

You are looking at a highly configurable piece of software. To get the right understanding of the server it
is recommended to read this part carefully.

Since the swiss confederation's definition and the specification for the `OEREB Data Extract
<https://www.cadastre.ch/content/cadastre-internet/de/manual-oereb/publication/publication.download
/cadastre-internet/de/documents/oereb-weisungen/OEREB-Data-Extract_de.pdf>`__ is really straight,
we had very narrow margins to develop the code. Using this pyramid plugin, you will get a running server
providing the services to satisfy the federal specification. But to get this extract, you need to bind your
data to this server. And this is basically what you need to configure.

This section describes the different possibilities to adapt the application on different data structures or
even custom data sources. If you are planning to use such modifications, we suggest to check all possible
solutions first, as the necessary effort can vary significantly depending on your specific needs.


.. _configuration-additional-topics:

Add additional topics
---------------------

If you only need to add one or more additional cantonal topics and want to use the standard database structure
for these too, you can run a provided script to generate the required models.

.. code-block:: shell

   create_standard_model -c <YOUR_NEW_TOPIC_CODE> -g <GEOMETRY_TYPE> -p <TARGET_PATH> -k TRUE

The first parameter is the code of your new topic and has to be defined in camelcase. The geometry type for
the theme can be one of the following:

   - `POINT`,
   - `LINESTRING`,
   - `POLYGON`
   - `MULTIPOINT`
   - `MULTILINESTRING`
   - `MULTIPOLYGON` or
   - `GEOMETRYCOLLECTION`.

The geometry collection is only meant for topics that can consist of different geometry types. We **strongly**
recommend to use it **only if a simple geometry cannot be used** and to put **only one geometry** in each
record. Do not use it as a bucket for everything! The third parameter defines the output directory in which
the new file will be created, e.g. a module directory of your application.

To use strings as primary key type, add the '-k TRUE' parameter. If not supplied, the default primary key type
of integer will be used instead.

After creating the models you have to create its configuration. Open the configuration file
(pyramid_oereb_standard.yml) and copy the section from one of the existing topics which usually looks like
this:

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
         unit: 'm2'
         precision: 2
       percentage:
         precision: 1
     text:
       de: Baulinien Nationalstrassen
     language: de
     federal: true
     standard: true
     source:
       class: pyramid_oereb.lib.sources.plr.DatabaseSource
       params:
         db_connection: postgresql://postgres:password@localhost:5432/pyramid_oereb
         models: pyramid_oereb.standard.models.motorways_building_lines
     get_symbol_method: pyramid_oereb.standard.methods.get_symbol


Apply the necessary modifications for the new topic. This should at least be the the name, code and text
definitions and of course the models property within the source parameters. It should point to the module
with the generated models of the former step.

Now you have set up an empty additional topic and you can continued with deploying your data into it.


Add an oereblex topic
---------------------

If you want to use oereblex for a topic, you can proceed as described in the previous section,
but using a different script to generate the required models.

.. code-block:: shell

   create_oereblex_model -c <YOUR_NEW_TOPIC_CODE> -g <GEOMETRY_TYPE> -p <TARGET_PATH> -k TRUE


.. _configuration-adapt-models:

Adapt existing models
---------------------

Another option to modify the standard configuration, is to adapt the existing models to fit another database
structure. This method is recommended if you are using an existing database supported by GeoAlchemy 2 and
already containing all the necessary data but in a different structure. In this case you should check, if it
is possible to transform the data by extending the existing models with a mapping to fit your structure.

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
