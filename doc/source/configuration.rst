.. _configuration:

Configuration
=============

This section describes the different possibilities to adapt the application on different data structures or
even custom data sources. If you are planning to use such modifications, we suggest to check all possible
solutions first, as the necessary effort can vary significantly depending on your specific needs.


.. _configuration-additional-topics:

Add additional topics
---------------------

If you only need to add one or more additional cantonal topics and want to use the standard database structure
for these too, you can run a provided script to generate the required models.

.. code-block:: shell

 create_standard_model -c <YOUR_NEW_TOPIC_CODE> -g <GEOMETRY_TYPE> -p <TARGET_PATH>

The first parameter is the code of your new topic and has to be defined in camelcase. The geometry type for
the theme can be one of the following:

   - `POINT`,
   - `LINESTRING`,
   - `POLYGON` or
   - `GEOMETRYCOLLECTION`.

The geometry collection is only meant for topics that can consist of different geometry types. We **strongly**
recommend to use it **only if a simple geometry cannot be used** and to put **only one geometry** in each
record. Do not use it as a bucket for everything! The third parameter defines the output directory in which
the new file will be created, e.g. a module directory of your application.

After creating the models you have to create its configuration. Open the configuration file
(pyramid_oereb_standard.yml) and copy the section from one of the existing topics which usually looks like
this:

.. code-block:: yaml

 - name: plr88
      code: MotorwaysBuildingLines
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
        class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
        params:
          db_connection: postgresql://postgres:password@localhost:5432/pyramid_oereb
          models: pyramid_oereb.standard.models.motorways_building_lines
      get_symbol_method: pyramid_oereb.standard.methods.get_symbol

Apply the necessary modifications for the new topic. This should at least be the the name, code and text
definitions and of course the models property within the source parameters. It should point to the module
with the generated models of the former step.

Now you have set up an empty additional topic and you can continued with deploying your data into it.


.. _configuration-adapt-models:

Adapt existing models
---------------------

Another option to modify the standard configuration, is to adapt the existing models to fit another database
structure. This method is recommended if you are using an existing database supported by GeoAlchemy 2 and
already containing all the necessary data but in a different structure. In this case you should check, if it
is possible to transform the data by extending the existing models with a mapping to fit your structure.


Name mapping
............

The easiest example is a simple mapping of table and column names, if you use a different language. Using the
possibilities of SQLAlchemy, you could extend the existing
:ref:`api-pyramid_oereb-standard-models-motorways_building_lines-office` like this:

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

    ...

The only thing, you have to care about, if you want to stay using the standard sources, is to keep the class
name, the names of the properties and their data types.


Structure mapping
.................




.. _configuration-create-sources:

Create custom sources
---------------------
