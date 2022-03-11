===============================
``pyramid_oereb`` (ÖREB-Server)
===============================

Project description
===================

``pyramid_oereb`` is an open-source implementation of the server side part for the swiss `"Cadastre of
Public-law Restrictions on landownership" (PLR-cadastre) <https://www.cadastre.ch/en/oereb.html>`__.

It is written in Python and designed as a plugin for the `Pyramid Web Framework
<http://docs.pylonsproject.org/projects/pyramid/en/latest/>`__. This allows ``pyramid_oereb`` to be
included in any Pyramid web application.

Please refer to the `documentation <https://openoereb.github.io/pyramid_oereb/>`__ for detailed
information and instructions for installation and configuration.

If you are interested in contributing or extending the project, take a look at the
`contribution page <https://openoereb.github.io/pyramid_oereb/doc/contrib/>`__.


Starting the development server
===============================

1. Build run the initial build depending on you OS:
  * Linux: ``docker-compose run --rm -u $(id -u):$(id -g) oereb-make build``
  * MAC/Windows: ``docker-compose run --rm oereb-make build``
2. ``docker-compose up``

Running ``docker-compose up`` will start the DB (it will automatically import the test/dev data on startup) and start
a running instance of the pyramid_oereb DEV server connected to the DB. The project folder is mounted
to it. So changes take effect.

The sample static extract should then be available at http://localhost:6543/oereb/extract/json?EGRID=CH113928077734


Running the tests
=================

To run the tests locally:

The docker way:
---------------
  * Linux: ``docker-compose run --rm -u $(id -u):$(id -g) oereb-server make build tests``
  * MAC/Windows: ``docker-compose run --rm oereb-server make build tests``

For systems having a local make tool, the following recipe can be used:
``make docker-tests``

sometimes the local postgres port is already in use, and you must override it:
``EXPOSED_PGPORT=5433 make docker-tests``


Local tests:
------------
For local tests without the complete docker composition you need a running DB.
You can create one based on the oereb image:
``docker-compose up -d oereb-db``

or create an empty postgis DB
``docker run -p 5555:5432 --name pg_oereb --rm -it -e POSTGRES_PASSWORD=pw postgis/postgis``

Then you can run the tests easily:
``make tests``

If the DB does not use standard credentials, you can set them as ENV vars:
``PGPORT=5555 PGPASSWORD=pw make tests``

To run one specfic test:

.. code-block:: bash

  docker-compose exec oereb-server PYTEST_OPTS="-k <name_of_the_test>" make tests

Troubleshooting
---------------
Some local files may remain from previous builds, and the regular user may not be able to delete them.
In this case cleanup can be done like:

.. code-block:: bash
  docker-compose run --rm oereb-make clean-all



Useful ``make`` targets
=======================

Run the ``make`` targets found in the Makefile either in the ``oereb-server`` container (if using ``docker-compose``) or in your local shell (if running the server locally).
Some useful targets:

- ``make serve-dev`` to run the application
- ``make tests`` to run the application tests
- ``make docker-tests`` to run the application tests inside a docker composition, so one does not have to care about local set up
- ``make clean`` to empty the database
- ``make clean-all`` to empty the database, uninstall the application and the virtual env and clear the rendered configuration files
- ``make docker-clean-all`` to clean up everything written by the docker container. This is sometimes useful when docker has created some files with root only permission

If necessary the application is re-installed and the database is filled when running ``make serve-dev`` again.


Using MapFish-Print
===================

To be able to test the OEREB static extract (pdf), you need to run ``pyramid_oereb`` with ``docker-compose`` and to have a running instance of `pyramid_oereb_mfp <https://github.com/openoereb/pyramid_oereb_mfp>`__.
The Docker network ``print-network`` is also required and can be created with:

.. code-block:: bash

  docker network create print-network

It is also possible to launch a mapfish print service on a local URL (via docker or not) and then run the server via `make serve`. The correct print url must be provided:
```
PRINT_URL="http://localhost:8680/print/oereb" EXPOSED_PGPORT=5433 PGPORT=5433 make serve-dev
```

The sample static extract should then be available at http://localhost:6543/oereb/extract/pdf?EGRID=CH113928077734


CI Status
=========

CI status on master branch:

.. image:: https://github.com/openoereb/pyramid_oereb/actions/workflows/ci.yaml/badge.svg
   :alt: Master CI status
   :target: https://github.com/openoereb/pyramid_oereb/actions/workflows/ci.yaml

Daily check status:

.. image:: https://github.com/openoereb/pyramid_oereb/actions/workflows/daily_check.yaml/badge.svg
   :alt: Daily check status
   :target: https://github.com/openoereb/pyramid_oereb/actions/workflows/daily_check.yaml

Code Quality Status:

.. image:: https://api.codacy.com/project/badge/Grade/cf50094a4e84434d837babf1106f9fcb
   :alt: Codacy Badge
   :target: https://app.codacy.com/gh/openoereb/pyramid_oereb?utm_source=github.com&utm_medium=referral&utm_content=openoereb/pyramid_oereb&utm_campaign=Badge_Grade_Settings

Requirement status:

.. image:: https://requires.io/github/openoereb/pyramid_oereb/requirements.svg?branch=master
   :target: https://requires.io/github/openoereb/pyramid_oereb/requirements/?branch=master
   :alt: Requirements Status
