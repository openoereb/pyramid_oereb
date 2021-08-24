===============================
``pyramid_oereb`` (ÖREB-Server)
===============================

|Build Status| |Requirements Status|

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

Following packages are required: ``python3-dev`` ``libgeos-dev`` ``python3-venv`` ``postgresql-client`` ``libpq-dev``

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


DEV Environment (V2)
====================

For runtime pyramid_oereb needs at least a running database to get the data from. this
repo ships with a `docker-compose.yml` to satisfy this needs.

If you are working on a linux system, and that all the dependencies are installed, it is
also possible to use an already existing database, and to run the pyramid server directly
on the host. Use the following command to run the server in development mode:

.. code-block:: bash

  make serve-dev

For the databse connection, the following environment variables must be set:

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

If these are not provided, the default values can be found in the Makefile.

NB: if these environment variables are set in the host environment, they will
also be used in the `docker-compose` composition.


General workflow (in Docker)
----------------------------

1. run docker-compose
2. connect a terminal to bash in the pyramid_oereb server container
3. use make with the provided Makefile to test, start the server or to build the virtual environment
4. BONUS: If you use an IDE like VSCode you can attach it to the running container to have convenient features like autocomplete or code inspection

General workflow (Docker + local shell)
---------------------------------------

This is only sufficient if you have all dependencies locally available (python3-dev, postgres-client, geos, etc.)
and in the right versions. Otherwise this might lead to strange behaviors.


1. run docker-compose
2. open local shell in project path
3. use make with the provided Makefile to clean the virtual environment (if needed)

Docker composition in detail
----------------------------

Prerequisite
............

Setup is intendet to have network available "print-network". To use the setup just for pyramid_oereb
dev without MapFishPrint you need to create the network first:

docker network create print-network

Fresh startup
.............

You can create the docker composition to develop the project:

.. code-block:: bash

  docker-compose up -d

This sets up a database container and a container which encapsulates the project. In case
you didn't had the images alread this will build the DEV-container first. Its based on
the `Dockerfile`. It will also start `pserve` with the `--reload` option in the `oereb-server`
container.

Once this step finished you should have 2 running containers belonging to the composition.

You might inspect with:

.. code-block:: bash

  docker container ls

This containers should run as long as you have dev work to do. Everything else is solved by
the provided Makefile.

To enter in the `oereb-server` container with `zsh` type:

.. code-block:: bash

  docker-compose exec oereb-server zsh

To start the server (and build the project automatically) you can run:

.. code-block:: bash

  docker-compose exec oereb-server make serve-dev


Clean up after work
...................

It is a recommended habit to stop your composition when you stop working:

.. code-block:: bash

  docker-compose down

Update Dockerfile
.................

If you need to change something inside the `Dockerfile` you need to rebuild it. So after your change
stop docker composition and rebuild it:

.. code-block:: bash

  docker-compose down
  docker-compose build
