===============================
``pyramid_oereb`` (ÖREB-Server)
===============================

Temporary Startup of the dev server:

1. ``docker build -t pyramid_oereb:dev .``
2. Build run the initial build depending on you OS:
  * Linux: ``docker run --rm -v $(pwd):/workspace -u $(id -u):$(id -g) pyramid_oereb:dev make clean-all build`` 
  * MAC: ``docker run --rm -v $(pwd):/workspace pyramid_oereb:dev make clean-all build`` 
  * Windows CMD: ``docker run --rm -v %cd%:/workspace pyramid_oereb:dev make clean-all build`` 
  * Windows Powershell: ``docker run --rm -v ${PWD}:/workspace pyramid_oereb:dev make clean-all build`` 
5. ``docker-compose build``
6. ``docker-compose up``

Running ``docker-compose up`` will start the DB (it will automatically import the test/dev data on startup) and start
a running instance of the pyramid_oereb DEV server connected to the DB. The project folder is mounted
to it. So changes take effect.

To run the tests locally (unix machine, windows users should go with the docker way described below):

1. Run ``make build`` (this will install the virtual environment on your machine if it's not already installed)
2. Start the dev database with ``docker-compose up -d oereb-db`` (with the default config, this uses the default Postgres port on your machine)
3. Run the tests with ``make tests``

To run one specfic test:

.. code-block:: bash

  PYTEST_OPTS="-k <name_of_the_test>" make tests

To run all tests in a specific file or directory (omit the subfolder ``tests`` in ``PYTEST_PATH``):

.. code-block:: bash

  PYTEST_PATH="<path_to_test>"  make tests

To run the tests locally but inside Docker:

1. ``docker-compose build``
2. ``docker-compose up -d``
3. change line 7 in tests/resources/test_config.yml from ``postgresql://postgres:postgres@localhost:5432/oereb_test_db`` to ``postgresql://postgres:postgres@oereb-db:5432/oereb_test_db``
4. ``docker-compose exec oereb-server make test-core``

|Build Status| |Requirements Status|


.. image:: https://api.codacy.com/project/badge/Grade/cf50094a4e84434d837babf1106f9fcb
   :alt: Codacy Badge
   :target: https://app.codacy.com/gh/openoereb/pyramid_oereb?utm_source=github.com&utm_medium=referral&utm_content=openoereb/pyramid_oereb&utm_campaign=Badge_Grade_Settings


``pyramid_oereb`` is an open-source implementation of the server side part for the swiss `"Cadastre of
Public-law Restrictions on landownership" (PLR-cadastre) <https://www.cadastre.ch/en/oereb.html>`__.

It is written in Python and designed as a plugin for the `Pyramid Web Framework
<http://docs.pylonsproject.org/projects/pyramid/en/latest/>`__. This allows ``pyramid_oereb`` to be
included in any Pyramid web application.

Please refer to the `documentation <https://openoereb.github.io/pyramid_oereb/>`__ for detailed
information and instructions for installation and configuration.

If you are interested in contributing or extending the project, take a look at the
`contribution page <https://openoereb.github.io/pyramid_oereb/doc/contrib/>`__.

.. |Build Status| image:: https://github.com/openoereb/pyramid_oereb/actions/workflows/ci.yaml/badge.svg
   :target: https://github.com/openoereb/pyramid_oereb/actions/workflows/ci.yaml
   :alt: Build Status

.. |Requirements Status| image:: https://requires.io/github/openoereb/pyramid_oereb/requirements.svg?branch=master
   :target: https://requires.io/github/openoereb/pyramid_oereb/requirements/?branch=master
   :alt: Requirements Status

Local testing for versions V1
=============================

Run dev server
--------------

Following packages are required: ``python3-dev`` ``libgeos-dev`` ``python3-venv`` ``postgresql-client`` ``libpq-dev`` ``xsltproc``

Clone project:

.. code-block:: bash

  git clone git@github.com:openoereb/pyramid_oereb.git
  cd pyramid_oereb

The information for the connection to the main database, the print service and the statistics functionality database has to be provided in a .env file (not committed, copy sample.env and edit it if necessary):

.. code-block:: bash

  cp sample.env .env

Run:

.. code-block:: bash

  make serve

JSON reduced extract is accessible at: http://localhost:6543/oereb/extract/reduced/json/CH113928077734.


**When running in to issues installing** ``libpq-dev`` **:**

.. code-block:: bash

  The following packages have unmet dependencies:
   libpq-dev : Depends: libpq5 (= 10.12-0ubuntu0.18.04.1) but 12.3-1.pgdg18.04+1 is to be installed


Try to install a specific version (adapt the version to your requirement):

.. code-block:: bash

  sudo apt install libpq5=10.12-0ubuntu0.18.04.1


Run tests
---------

To check your code, run `make checks`. It will run style checks and tests. It's also possible to
run sub-target independently:

- ``make checks-style`` to run only style-related checks (linting).
- ``make tests`` to run tests. Python 3.7 is used by default. But you can run tests with another version by
  running: ``PYTHON_TEST_VERSION=python3.x make tests``. You can also set this variable in the Makefile.
- ``PYTEST_OPTS="-k test_name" make test`` to run a specific test

After running tests, the coverage is available in the folder ``coverage_report``.

Use Oereblex data model
-----------------------

To test the application with the Oereblex data model, adapt the configuration files ``pyramid_oereb_standard.yml.mako`` and ``docker/config.yml.tmpl``.
See this example with the theme forest_perimeters:

.. code-block:: yaml

  source:
    # Standard data model
    #class: pyramid_oereb.standard.sources.plr.DatabaseSource
    # Oereblex data model
    class: pyramid_oereb.contrib.sources.plr_oereblex.DatabaseOEREBlexSource
    params:
      db_connection: *main_db_connection
      # Standard data model
      #models: pyramid_oereb.standard.models.forest_perimeters
      # Oereblex data model
      models: pyramid_oereb.contrib.models.oereblex.forest_perimeters

The sample data is in ``sample_data/oereblex``.

Run the application:

.. code-block:: bash

  USE_OEREBLEX=TRUE make serve


JSON reduced extract is accessible at: http://localhost:6544/oereb/extract/reduced/json/CH113928077734. This will do a call to the Oereblex service defined in the configuration file, and the success of the call will depend on the external service being available, and the geolink id being used in the sample data still existing on the external system.

It is possible to run this instance in parallel to the instance which uses the standard database. For this, one should create a second clone of the project.

If testing ``make serve`` with another theme than forest_perimeters, changes will be necessary in the directory ``sample_data/oereblex/``: first remove the symbolic link corresponding to this theme, then create a directory and add JSON data files into it. In comparison to the data from the standard model, a new attribute ``geolink`` is required in ``public_law_restriction.json``, which should correspond to an existing geolink in the Oereblex server defined in the configuration (see ``sample_data/oereblex/forest_perimeters`` for example files).


Dev environment (V2)
====================

``pyramid_oereb`` can be run with ``docker-compose`` or directly on the host. The application requires a running database.

The Docker composition consists of the service ``oereb-server`` (the container in which the application is to be started) and the service ``oereb-db`` (which hosts the database). To run ``pyramid_oereb`` with ``docker-compose``, see section "General workflow (in Docker)".

To run the server directly on the host, you need to be using a Linux system with all the dependencies installed. In this case, you should use an already existing database. For details see section "General worfklow (local shell)".

Database connection
-------------------

For the database connection, the following environment variables must be set (if not using the default parameters):

.. code-block:: bash

  # the db-server username
  PGUSER
  # the db-server password
  PGPASSWORD
  # the db-server host
  PGHOST
  # the database in the db-server
  PGDATABASE
  # the port on which the db-server is listening
  PGPORT

If these are not provided, the default values found in the Makefile will be used.

NB: if these environment variables are set in the host environment, they will also be used in the ``docker-compose`` composition.


General workflow (in Docker)
----------------------------

1. Run the composition with ``docker-compose up -d``
2. You can check whether the containers started properly with ``docker-compose ps``
3. Connect to the server container with ``docker-compose exec oereb-server zsh``
4. Start the server in development mode with ``make serve-dev``
5. The sample data extract should be available at http://localhost:6543/oereb/extract/json?EGRID=CH113928077734
6. BONUS: If you use an IDE like VSCode you can attach it to the running container to have convenient features like autocomplete or code inspection

NB: Alternatively, start the server from your local shell with ``docker-compose exec oereb-server make serve-dev``

Clean up after work
...................

It is recommended to stop your composition when you stop working:

.. code-block:: bash

  docker-compose down

Update Dockerfile
.................

If you need to change something inside the ``Dockerfile`` you need to rebuild the ``oereb-server`` image. So after your change,
stop the docker composition and rebuild it:

.. code-block:: bash

  docker-compose down
  docker-compose build

General workflow (local shell)
------------------------------

These instructions are sufficient only if you have all dependencies locally available (``python3-dev`` ``libgeos-dev`` ``python3-venv`` ``postgresql-client`` ``libpq-dev`` etc.)
and in the right versions. Otherwise this might lead to strange behaviors.

1. In a local shell in the project path, start the server in development mode with ``make serve-dev``
2. The sample data extract should be available at http://localhost:6543/oereb/extract/json?EGRID=CH113928077734


Useful ``make`` targets
------------------------

Run the ``make`` targets found in the Makefile either in the ``oereb-server`` container (if using ``docker-compose``) or in your local shell (if running the server locally).
Some useful targets:

- ``make serve-dev`` to run the application
- ``make test`` to run the application tests
- ``make clean`` to empty the database
- ``make clean-all`` to empty the database, uninstall the application and the virtual env and clear the rendered configuration files

If necessary the application is re-installed and the database is filled when running ``make serve-dev`` again.

Using MapFish-Print
-------------------

To be able to test the OEREB static extract (pdf), you need to run ``pyramid_oereb`` with ``docker-compose`` and to have a running instance of `pyramid_oereb_mfp <https://github.com/openoereb/pyramid_oereb_mfp>`__.
The Docker network ``print-network`` is also required and can be created with:

.. code-block:: bash

  docker network create print-network

The sample static extract should then be available at http://localhost:6543/oereb/extract/pdf?EGRID=CH113928077734
