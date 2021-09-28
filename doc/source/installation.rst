.. _installation:

Installation
============

This section will guide you through the steps to install and run an own instance of ``pyramid_oereb`` using
the standard configuration. If you are planning to adapt the application to fit a custom data source, the
possibilities and additional steps are described in the section :ref:`configuration`.


.. _installation-requirements:

Requirements
------------

In order to install and run an instance of ``pyramid_oereb``, the following requirements have to be met.

1.  **A running Pyramid application:**
    You need a running Pyramid application, in which you can include ``pyramid_oereb``. If you are not
    familiar with setting up such an application, please follow the instructions in the official `Pyramid
    documentation <http://docs.pylonsproject.org/projects/pyramid/en/latest/#getting-started>`__.

2.  **A running Database:**
    For the standard configuration you need a running database with a role which is allowed to create schemata
    and tables and to manipulate data. We recommend to use PostgreSQL with PostGIS, but theoretically you
    should be able to use any spatial database, that is supported by `SQLAlchemy
    <https://www.sqlalchemy.org/>`__ and `GeoAlchemy 2 <https://geoalchemy-2.readthedocs.io/en/latest/>`__.


.. _installation-step:

Installation steps
------------------

.. note:: Activate virtual environment before, if you use one.

   .. code-block:: shell

    source <path_to_your_venv>/bin/activate


.. _installation-step-add-package:

1. Add package
..............

Add ``pyramid_oereb`` to the list of requirements in your application's ``setup.py``.
In your ``setup.py``, you should depend on ``pyramid_oereb[recommend]`` to get the recommended versions of
the dependencies of ``pyramid_oereb``, or ``pyramid_oereb[no-version]`` to get the dependencies of
``pyramid_oereb`` without specifying which versions of these dependencies shall be used. You shouldn't just
depend on ``pyramid_oereb`` because this will not take into account the dependencies of ``pyramid_oereb``.


.. _installation-step-dependencies:

2. Install dependencies
.......................

Install the newly added dependencies using *pip*:

.. code-block:: shell

 pip install -e .


.. _installation-step-configuration:

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

.. note:: Not familiar with YAML? Please have a look at its `specification
   <http://www.yaml.org/spec/1.2/spec.html>`__.


.. _installation-step-database:

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


.. _installation-step-sample-data:

5. Load data (optional)
.......................

The easiest way to add some data, is to import the data of an available federal topic using the provided
script.

.. note:: This exmple shows the import for the topic `ch.Sicherheitszonenplan`, but you can use any federal
   topic you like to. You should ensure, that the topic contains some data within the perimeter (canton) you
   want to show.

.. warning:: The import script only works for topics using the standard database. Any modifications to the
   database structure may cause the import to fail.

First you have to ensure, that the correct download URL is defined for the topic in
`pyramid_oereb_standard.yml`. The configuration for the topic should contain the following download property:

.. code-block:: yaml

 plrs:

 ...

 - name: plr108
   code: ch.Sicherheitszonenplan
   ...
   download: https://data.geo.admin.ch/ch.bazl.sicherheitszonenplan.oereb/data.zip

If this is the case, you can run the import script for this topic:

.. code-block:: shell

 import_federal_topic -c pyramid_oereb_standard.yml -t ch.Sicherheitszonenplan

The data for this federal topic should now be available in your standard database. For an overview of the
available import options, please run ``import_federal_topic --help``.

Alternatively, a set of sample data is available in the repository_ in the directory `sample_data`. After
downloading it, you can import the sample data into the configured database using the following script:

.. code-block:: shell

 python <PATH TO VENV SITE_PACKAGES>/pyramid_oereb/standard/load_sample_data.py -c pyramid_oereb_standard.yml

We assume you have put your downloaded sample data in a folder named `sample_data` in your project's root
directory, as found in the repository_. Otherwise you have to specify the location of your sample data using
the ``-d`` or ``--dir=`` argument.

.. warning:: Use the sample data corresponding to the installed version of ``pyramid_oereb`` by selecting the
   matching release.


.. _installation-step-application:

6. Include in application
.........................

To include ``pyramid_oereb`` into your existing Pyramid application, you have to include the plugin in
your application's main method.
Open the ``__init__.py`` of your main module and add the following statement
in the main method somewhere before ``config.scan()``:

.. code-block:: python

 config.include('pyramid_oereb', route_prefix='oereb')

You can specify a different `route prefix <https://docs.pylonsproject.org/projects/pyramid/en/stable/narr/
urldispatch.html#using-a-route-prefix-to-compose-applications>`__ or omit it, if you are running a dedicated
server for ``pyramid_oereb``.

Additionally, you have to specify the created configuration in your application's INI file (e.g.
``development.ini``). Add the following lines in the ``[app:main]`` section:

.. code-block:: none

 pyramid_oereb.cfg.file = pyramid_oereb_standard.yml
 pyramid_oereb.cfg.section = pyramid_oereb

After modifying these two files, you have to start/restart your application's server, e.g. using `pserve`:

.. code-block:: none

 pserve development.ini

.. note:: If you have imported the sample data, you should now be able to request the sample extract by
   calling the extract service:

   .. code-block:: none

    http://<YOUR_APPLICATION_URL>/oereb/extract/embeddable/json/CH113928077734


.. _installation-next-steps:

Next steps
----------

Now you should be able to set up a running ``pyramid_oereb`` server using the standard configuration. If this
configuration fits your needs, you can now continue with importing your data into the created database. A
detailed description of each table can be found in the documentation of the
:ref:`api-pyramid_oereb-standard-models`.

If your data is already available in an existing database with a different structure or you need to use a
custom data source, the possible ways to adapt the models or to extend the application are described in the
section :ref:`configuration`.


.. _repository: https://github.com/openoereb/pyramid_oereb/
