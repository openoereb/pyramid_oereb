.. _installation:

Installation
============

This section will guide you through the steps to install and run an own instance of ``pyramid_oereb`` using
the standard configuration. If you are planning to adapt the application to fit a custom data source, the
possibilities and additional steps are described in the section :ref:`configuration`.


Requirements
------------

In order to install and run an instance of ``pyramid_oereb``, the following requirements have to be met.

1.  **A running Pyramid application:**
    You need a running Pyramid application, in which you can include ``pyramid_oereb``. If you are not
    familiar with setting up such an application, please follow the instructions in the official `Pyramid
    documentation <http://docs.pylonsproject.org/projects/pyramid/en/latest/#getting-started>`__.

2.  **A running Database:**
    For the standard configuration you need a running database with a role, which is allow to create schemata
    and tables and to manipulate data. We recommend to use PostgreSQL with PostGIS, but theoretically use
    should be able to use any spatial database, that is supported by `SQLAlchemy
    <https://www.sqlalchemy.org/>`__ and `GeoAlchemy 2 <https://geoalchemy-2.readthedocs.io/en/latest/>`__.

Installation steps
------------------

.. note:: Activate virtual environment before, if you use one.

   .. code-block:: shell

    source <path_to_your_venv>/bin/activate

1. Add package
..............

Add ``pyramid_oereb`` to the list of requirements in your application's ``setup.py``.

2. Install dependencies
.......................

Install the newly added dependencies using *pip*:

.. code-block:: shell

 pip install -e .

3. Create standard configuration
................................

Create the necessary configuration for the application. The easiest way to achieve this, is to use the script
``create_standard_yaml``. It creates the basic YAML file in your current directory, which can be customized
afterwards. Executing ``create_standard_yaml --help`` shows you the two possible commandline arguments for
adjusting the file name and the database connection parameters. So you should at least set the right
connection string for your database:

.. code-block:: shell

 create_standard_yaml --database=<YOUR_DATABASE_CONNECTION>

You could also integrate this configuration into an existing YAML file, but we suggest to keep it
separated because it is already very complex on its own.

4. Set up database
..................

Use the generated configuration file to create the needed database structure. The standard database structure,
defined in the module ``pyramid_oereb.standard.models``, can be created automatically using the provided
script:

.. code-block:: shell

 create_standard_tables -c pyramid_oereb_standard.yml

.. warning:: We assume you did not specify a custom name for the configuration file. If you have used a custom
   name, you will have to replace `pyramid_oereb_standard.yml` with your specified name in this and all
   following steps.

.. note:: Run ``create_standard_tables --help`` for further information.

5. Load sample data (optional)
..............................

Included sample data can be imported into the configured database using the following script:

.. code-block:: shell

 load_standard_sample_data -c pyramid_oereb_standard.yml

6. Include in application
.........................

To include ``pyramid_oereb`` into your existing Pyramid application, you first have to include the plugin in
your application's main method. Open the ``__init__.py`` of your main module and add the following statement
in the main method somewhere before ``config.scan()``:

.. code-block:: python

 config.include('pyramid_oereb', route_prefix='oereb')

Additionally, you have to specify the created configuration in your application's INI file (e.g.
``development.ini``). Add the following lines in the ``[app:main]`` section:

.. code-block:: none

 pyramid_oereb.cfg.file = pyramid_oereb_standard.yml
 pyramid_oereb.cfg.section = pyramid_oereb

After modifying these two files, you have start/restart your application's server, e.g. using `pserve`:

.. code-block:: none

 pserve development.ini

.. note:: If you have imported the sample data, you should now be able to request the sample extract by
   calling the extract service:

   .. code-block:: none

    http://<YOUR_APPLICATION_URL>/oereb/extract/embeddable/json/CH113928077734
